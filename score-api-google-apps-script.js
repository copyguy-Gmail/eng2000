const SCORE_FILE_NAME = "eng2000-scores.json";

function doGet() {
  return jsonResponse(readScoreFile());
}

function doPost(event) {
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);

  try {
    const payload = JSON.parse((event.postData && event.postData.contents) || "{}");
    const data = readScoreFile();

    if (payload.action === "saveScore" && payload.player) {
      const incoming = normalizePlayer(payload.player);
      if (incoming) {
        const existingIndex = data.players.findIndex((player) => player.name === incoming.name);

        if (existingIndex === -1) {
          data.players.push(incoming);
        } else {
          const existing = normalizePlayer(data.players[existingIndex]) || incoming;
          data.players[existingIndex] = {
            ...existing,
            ...incoming,
            score: Math.max(existing.score, incoming.score),
            updatedAt: Math.max(existing.updatedAt, incoming.updatedAt),
            history: [...(existing.history || []), ...(incoming.history || [])].slice(-50)
          };
        }
      }
    }

    data.players = normalizePlayers(data.players)
      .sort((a, b) => (b.score - a.score) || (b.updatedAt - a.updatedAt));
    writeScoreFile(data);
    return jsonResponse(data);
  } finally {
    lock.releaseLock();
  }
}

function readScoreFile() {
  const file = getScoreFile();
  const text = file.getBlob().getDataAsString("UTF-8");

  try {
    const data = text ? JSON.parse(text) : {};
    return { players: normalizePlayers(data.players || []) };
  } catch (error) {
    return { players: [] };
  }
}

function writeScoreFile(data) {
  getScoreFile().setContent(JSON.stringify({
    players: normalizePlayers(data.players || []),
    updatedAt: new Date().toISOString()
  }, null, 2));
}

function getScoreFile() {
  const files = DriveApp.getFilesByName(SCORE_FILE_NAME);
  if (files.hasNext()) return files.next();
  return DriveApp.createFile(SCORE_FILE_NAME, JSON.stringify({ players: [] }, null, 2), MimeType.PLAIN_TEXT);
}

function normalizePlayers(players) {
  return Array.isArray(players)
    ? players.map(normalizePlayer).filter(Boolean)
    : [];
}

function normalizePlayer(player) {
  if (!player || typeof player !== "object") return null;
  const name = String(player.name || "").trim();
  if (!name) return null;

  return {
    name,
    score: Number.isFinite(Number(player.score)) ? Number(player.score) : 0,
    updatedAt: Number.isFinite(Number(player.updatedAt)) ? Number(player.updatedAt) : Date.now(),
    history: Array.isArray(player.history) ? player.history.slice(-50) : []
  };
}

function jsonResponse(data) {
  return ContentService
    .createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}
