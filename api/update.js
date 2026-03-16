// api/update.js
import { fetch_all } from '../../main.js';

export default async function handler(req, res) {
  try {
    const data = await fetch_all();
    res.setHeader("Content-Type", "application/json");
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.status(200).json(data);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
}