const gameColors = {
  原神: "#4CAF50",
  鐵道: "#3F51B5",
  鳴潮: "#E91E63",
  異環: "#7B1FA2"
};

let selectedGames = new Set(["原神", "鐵道", "鳴潮", "異環"]);

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

    // 渲染日曆事件
    renderEvents(events);

    // 判定登入按鈕與導出按鈕狀態
    const exportBtn = document.getElementById("exportBtn");
    const loginBtn = document.getElementById("loginBtn");
    if (loginBtn && exportBtn) {
      exportBtn.disabled = loginBtn.textContent === "登入 Google 帳號";
    }

    loadingScreen.style.display = "none";
    updateBtn.disabled = false;
    updateBtn.textContent = "🔄 更新資料";

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

  // 先讀本地快取
  // 1. 先讀取本地快取
  const saved = localStorage.getItem("calendarEvents");
  if (saved) {
    renderEvents(JSON.parse(saved));

    // 🎯 重點：既然本地有快取，日曆已經畫好了，立刻拉開序幕！使用者體感延遲直接歸零！
    dismissInitOverlay();
  }

  // 2. 隨後默默在背景抓取最新資料，更新 localStorage 並重繪日曆
  loadCalendarData("/api/update");

  // 抓取最新資料
  loadCalendarData("/api/update");

  // 更新按鈕事件
  updateBtn.addEventListener("click", () => loadCalendarData("/api/update"));

  // 遊戲過濾器事件
  document.querySelectorAll("#gameFilter input").forEach((checkbox) => {
    checkbox.addEventListener("change", () => {
      selectedGames.clear();

      document.querySelectorAll("#gameFilter input:checked")
        .forEach(cb => selectedGames.add(cb.value));

      const events = JSON.parse(
        localStorage.getItem("calendarEvents") || "[]"
      );

      renderEvents(events);

      localStorage.setItem(
        "selectedGames",
        JSON.stringify([...selectedGames])
      );
    });
  });
});