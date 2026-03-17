let tokenClient;
const CLIENT_ID =
  "421221289192-qtf3spuf5bqgd8m4ss201kstc9vqtqf8.apps.googleusercontent.com";
const SCOPES = "https://www.googleapis.com/auth/calendar.events";

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
    callback: (response) => {
      if (response.error !== undefined) {
        console.error("登入失敗", response);
        return;
      }
      console.log("登入並獲取 Token 成功");

      const btn = document.getElementById("loginBtn");
      btn.textContent = user.getBasicProfile().getEmail();
      btn.disabled = true;
      btn.classList.add("active");
    },
  });
};

// 使用新的 Token Client
window.signIn = function () {
  tokenClient.requestAccessToken({ prompt: "consent" });
};

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
