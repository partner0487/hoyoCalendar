let tokenClient;
let isExported = false; // 是否已導出

// 確保在呼叫此變數時才動態取得元素，避免頂部全域宣告拿不到 DOM 的問題
function getExportBtn() {
  return document.getElementById("exportBtn");
}

const CLIENT_ID = "421221289192-qtf3spuf5bqgd8m4ss201kstc9vqtqf8.apps.googleusercontent.com";
const SCOPES = "https://www.googleapis.com/auth/calendar.events https://www.googleapis.com/auth/userinfo.email";

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// 初始化 Google APIs
window.handleClientLoad = function () {
  gapi.load("client", async () => {
    try {
      await gapi.client.init({
        discoveryDocs: ["https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest"],
      });
      console.log("✅ GAPI client loaded successfully");
    } catch (err) {
      console.error("❌ GAPI client init failed:", err);
    }
  });

  if (typeof google !== "undefined" && google.accounts && google.accounts.oauth2) {
    tokenClient = google.accounts.oauth2.initTokenClient({
      client_id: CLIENT_ID,
      scope: SCOPES,
      callback: async (response) => {
        if (response.error !== undefined) return;

        gapi.client.setToken(response);

        const userInfo = await fetch("https://www.googleapis.com/oauth2/v3/userinfo", {
          headers: { Authorization: `Bearer ${response.access_token}` },
        }).then((res) => res.json());

        const loginBtn = document.getElementById("loginBtn");
        if (loginBtn) {
          loginBtn.textContent = userInfo.email.split("@")[0];
          loginBtn.disabled = true;
          loginBtn.classList.add("active");
        }
        
        updateExportBtnUI();
      },
    });
    console.log("✅ GIS tokenClient initialized");
  } else {
    console.error("❌ Google Accounts Identity Service (GIS) script has not loaded yet.");
  }
};

window.signIn = function () {
  if (tokenClient) {
    tokenClient.requestAccessToken({ prompt: "consent" });
  } else {
    alert("Google 登入套件載入中，請稍候再試！");
    // 嘗試重新初始化
    window.handleClientLoad();
  }
};

function updateExportBtnUI() {
  const exportBtn = getExportBtn();
  if (!exportBtn) return;
  
  const hasToken = !!gapi.client.getToken();
  exportBtn.disabled = !hasToken; // 未登入時停用

  if (isExported) {
    exportBtn.textContent = "🗑️ 刪除 Google 日曆所有事件";
    exportBtn.classList.add("delete-mode");
  } else {
    exportBtn.textContent = "📤 導出到 Google 日曆";
    exportBtn.classList.remove("delete-mode");
  }
}

async function exportAllEvents() {
  if (!gapi.client.getToken()) {
    alert("請先登入 Google 帳號！");
    window.signIn();
    return false;
  }

  // 1. 撈出所有爬下來的事件
  const allEvents = JSON.parse(localStorage.getItem("calendarEvents") || "[]");

  const savedSelectedGames = JSON.parse(
    localStorage.getItem("selectedGames") || '["原神", "鐵道", "鳴潮", "異環"]'
  );
  const selectedGamesSet = new Set(savedSelectedGames);

  // 透過 filter 篩選出只有存在於 selectedGames 中的事件
  const eventsToExport = allEvents.filter((e) => selectedGamesSet.has(e.game));
  // ───────────────────────────────────────────────────

  if (eventsToExport.length === 0) {
    alert("目前選擇的遊戲中沒有任何事件可以導出。");
    return false;
  }

  const exportBtn = getExportBtn();
  if (exportBtn) {
    exportBtn.disabled = true;
    exportBtn.textContent = "⏳ 導出中 (請勿關閉視窗)...";
  }

  console.log(`準備導出 ${eventsToExport.length} 個事件... (已排除未勾選遊戲)`);
  let successCount = 0;

  try {
    for (const e of eventsToExport) {
      try {
        await addEventToGoogleCalendar(e);
        console.log(`✅ 成功導出: [${e.game}] ${e.title}`);
        successCount++;
      } catch (err) {
        console.error(`❌ 導出失敗: ${e.title}`, err);
      }
      await sleep(500); 
    }

    alert(`導出程序已完成！成功匯出 ${successCount}/${eventsToExport.length} 個事件。`);
    return successCount > 0;
  } catch (error) {
    alert("導出時發生錯誤，請查看主控台。");
    return false;
  } finally {
    updateExportBtnUI();
  }
}

async function deleteAllEvents() {
  if (!gapi.client.getToken()) {
    alert("請先登入 Google 帳號！");
    return false;
  }

  if (!confirm("確定要刪除所有由本網站建立的事件嗎？")) return false;

  const exportBtn = getExportBtn();
  if (exportBtn) {
    exportBtn.disabled = true;
    exportBtn.textContent = "⏳ 刪除中 (請勿關閉視窗)...";
  }

  try {
    const res = await gapi.client.calendar.events.list({
      calendarId: "primary",
      q: "由 Hoyo-Calendar 自動產生", 
    });

    const events = res.result.items || [];
    console.log(`找到 ${events.length} 個事件準備刪除`);

    if (events.length === 0) {
      alert("日曆中沒有找到本網站建立的事件。");
      return true;
    }

    for (const e of events) {
      try {
        await gapi.client.calendar.events.delete({
          calendarId: "primary",
          eventId: e.id,
        });
        console.log(`🗑️ 已刪除: ${e.summary}`);
      } catch (err) {
        console.error("刪除失敗", err);
      }
      await sleep(300); 
    }

    alert("所有相關事件已從 Google 日曆刪除！");
    return true;
  } catch (error) {
    console.error("刪除程序發生錯誤:", error);
    alert("刪除時發生錯誤，請查看主控台。");
    return false;
  } finally {
    updateExportBtnUI();
  }
}

const gameToColorId = {
  原神: "2", // 鼠尾草綠
  鐵道: "7", // 孔雀藍
  鳴潮: "4", // 火鶴粉
  異環: "3", // 孔雀紫
};

async function addEventToGoogleCalendar(event) {
  const startDate = event.dates;
  const endDate = new Date(startDate);
  endDate.setDate(endDate.getDate() + 1);

  const colorId = gameToColorId[event.game];

  const listRes = await gapi.client.calendar.events.list({
    calendarId: "primary",
    timeMin: new Date(startDate).toISOString(),
    timeMax: new Date(endDate).toISOString(),
    singleEvents: true,
    q: `${event.game} ${event.title}`, 
  });

  const resourceData = {
    summary: `${event.game} ${event.title}`,
    description: "由 Hoyo-Calendar 自動產生",
    start: { date: startDate },
    end: { date: endDate.toISOString().split("T")[0] },
    ...(colorId && { colorId: colorId }),
  };

  if (listRes.result.items && listRes.result.items.length > 0) {
    const existingEvent = listRes.result.items[0];
    return gapi.client.calendar.events.update({
      calendarId: "primary",
      eventId: existingEvent.id,
      resource: resourceData,
    });
  } else {
    return gapi.client.calendar.events.insert({
      calendarId: "primary",
      resource: resourceData,
    });
  }
}

// ─── 💡 整合的事件綁定 ───
document.addEventListener("DOMContentLoaded", () => {
  const exportBtn = getExportBtn();
  if (exportBtn) {
    exportBtn.addEventListener("click", async () => {
      if (!isExported) {
        const success = await exportAllEvents();
        if (success) {
          isExported = true;
          updateExportBtnUI();
        }
      } else {
        const success = await deleteAllEvents();
        if (success) {
          isExported = false;
          updateExportBtnUI();
        }
      }
    });
  }

  const loginBtn = document.getElementById("loginBtn");
  if (loginBtn) {
    loginBtn.addEventListener("click", () => {
      window.signIn();
    });
  }
});

// 當 Google 官方 JS 檔案非同步載入完成後，由系統或手動觸發初始化
window.addEventListener("load", () => {
  // 給予 Google API 載入的極短緩衝時間
  setTimeout(() => {
    window.handleClientLoad();
  }, 100);
});