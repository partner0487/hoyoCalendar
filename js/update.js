const gameColors = {
  原神: "#4CAF50",
  鐵道: "#3F51B5",
  鳴潮: "#E91E63",
};

document.addEventListener("DOMContentLoaded", () => {
  const calendarEl = document.getElementById("calendar");

  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",
    locale: "zh-tw",
    events: [],
  });

  calendar.render();

  async function loadCalendarData(url) {
    const btn = document.getElementById("updateBtn");
    btn.disabled = true;
    btn.textContent = "更新中...";

    let events = [];

    try {
      const res = await fetch(url);
      events = await res.json();

      // 存入 localStorage
      localStorage.setItem("calendarEvents", JSON.stringify(events));
    } catch (e) {
      console.error("抓取失敗，使用本地資料 fallback:", e);

      const fallback = localStorage.getItem("calendarEvents");
      if (fallback) {
        events = JSON.parse(fallback);
      } else {
        console.warn("本地也沒有資料可用");
      }
    }

    calendar.removeAllEvents();

    events.forEach((e) => {
      calendar.addEvent({
        title: `${e.game} ${e.title}`,
        start: e.dates,
        color: gameColors[e.game] || "#2196F3",
      });
    });

    btn.disabled = false;
    btn.textContent = "🔄 更新資料";
  }

  // 頁面載入時先嘗試讀 localStorage
  const saved = localStorage.getItem("calendarEvents");
  if (saved) {
    const events = JSON.parse(saved);
    events.forEach((e) => {
      calendar.addEvent({
        title: `${e.game} ${e.title}`,
        start: e.dates,
        color: gameColors[e.game] || "#2196F3",
      });
    });
  }

  // 再去抓最新資料更新 localStorage
  loadCalendarData("/api/update");

  // 更新按鈕
  document
    .getElementById("updateBtn")
    .addEventListener("click", () => loadCalendarData("/api/update"));
});
