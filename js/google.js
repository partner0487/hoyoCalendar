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
// 定義延遲工具
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

document.getElementById("exportBtn").addEventListener("click", async () => {
  // 檢查是否登入
  if (!gapi.client.getToken()) {
    alert("請先登入 Google 帳號！");
    window.signIn();
    return;
  }

  // 取得資料來源 (請確保變數名稱正確，假設你的資料叫 allEvents)
  if (typeof allEvents === "undefined" || allEvents.length === 0) {
    alert("沒有可導出的事件！");
    return;
  }

  const btn = document.getElementById("exportBtn");
  btn.disabled = true;
  const originalText = btn.textContent;
  btn.textContent = "正在同步至日曆...";

  try {
    for (const event of allEvents) {
      try {
        // 等待 Google 回傳成功
        await addEventToGoogleCalendar(event);
        console.log(`✅ 成功新增: ${event.title}`);
      } catch (err) {
        // 如果單一事件失敗（例如又是 403），會記錄在這裡
        console.error(`❌ 新增失敗: ${event.title}`, err);
      }

      // *** 重點：每新增一個就強迫休息 500 毫秒，避免被 Google 封鎖 ***
      await sleep(500);
    }
    alert("導出程序完成！請至 Google 日曆查看。");
  } catch (globalErr) {
    console.error("發生非預期錯誤:", globalErr);
  } finally {
    btn.disabled = false;
    btn.textContent = originalText;
  }
});

const gameToColorId = {
  原神: "2", // 鼠尾草綠
  鐵道: "7", // 孔雀藍
  鳴潮: "4", // 火鶴粉
};

function addEventToGoogleCalendar(event) {
  const startDate = new Date(event.dates);
  const endDate = new Date(startDate);
  endDate.setDate(startDate.getDate() + 1);
  const colorId = gameToColorId[event.game];

  const gEvent = {
    summary: `${event.game} ${event.title}`,
    description: "由 Hoyo-Calendar 自動產生",
    start: { date: event.dates },
    end: { date: endDate.toISOString().split("T")[0] },
    ...(colorId && { colorId: colorId }),
  };

  return gapi.client.calendar.events.insert({
    calendarId: "primary",
    resource: gEvent,
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const exportBtn = document.getElementById("exportBtn");
  if (exportBtn) {
    exportBtn.addEventListener("click", exportAllEvents);
    console.log("導出按鈕監聽器已綁定");
  }
});
