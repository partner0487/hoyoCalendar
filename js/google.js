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

function exportAllEvents() {
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

  eventsToExport.forEach((e) => addEventToGoogleCalendar(e));
  alert("導出程序已開始，請稍後。");
}

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
    ...(colorId && { colorId: colorId })
  };

  gapi.client.calendar.events
    .insert({
      calendarId: "primary",
      resource: gEvent,
    })
    .then((res) => console.log(`成功新增事件: ${event.title}`, res))
    .catch((err) => console.error(`新增失敗: ${event.title}`, err));
}

document.addEventListener("DOMContentLoaded", () => {
  const exportBtn = document.getElementById("exportBtn");
  if (exportBtn) {
    exportBtn.addEventListener("click", exportAllEvents);
    console.log("導出按鈕監聽器已綁定");
  }
});
