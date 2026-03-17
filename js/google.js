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

window.signIn = function () {
  if (gapi.client.getToken() === null) {
    tokenClient.requestAccessToken({ prompt: "consent" });
  } else {
    tokenClient.requestAccessToken({ prompt: "" });
  }
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
