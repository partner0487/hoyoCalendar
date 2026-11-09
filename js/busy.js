// loading.js 與 google.js 共用的忙碌狀態：
// 載入資料或導出／刪除 Google 日曆期間都不能按「更新資料」，
// 兩者都結束才重新啟用，避免其中一方先結束時把按鈕提早打開。
export const busy = { loading: false, exporting: false };

export function refreshUpdateBtn() {
  const btn = document.getElementById("updateBtn");
  if (btn) btn.disabled = busy.loading || busy.exporting;
}
