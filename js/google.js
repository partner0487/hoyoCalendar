let tokenClient;
const CLIENT_ID =
  "421221289192-qtf3spuf5bqgd8m4ss201kstc9vqtqf8.apps.googleusercontent.com";
const SCOPES =
  "https://www.googleapis.com/auth/calendar.events https://www.googleapis.com/auth/userinfo.email";

window.handleClientLoad = function () {
  gapi.load("client", async () => {
    await gapi.client.init({
      discoveryDocs: [
        "https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest",
      ],
    });
    console.log("GAPI client loaded");
  });

  tokenClient = google.accounts.oauth2.initTokenClient({
    client_id: CLIENT_ID,
    scope: SCOPES,
    callback: async (response) => {
      if (response.error !== undefined) return;

      gapi.client.setToken(response);

      const userInfo = await fetch(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        {
          headers: { Authorization: `Bearer ${response.access_token}` },
        },
      ).then((res) => res.json());

      const btn = document.getElementById("loginBtn");
      btn.textContent = userInfo.email.split("@")[0];
      btn.disabled = true;
      btn.classList.add("active");
    },
  });
};

window.signIn = function () {
  tokenClient.requestAccessToken({ prompt: "consent" });
};
// 定義延遲工具函數 (如果還沒加的話)
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function exportAllEvents() {
  if (!gapi.client.getToken()) {
    alert("請先登入 Google 帳號！");
    window.signIn();
    return;
  }

  const eventsToExport = JSON.parse(
    localStorage.getItem("calendarEvents") || "[]",
  );

  if (eventsToExport.length === 0) {
    alert("目前沒有任何事件可以導出。");
    return;
  }

  const btn = document.getElementById("exportBtn");
  const originalText = btn.textContent;
  btn.disabled = true;
  btn.textContent = "導出中 (請勿關閉視窗)...";

  console.log(`準備導出 ${eventsToExport.length} 個事件...`);

  try {
    for (const e of eventsToExport) {
      try {
        await addEventToGoogleCalendar(e);
        console.log(`✅ 成功導出: ${e.title}`);
      } catch (err) {
        console.error(`❌ 導出失敗: ${e.title}`, err);
      }

      await sleep(500);
    }

    alert("導出程序已完成！");
  } catch (error) {
    console.error("導出過程發生嚴重錯誤:", error);
    alert("導出時發生錯誤，請查看主控台。");
  } finally {
    btn.disabled = false;
    btn.textContent = originalText;
  }
}

const gameToColorId = {
  原神: "2", // 鼠尾草綠
  鐵道: "7", // 孔雀藍
  鳴潮: "4", // 火鶴粉
};
async function addEventToGoogleCalendar(event) {
  const startDate = event.dates;
  const endDate = new Date(startDate);
  endDate.setDate(endDate.getDate() + 1);

  const colorId = gameToColorId[event.game];

  // 先查詢當天所有事件
  const listRes = await gapi.client.calendar.events.list({
    calendarId: "primary",
    timeMin: new Date(startDate).toISOString(),
    timeMax: new Date(endDate).toISOString(),
    singleEvents: true,
    q: `${event.game} ${event.title}`, // 搜尋標題
  });

  if (listRes.result.items && listRes.result.items.length > 0) {
    // 已存在 → 更新
    const existingEvent = listRes.result.items[0];
    return gapi.client.calendar.events.update({
      calendarId: "primary",
      eventId: existingEvent.id,
      resource: {
        summary: `${event.game} ${event.title}`,
        description: "由 Hoyo-Calendar 自動產生",
        start: { date: startDate },
        end: { date: endDate.toISOString().split("T")[0] },
        ...(colorId && { colorId: colorId }),
      },
    });
  } else {
    // 不存在 → 新增
    return gapi.client.calendar.events.insert({
      calendarId: "primary",
      resource: {
        summary: `${event.game} ${event.title}`,
        description: "由 Hoyo-Calendar 自動產生",
        start: { date: startDate },
        end: { date: endDate.toISOString().split("T")[0] },
        ...(colorId && { colorId: colorId }),
      },
    });
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const exportBtn = document.getElementById("exportBtn");
  if (exportBtn) {
    exportBtn.addEventListener("click", exportAllEvents);
    console.log("導出按鈕監聽器已綁定");
  }
});
