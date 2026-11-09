const gameColors = {
  原神: "#4CAF50",
  鐵道: "#3F51B5",
  鳴潮: "#E91E63",
  異環: "#7B1FA2"
};

let selectedGames = new Set(["原神", "鐵道", "鳴潮", "異環"]);

// 讀取快取的事件；舊版可能存過 API 的錯誤物件，不是陣列就當作沒有快取
function loadCachedEvents() {
  try {
    const data = JSON.parse(localStorage.getItem("calendarEvents") || "[]");
    return Array.isArray(data) ? data : [];
  } catch {
    return [];
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const calendarEl = document.getElementById("calendar");
  const loadingScreen = document.getElementById("loadingScreen");
  const updateBtn = document.getElementById("updateBtn");

  const savedGames = JSON.parse(
    localStorage.getItem("selectedGames") || '["原神","鐵道","鳴潮", "異環"]'
  );

  selectedGames = new Set(savedGames);

  document.querySelectorAll("#gameFilter input").forEach((cb) => {
    cb.checked = selectedGames.has(cb.value);
  });

  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",
    locale: "zh-tw",
    events: [],
    eventMouseEnter: function (info) {
      const imgUrl = info.event.extendedProps.image;
      if (!imgUrl) return;

      // 1. 建立 Tooltip 容器
      const tooltip = document.createElement("div");
      tooltip.id = "imgTooltip";
      tooltip.style.position = "fixed"; // 相對於視窗定位
      tooltip.style.zIndex = "9999";
      tooltip.style.pointerEvents = "none"; // 避免遮擋滑鼠點擊

      const imgNode = document.createElement("img");
      imgNode.src = imgUrl; // 即使 imgUrl 含有惡意代碼，也會被瀏覽器當成純字串處理
      imgNode.style.width = "300px";
      imgNode.style.borderRadius = "10px";
      imgNode.style.boxShadow = "0 0 10px rgba(0,0,0,0.5)";

      tooltip.appendChild(imgNode);
      document.body.appendChild(tooltip);

      function move(e) {
        let left = e.clientX + 15;
        let top = e.clientY + 15;

        // ─── 💡 邊界防禦：如果圖片會衝出右側螢幕，改顯示在滑鼠左邊 ───
        const tooltipWidth = 320; // 圖片寬 300px + 留白 20px
        if (left + tooltipWidth > window.innerWidth) {
          left = e.clientX - tooltipWidth - 15; // 移到滑鼠左邊
        }
        // ────────────────────────────────────────────────────────

        tooltip.style.left = left + "px";
        tooltip.style.top = top + "px";
      }

      // 初始化位置
      move(info.jsEvent);

      // 監聽並將 move 函式綁定在元件上，以便移出時精準卸載
      document.addEventListener("mousemove", move);
      info.el._moveHandler = move;
    },

    eventMouseLeave: function (info) {
      const tooltip = document.getElementById("imgTooltip");
      if (tooltip) tooltip.remove();

      if (info.el._moveHandler) {
        document.removeEventListener("mousemove", info.el._moveHandler);
        delete info.el._moveHandler; // 清理物件屬性
      }
    },
  });

  calendar.render();

  function renderEvents(events) {
    calendar.removeAllEvents();

    events
      .filter((e) => selectedGames.has(e.game))
      .forEach((e) => {
        calendar.addEvent({
          title: `${e.game} ${e.title}`,
          start: e.dates,
          color: gameColors[e.game] || "#2196F3",
          extendedProps: {
            image: e.image,
          },
        });
      });
  }

  // 只改按鈕裡的文字 span，保留 SVG 圖示
  const updateText = document.getElementById("updateText");

  async function loadCalendarData(url) {
    loadingScreen.style.display = "inline-block";
    updateBtn.disabled = true;
    updateText.textContent = "更新中...";

    let events = [];

    try {
      const res = await fetch(url);
      const data = await res.json();
      // API 出錯時回傳的是 {"error": ...}，不能拿來覆蓋快取
      if (!res.ok || !Array.isArray(data)) {
        throw new Error(data && data.error ? data.error : `HTTP ${res.status}`);
      }
      events = data;
      localStorage.setItem("calendarEvents", JSON.stringify(events));
    } catch (e) {
      console.error("抓取失敗，使用本地資料 fallback:", e);
      events = loadCachedEvents();
    } finally {
      loadingScreen.style.display = "none";
      updateBtn.disabled = false;
      updateText.textContent = "更新資料";
    }

    // 渲染日曆事件（導出按鈕的啟用狀態由 google.js 依登入狀態控制）
    renderEvents(events);

    // ─── 💡 核心新增：優雅解鎖序幕遮罩 ───
    const initOverlay = document.getElementById("initOverlay");
    if (initOverlay) {
      setTimeout(() => {
        // 往上滑動並淡出，營造極佳的拉開序幕效果
        initOverlay.style.transform = "translateY(-100%)";
        initOverlay.style.opacity = "0";

        // 動畫結束後完全拔除 DOM，釋放記憶體且不影響任何點擊
        setTimeout(() => {
          initOverlay.remove();
        }, 600); // 600ms 對應 transition 的 0.6s
      }, 200); // 給日曆 200 毫秒完成最後的排版快照
    }
  }

  function dismissInitOverlay() {
    const initOverlay = document.getElementById("initOverlay");
    if (initOverlay) {
      // 往上滑動並淡出
      initOverlay.style.transform = "translateY(-100%)";
      initOverlay.style.opacity = "0";

      // 動畫結束後完全拔除 DOM
      setTimeout(() => {
        initOverlay.remove();
      }, 600); // 600ms 對應 transition 的 0.6s
    }
  }

  // 1. 先讀取本地快取
  const saved = loadCachedEvents();
  if (saved.length) {
    renderEvents(saved);

    // 🎯 重點：既然本地有快取，日曆已經畫好了，立刻拉開序幕！使用者體感延遲直接歸零！
    dismissInitOverlay();
  }

  // 2. 隨後在背景抓取最新資料，更新 localStorage 並重繪日曆
  loadCalendarData("/api/update");

  // 更新按鈕事件
  updateBtn.addEventListener("click", () => loadCalendarData("/api/update"));

  // 遊戲過濾器事件
  document.querySelectorAll("#gameFilter input").forEach((checkbox) => {
    checkbox.addEventListener("change", () => {
      selectedGames.clear();

      document.querySelectorAll("#gameFilter input:checked")
        .forEach(cb => selectedGames.add(cb.value));

      renderEvents(loadCachedEvents());

      localStorage.setItem(
        "selectedGames",
        JSON.stringify([...selectedGames])
      );
    });
  });
});