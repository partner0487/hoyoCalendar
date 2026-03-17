export {}; // 保留 module

const CLIENT_ID =
  "421221289192-qtf3spuf5bqgd8m4ss201kstc9vqtqf8.apps.googleusercontent.com";
const SCOPES = "https://www.googleapis.com/auth/calendar.events";

window.handleClientLoad = function () {
  gapi.load("client:auth2", initClient);
};

function initClient() {
  gapi.client
    .init({
      clientId: CLIENT_ID,
      scope: SCOPES,
      discoveryDocs: [
        "https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest",
      ],
    })
    .then(() => console.log("Google API initialized"));
}

window.signIn = function () {
  gapi.auth2
    .getAuthInstance()
    .signIn()
    .then(() => console.log("已登入 Google 帳號"));
};

function addEventToGoogleCalendar(event) {
  const gEvent = {
    summary: `${event.game} ${event.title}`,
    start: { date: event.dates }, // 全日事件
    end: { date: event.dates }, // 同一天會被視作一天結束，建議加一天：
  };

  gapi.client.calendar.events
    .insert({
      calendarId: "primary",
      resource: gEvent,
    })
    .then(
      (response) => {
        console.log("事件已新增到 Google Calendar", response);
      },
      (err) => {
        console.error("新增失敗", err);
      },
    );
}

// 全部導出
function exportAllEvents(events) {
  events.forEach((e) => addEventToGoogleCalendar(e));
}

document.getElementById("exportBtn").addEventListener("click", () => {
  exportAllEvents(events); // events 來源：你的 localStorage 或 API
});
