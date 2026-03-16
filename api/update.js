// api/update.js
import fs from "fs";
import path from "path";
import { fetch_all } from "../../main.js"; // 你的 fetch_all 函數

export default async function handler(req, res) {
  try {
    let data = await fetch_all(); // 嘗試抓最新資料
    res.setHeader("Content-Type", "application/json");
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.status(200).json(data);
  } catch (e) {
    console.error("fetch_all 失敗，使用 fallback:", e);

    // fallback 到本地 events.json
    try {
      const filePath = path.join(process.cwd(), "public", "events.json");
      const fileData = fs.readFileSync(filePath, "utf-8");
      const fallbackData = JSON.parse(fileData);

      res.setHeader("Content-Type", "application/json");
      res.setHeader("Access-Control-Allow-Origin", "*");
      res.status(200).json(fallbackData);
    } catch (fileErr) {
      console.error("讀取 fallback 也失敗:", fileErr);
      res.status(500).json({ error: "更新與 fallback 都失敗" });
    }
  }
}