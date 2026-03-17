let tokenClient;
const CLIENT_ID =
  "421221289192-qtf3spuf5bqgd8m4ss201kstc9vqtqf8.apps.googleusercontent.com";
const SCOPES = "https://www.googleapis.com/auth/calendar.events";

window.handleClientLoad = function () {
  gapi.load("client", async () => {
    // 初始化日曆 API
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
    callback: (response) => {
      if (response.error !== undefined) {
        throw response;
      }
      console.log("登入並獲取 Token 成功");
    },
  });
};

function signIn() {
  gapi.auth2
    .getAuthInstance()
    .signIn()
    .then(
      (user) => {
        console.log("已登入 Google 帳號", user.getBasicProfile().getEmail());

        // 修改按鈕文字
        const btn = document.getElementById("loginBtn");
        btn.textContent = user.getBasicProfile().getEmail();
        btn.disabled = true; // 如果想要禁止再次點擊
      },
      (err) => {
        console.error("登入失敗", err);
        alert("登入失敗，請重試");
      },
    );
}

function addEventToGoogleCalendar(event) {
  const gEvent = {
    summary: `${event.game} ${event.title}`,
    start: { date: event.dates },
    end: { date: event.dates },
  };

  gapi.client.calendar.events
    .insert({
      calendarId: "primary",
      resource: gEvent,
    })
    .then((res) => console.log("新增成功", res))
    .catch((err) => console.error("新增失敗", err));
}
