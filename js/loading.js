const gameColors = {
  原神: "#4CAF50",
  鐵道: "#3F51B5",
  鳴潮: "#E91E63",
};

document.addEventListener("DOMContentLoaded", () => {
  const calendarEl = document.getElementById("calendar");
  const loadingScreen = document.getElementById("loadingScreen");
  const updateBtn = document.getElementById("updateBtn");

  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",
    locale: "zh-tw",
    events: [],
    eventMouseEnter: function(info) {
      const img = info.event.extendedProps.image;
      if (!img) return;

      const tooltip = document.createElement("div");
      tooltip.id = "imgTooltip";
      tooltip.style.position = "fixed";
      tooltip.style.zIndex = "9999";
      tooltip.style.pointerEvents = "none";
      tooltip.innerHTML = `
        <img src="${img}" style="
          width: 300px;
          border-radius: 10px;
          box-shadow: 0 0 10px rgba(0,0,0,0.5);
        ">
      `;
      document.body.appendChild(tooltip);

      function move(e) {
        tooltip.style.left = e.pageX + 15 + "px";
        tooltip.style.top = e.pageY + 15 + "px";
      }

      document.addEventListener("mousemove", move);
      info.el._moveHandler = move;
    },
    eventMouseLeave: function(info) {
      const tooltip = document.getElementById("imgTooltip");
      if (tooltip) tooltip.remove();
      if (info.el._moveHandler) {
        document.removeEventListener("mousemove", info.el._moveHandler);
      }
    },
  });

  calendar.render();

  async function loadCalendarData(url) {
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

    calendar.removeAllEvents();
    events.forEach((e) => {
      calendar.addEvent({
        title: `${e.game} ${e.title}`,
        start: e.dates,
        color: gameColors[e.game] || "#2196F3",
        extendedProps: { image: e.image }, // 存版本圖片
      });
    });

    loadingScreen.style.display = "none";
    updateBtn.disabled = false;
    updateBtn.textContent = "🔄 更新資料";
  }

  // 先讀 localStorage
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

  // 更新按鈕
  updateBtn.addEventListener("click", () => loadCalendarData("/api/update"));
});