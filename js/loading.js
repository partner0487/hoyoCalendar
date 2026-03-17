const gameColors = {
  原神: "#4CAF50",
  鐵道: "#3F51B5",
  鳴潮: "#E91E63",
};

document.addEventListener("DOMContentLoaded", () => {
  const calendarEl = document.getElementById("calendar");
  const loadingScreen = document.getElementById("loadingScreen");
  const updateBtn = document.getElementById("updateBtn");

  // 初始化 FullCalendar
  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",
    locale: "zh-tw",
    events: [],
  });
  calendar.render();

  async function loadCalendarData(url) {
    // 顯示 loading
    loadingScreen.style.display = "inline-block";
    updateBtn.disabled = true;
    updateBtn.textContent = "更新中...";

    let events = [];

    try {
      const res = await fetch(url);
      events = await res.json();
      localStorage.setItem("calendarEvents", JSON.stringify(events));
    } catch (e) {
      console.error("抓取失敗，使用本地資料 fallback:", e);
      const fallback = localStorage.getItem("calendarEvents");
      if (fallback) events = JSON.parse(fallback);
    }

    // 清空再加事件
    calendar.removeAllEvents();
    events.forEach((e) => {
      calendar.addEvent({
        title: `${e.game} ${e.title}`,
        start: e.dates,
        color: gameColors[e.game] || "#2196F3",
        extendedProps: { image: e.image },
      });
    });

    // 隱藏 loading
    loadingScreen.style.display = "none";
    updateBtn.disabled = false;
    updateBtn.textContent = "🔄 更新資料";
  }

  // 頁面先讀 localStorage
  const saved = localStorage.getItem("calendarEvents");
  if (saved) {
    const events = JSON.parse(saved);
    events.forEach((e) => {
      calendar.addEvent({
        title: `${e.game} ${e.title}`,
        start: e.dates,
        color: gameColors[e.game] || "#2196F3",
        extendedProps: { image: e.image },
      });
    });
  }

  // 抓最新資料更新 localStorage
  loadCalendarData("/api/update");

  // 更新按鈕事件
  updateBtn.addEventListener("click", () => loadCalendarData("/api/update"));
});