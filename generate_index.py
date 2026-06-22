from __future__ import annotations

import json
import re
from pathlib import Path

from pypdf import PdfReader


WORKSPACE = Path(r"C:\Users\chungyi\Documents\LAB\codex_lab")
OUTPUT_PATH = WORKSPACE / "index.html"
PDF_PATH = Path(r"C:\Users\chungyi\Downloads\1141298285_3_376540000A_1140231689_ATTACH3.pdf")

POS_TAGS = [
    r"代名詞\(主/受格\)",
    r"代名詞\(主格\)",
    r"代名詞\(受格\)",
    r"副詞/連接詞",
    r"代名詞/限定詞",
    r"名詞/形容詞",
    r"形容詞/副詞",
    r"動詞/名詞",
    r"所有格",
    r"疑問詞",
    r"名詞",
    r"動詞",
    r"形容詞",
    r"副詞",
    r"限定詞",
    r"介系詞",
    r"連接詞",
    r"代名詞",
    r"助動詞",
    r"感嘆詞",
]

PARSE_RE = re.compile(rf"^(.*?)\s+({'|'.join(POS_TAGS)})\s*(.*)$")
START_RE = re.compile(r"^(\d+)\s+(.*)$")


def parse_column(lines: list[str]) -> list[tuple[int, str]]:
    current_id: int | None = None
    chunks: list[str] = []
    entries: list[tuple[int, str]] = []

    for raw in lines:
        line = re.sub(r"\s+", " ", raw).strip()
        if not line:
            continue
        if "國中單字王" in line or "單字、詞" in line or re.fullmatch(r"\d+", line):
            continue

        match = START_RE.match(line)
        if match:
            item_id = int(match.group(1))
            if current_id is not None:
                entries.append((current_id, " ".join(chunks)))
            current_id = item_id
            chunks = [match.group(2).strip()]
            continue

        if current_id is not None:
            chunks.append(line)

    if current_id is not None:
        entries.append((current_id, " ".join(chunks)))

    return entries


def load_vocab() -> list[dict[str, object]]:
    reader = PdfReader(str(PDF_PATH))
    parsed: dict[int, dict[str, object]] = {}

    for page in reader.pages:
        text = page.extract_text(extraction_mode="layout") or ""
        lines = text.splitlines()
        columns = ([line[:41] for line in lines], [line[41:] for line in lines])
        for column in columns:
            for item_id, content in parse_column(column):
                if not (1 <= item_id <= 2000):
                    continue
                cleaned = re.sub(r"\s+", " ", content).strip()
                match = PARSE_RE.match(cleaned)
                if not match:
                    continue
                word, pos, meaning = match.groups()
                parsed[item_id] = {
                    "id": item_id,
                    "word": word.strip(),
                    "pos": pos.strip(),
                    "meaning": meaning.replace(" ", "").strip(),
                }

    overrides = {
        974: {"id": 974, "word": "Double Tenth Day", "pos": "名詞", "meaning": "雙十節"},
        975: {"id": 975, "word": "Dragon-boat Festival", "pos": "名詞", "meaning": "端午節"},
        1188: {"id": 1188, "word": "their", "pos": "所有格", "meaning": "他們的"},
        1189: {"id": 1189, "word": "I", "pos": "代名詞(主格)", "meaning": "我"},
        1190: {"id": 1190, "word": "me", "pos": "代名詞(受格)", "meaning": "我"},
        1191: {"id": 1191, "word": "my", "pos": "所有格", "meaning": "我的"},
        1192: {"id": 1192, "word": "mine", "pos": "代名詞", "meaning": "我的"},
        1193: {"id": 1193, "word": "myself", "pos": "代名詞", "meaning": "我自己"},
        1194: {"id": 1194, "word": "you", "pos": "代名詞(主/受格)", "meaning": "你；你們"},
        1195: {"id": 1195, "word": "your", "pos": "所有格", "meaning": "你的；你們的"},
        1196: {"id": 1196, "word": "yours", "pos": "代名詞", "meaning": "你的；你們的"},
        1197: {"id": 1197, "word": "yourself", "pos": "代名詞", "meaning": "你自己"},
        1198: {"id": 1198, "word": "yourselves", "pos": "代名詞", "meaning": "你們自己"},
        1199: {"id": 1199, "word": "he", "pos": "代名詞(主格)", "meaning": "他"},
        1200: {"id": 1200, "word": "him", "pos": "代名詞(受格)", "meaning": "他"},
        1201: {"id": 1201, "word": "his", "pos": "代名詞", "meaning": "他的"},
        1202: {"id": 1202, "word": "himself", "pos": "代名詞", "meaning": "他自己"},
        1203: {"id": 1203, "word": "she", "pos": "代名詞(主格)", "meaning": "她"},
        1204: {"id": 1204, "word": "her", "pos": "代名詞(受格)", "meaning": "她"},
        1205: {"id": 1205, "word": "hers", "pos": "代名詞", "meaning": "她的"},
        1206: {"id": 1206, "word": "herself", "pos": "代名詞", "meaning": "她自己"},
        1207: {"id": 1207, "word": "it", "pos": "代名詞(主/受格)", "meaning": "它"},
        1208: {"id": 1208, "word": "its", "pos": "所有格", "meaning": "它的"},
        1209: {"id": 1209, "word": "itself", "pos": "代名詞", "meaning": "它自己"},
        1210: {"id": 1210, "word": "we", "pos": "代名詞(主格)", "meaning": "我們"},
        1211: {"id": 1211, "word": "us", "pos": "代名詞(受格)", "meaning": "我們"},
        1212: {"id": 1212, "word": "our", "pos": "所有格", "meaning": "我們的"},
        1213: {"id": 1213, "word": "ours", "pos": "代名詞", "meaning": "我們的"},
        1214: {"id": 1214, "word": "ourselves", "pos": "代名詞", "meaning": "我們自己"},
        1215: {"id": 1215, "word": "they", "pos": "代名詞(主格)", "meaning": "他們；它們"},
        1216: {"id": 1216, "word": "them", "pos": "代名詞(受格)", "meaning": "他們；它們"},
        1217: {"id": 1217, "word": "their", "pos": "所有格", "meaning": "他們的；它們的"},
        1218: {"id": 1218, "word": "theirs", "pos": "代名詞", "meaning": "他們的；它們的"},
        1219: {"id": 1219, "word": "themselves", "pos": "代名詞", "meaning": "他們自己；它們自己"},
        1266: {"id": 1266, "word": "in", "pos": "介系詞", "meaning": "在…裡面（較大範圍）"},
        1897: {"id": 1897, "word": "free", "pos": "形容詞", "meaning": "免費的；自由的"},
        1930: {"id": 1930, "word": "present", "pos": "形容詞", "meaning": "現在的；出席的"},
        1932: {"id": 1932, "word": "public", "pos": "形容詞", "meaning": "公眾的；公共的"},
        1944: {"id": 1944, "word": "serious", "pos": "形容詞", "meaning": "嚴肅的；嚴重的"},
        1948: {"id": 1948, "word": "single", "pos": "形容詞", "meaning": "單一的；單身的"},
        1957: {"id": 1957, "word": "terrible", "pos": "形容詞", "meaning": "糟糕的；可怕的"},
        1999: {"id": 1999, "word": "either", "pos": "副詞/連接詞", "meaning": "也（用於否定句）"},
    }
    parsed.update(overrides)

    missing = [idx for idx in range(1, 2001) if idx not in parsed]
    if missing:
        raise RuntimeError(f"Missing vocab ids: {missing[:20]}")

    return [parsed[idx] for idx in range(1, 2001)]


def build_html(vocab_list: list[dict[str, object]]) -> str:
    vocab_json = json.dumps(vocab_list, ensure_ascii=False, indent=2)
    return """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>暑期 2000 單字王</title>
  <style>
    :root {
      --bg: #f4efe6;
      --bg-deep: #f8fafc;
      --card: rgba(255, 255, 255, 0.9);
      --ink: #17324d;
      --muted: #59738f;
      --line: rgba(23, 50, 77, 0.12);
      --primary: #ff8a3d;
      --accent: #36b37e;
      --danger: #ef5350;
      --shadow: 0 18px 40px rgba(23, 50, 77, 0.12);
      --radius-xl: 28px;
      --radius-lg: 20px;
      --radius-md: 14px;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(255, 211, 135, 0.7), transparent 30%),
        radial-gradient(circle at top right, rgba(83, 178, 255, 0.25), transparent 25%),
        linear-gradient(160deg, var(--bg) 0%, #fefaf0 45%, var(--bg-deep) 100%);
    }

    body::before,
    body::after {
      content: "";
      position: fixed;
      border-radius: 50%;
      z-index: -1;
      filter: blur(10px);
      opacity: 0.55;
    }

    body::before {
      width: 240px;
      height: 240px;
      right: -60px;
      top: 110px;
      background: rgba(255, 173, 96, 0.32);
    }

    body::after {
      width: 300px;
      height: 300px;
      left: -100px;
      bottom: -80px;
      background: rgba(54, 179, 126, 0.18);
    }

    button,
    input {
      font: inherit;
    }

    .app {
      width: min(1200px, calc(100% - 32px));
      margin: 24px auto 40px;
      display: grid;
      gap: 18px;
    }

    .hero,
    .panel,
    .leaderboard,
    .study-card,
    .quiz-card,
    .login-card {
      background: var(--card);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.65);
      box-shadow: var(--shadow);
      border-radius: var(--radius-xl);
    }

    .hero {
      padding: 24px;
      display: flex;
      flex-wrap: wrap;
      gap: 18px;
      justify-content: space-between;
      align-items: center;
    }

    .hero-title h1 {
      margin: 0;
      font-size: clamp(2rem, 4vw, 3rem);
      line-height: 1.05;
    }

    .hero-title p {
      margin: 10px 0 0;
      color: var(--muted);
      font-size: 1rem;
    }

    .hero-badges {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
    }

    .badge {
      padding: 12px 16px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.86);
      border: 1px solid var(--line);
      display: flex;
      gap: 10px;
      align-items: center;
      min-height: 50px;
    }

    .badge strong {
      font-size: 1.1rem;
    }

    .page-grid {
      display: grid;
      grid-template-columns: minmax(0, 1.45fr) minmax(290px, 0.9fr);
      gap: 18px;
    }

    .stack {
      display: grid;
      gap: 18px;
    }

    .panel {
      padding: 20px;
    }

    .panel-title {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      margin-bottom: 16px;
    }

    .panel-title h2,
    .panel-title h3 {
      margin: 0;
      font-size: 1.2rem;
    }

    .muted {
      color: var(--muted);
    }

    .range-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
      margin-bottom: 14px;
    }

    label {
      display: grid;
      gap: 8px;
      color: var(--muted);
      font-weight: 700;
    }

    input[type="number"],
    input[type="text"] {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 13px 14px;
      background: rgba(255, 255, 255, 0.9);
      color: var(--ink);
      outline: none;
      transition: border-color 0.2s ease, transform 0.2s ease;
    }

    input:focus {
      border-color: rgba(255, 138, 61, 0.8);
      transform: translateY(-1px);
    }

    .actions,
    .tab-buttons,
    .card-actions,
    .quiz-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }

    .btn {
      border: none;
      border-radius: 14px;
      padding: 12px 16px;
      cursor: pointer;
      transition: transform 0.18s ease, box-shadow 0.18s ease, opacity 0.18s ease;
      font-weight: 800;
    }

    .btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 22px rgba(23, 50, 77, 0.14);
    }

    .btn:disabled {
      cursor: not-allowed;
      opacity: 0.55;
      transform: none;
      box-shadow: none;
    }

    .btn-primary {
      background: linear-gradient(135deg, var(--primary), #ffb14a);
      color: white;
    }

    .btn-secondary {
      background: #edf4fb;
      color: var(--ink);
    }

    .btn-success {
      background: rgba(54, 179, 126, 0.14);
      color: #14734d;
    }

    .tab-buttons {
      margin-top: 10px;
    }

    .tab-btn.active {
      background: var(--ink);
      color: white;
    }

    .stats {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 16px;
    }

    .stat-box {
      border-radius: 18px;
      padding: 16px;
      background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(244, 248, 252, 0.86));
      border: 1px solid var(--line);
    }

    .stat-box small {
      color: var(--muted);
      display: block;
      margin-bottom: 6px;
    }

    .tab-panel {
      display: none;
    }

    .tab-panel.active {
      display: block;
    }

    .study-card,
    .quiz-card {
      padding: 22px;
      background: linear-gradient(180deg, rgba(255,255,255,0.97), rgba(255,249,239,0.92));
    }

    .card-top {
      display: flex;
      justify-content: space-between;
      gap: 14px;
      align-items: center;
      margin-bottom: 14px;
      flex-wrap: wrap;
    }

    .pill {
      padding: 8px 12px;
      border-radius: 999px;
      background: rgba(23, 50, 77, 0.08);
      color: var(--ink);
      font-weight: 700;
    }

    .word-display {
      font-size: clamp(2.1rem, 6vw, 3.8rem);
      margin: 10px 0 4px;
      font-weight: 900;
      letter-spacing: 0.02em;
      word-break: break-word;
    }

    .meaning-display {
      margin: 0;
      font-size: clamp(1.2rem, 3vw, 1.6rem);
      color: var(--ink);
      font-weight: 800;
    }

    .meta-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin: 18px 0;
    }

    .meta-card {
      border-radius: 18px;
      background: white;
      border: 1px solid var(--line);
      padding: 14px;
    }

    .meta-card small {
      color: var(--muted);
      display: block;
      margin-bottom: 6px;
    }

    .toggle {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 10px 14px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.92);
      border: 1px solid var(--line);
      color: var(--ink);
      font-weight: 700;
    }

    .toggle input {
      width: 20px;
      height: 20px;
    }

    .quiz-question {
      font-size: clamp(1.7rem, 4.5vw, 2.7rem);
      margin: 12px 0 6px;
      font-weight: 900;
    }

    .quiz-subtitle {
      margin: 0 0 16px;
      color: var(--muted);
    }

    .option-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }

    .option-btn {
      width: 100%;
      text-align: left;
      padding: 16px;
      border-radius: 18px;
      border: 1px solid var(--line);
      background: white;
      color: var(--ink);
      cursor: pointer;
      font-weight: 800;
      min-height: 74px;
      transition: transform 0.18s ease, border-color 0.18s ease, background 0.18s ease;
    }

    .option-btn:hover {
      transform: translateY(-2px);
      border-color: rgba(255, 138, 61, 0.55);
    }

    .option-btn.correct {
      background: rgba(54, 179, 126, 0.16);
      border-color: rgba(54, 179, 126, 0.72);
      color: #116844;
    }

    .option-btn.wrong {
      background: rgba(239, 83, 80, 0.14);
      border-color: rgba(239, 83, 80, 0.72);
      color: #b43431;
    }

    .feedback {
      margin-top: 16px;
      min-height: 28px;
      font-weight: 800;
    }

    .feedback.success { color: #14734d; }
    .feedback.error { color: #b43431; }

    .leaderboard {
      padding: 20px;
      align-self: start;
      position: sticky;
      top: 20px;
    }

    .leaderboard-list {
      display: grid;
      gap: 10px;
      margin-top: 16px;
    }

    .leaderboard-item {
      display: grid;
      grid-template-columns: auto 1fr auto;
      gap: 12px;
      align-items: center;
      padding: 14px;
      border-radius: 18px;
      background: rgba(255,255,255,0.88);
      border: 1px solid var(--line);
    }

    .leaderboard-rank {
      width: 38px;
      height: 38px;
      border-radius: 50%;
      display: grid;
      place-items: center;
      font-weight: 900;
      background: rgba(255, 209, 102, 0.38);
    }

    .empty-box {
      padding: 18px;
      border-radius: 18px;
      background: rgba(255,255,255,0.76);
      border: 1px dashed var(--line);
      color: var(--muted);
    }

    .login-overlay {
      position: fixed;
      inset: 0;
      background: rgba(18, 35, 53, 0.36);
      backdrop-filter: blur(8px);
      display: none;
      align-items: center;
      justify-content: center;
      padding: 20px;
      z-index: 50;
    }

    .login-overlay.show {
      display: flex;
    }

    .login-card {
      width: min(520px, 100%);
      padding: 28px;
      background: linear-gradient(180deg, #fffdf8, #fff3da);
    }

    .login-card h2 {
      margin: 0 0 10px;
      font-size: 2rem;
    }

    .login-card p {
      margin: 0 0 18px;
      color: var(--muted);
      line-height: 1.7;
    }

    .message {
      margin-top: 12px;
      min-height: 24px;
      color: #b43431;
      font-weight: 800;
    }

    @media (max-width: 980px) {
      .page-grid {
        grid-template-columns: 1fr;
      }

      .leaderboard {
        position: static;
      }
    }

    @media (max-width: 720px) {
      .app {
        width: min(100% - 18px, 1000px);
        margin-top: 12px;
      }

      .hero,
      .panel,
      .leaderboard,
      .study-card,
      .quiz-card,
      .login-card {
        border-radius: 22px;
      }

      .range-grid,
      .stats,
      .meta-grid,
      .option-grid {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="login-overlay" id="loginOverlay">
    <div class="login-card">
      <h2>歡迎挑戰暑期 2000 單字王</h2>
      <p>先輸入小朋友的姓名，系統就會在這台電腦裡記住目前使用者與累積分數，之後打開同一個 HTML 檔案就能接著玩。</p>
      <label>
        姓名
        <input type="text" id="loginName" maxlength="20" placeholder="例如：小宇、小安" />
      </label>
      <div class="actions" style="margin-top: 16px;">
        <button class="btn btn-primary" id="loginBtn">開始學單字</button>
      </div>
      <div class="message" id="loginMessage"></div>
    </div>
  </div>

  <main class="app">
    <section class="hero">
      <div class="hero-title">
        <h1>暑期 2000 單字王</h1>
        <p>本機就能背單字、聽發音、做四選一測驗，排行榜也會永久保存在這台瀏覽器裡。</p>
      </div>
      <div class="hero-badges">
        <div class="badge">
          <span>目前玩家</span>
          <strong id="currentUserName">未登入</strong>
        </div>
        <div class="badge">
          <span>累積分數</span>
          <strong id="currentUserScore">0</strong>
        </div>
        <button class="btn btn-secondary" id="switchUserBtn">切換使用者</button>
      </div>
    </section>

    <div class="page-grid">
      <div class="stack">
        <section class="panel">
          <div class="panel-title">
            <div>
              <h2>自訂學習與測驗範圍</h2>
              <div class="muted">可輸入起始與結束編號，例如 1 到 50。</div>
            </div>
          </div>

          <div class="range-grid">
            <label>
              起始編號
              <input type="number" id="rangeStart" min="1" max="2000" />
            </label>
            <label>
              結束編號
              <input type="number" id="rangeEnd" min="1" max="2000" />
            </label>
          </div>

          <div class="actions">
            <button class="btn btn-primary" id="applyRangeBtn">套用範圍</button>
            <button class="btn btn-secondary" id="fullRangeBtn">使用全部 1-2000</button>
          </div>

          <div class="stats">
            <div class="stat-box">
              <small>目前範圍</small>
              <strong id="rangeSummary">1 - 50</strong>
            </div>
            <div class="stat-box">
              <small>本次單字數</small>
              <strong id="rangeCount">50</strong>
            </div>
            <div class="stat-box">
              <small>系統總單字</small>
              <strong id="totalCount">2000</strong>
            </div>
          </div>
        </section>

        <section class="panel">
          <div class="panel-title">
            <div>
              <h2>學習與測驗</h2>
              <div class="muted">先用學習卡複習，再用測驗模式檢查記憶。</div>
            </div>
          </div>

          <div class="tab-buttons">
            <button class="btn btn-secondary tab-btn active" data-tab="study">Study Mode</button>
            <button class="btn btn-secondary tab-btn" data-tab="quiz">Quiz Mode</button>
          </div>

          <div class="tab-panel active" id="studyPanel" style="margin-top: 18px;">
            <div class="study-card">
              <div class="card-top">
                <span class="pill" id="studyProgress">第 1 / 50 張</span>
                <label class="toggle">
                  <input type="checkbox" id="autoSpeakToggle" />
                  自動發音
                </label>
              </div>
              <div class="word-display" id="studyWord">adult</div>
              <p class="meaning-display" id="studyMeaning">成年人</p>
              <div class="meta-grid">
                <div class="meta-card">
                  <small>編號</small>
                  <strong id="studyId">1</strong>
                </div>
                <div class="meta-card">
                  <small>詞性</small>
                  <strong id="studyPos">名詞</strong>
                </div>
                <div class="meta-card">
                  <small>英文發音</small>
                  <strong>en-US</strong>
                </div>
              </div>
              <div class="card-actions">
                <button class="btn btn-secondary" id="prevCardBtn">上一張</button>
                <button class="btn btn-primary" id="speakBtn">發音一次</button>
                <button class="btn btn-secondary" id="nextCardBtn">下一張</button>
              </div>
              <div class="muted" id="speechHint" style="margin-top: 14px;">提示：若瀏覽器支援語音，按下按鈕即可播放英文發音。</div>
            </div>
          </div>

          <div class="tab-panel" id="quizPanel" style="margin-top: 18px;">
            <div class="quiz-card">
              <div class="card-top">
                <span class="pill" id="quizRangePill">範圍 1 - 50</span>
                <span class="pill">答對 +10 分</span>
              </div>
              <div class="quiz-question" id="quizWord">adult</div>
              <p class="quiz-subtitle" id="quizMeta">請選出正確的中文意思</p>
              <div class="option-grid" id="quizOptions"></div>
              <div class="feedback" id="quizFeedback"></div>
              <div class="quiz-actions" style="margin-top: 14px;">
                <button class="btn btn-success" id="nextQuizBtn">下一題</button>
                <button class="btn btn-secondary" id="quizSpeakBtn">聽發音</button>
              </div>
            </div>
          </div>
        </section>
      </div>

      <aside class="leaderboard">
        <div class="panel-title">
          <div>
            <h3>單字王者排行榜</h3>
            <div class="muted">依照本機瀏覽器紀錄即時排序。</div>
          </div>
        </div>
        <div class="leaderboard-list" id="leaderboardList"></div>
      </aside>
    </div>
  </main>

  <script>
    const vocabData = __VOCAB_DATA__;
    // 若未來有新版單字表，可直接替換上方 vocabData 內容，維持同樣欄位格式即可。

    const STORAGE_KEYS = {
      players: "summer2000king.players",
      currentUser: "summer2000king.currentUser",
      autoSpeak: "summer2000king.autoSpeak"
    };

    const state = {
      currentUser: null,
      rangeStart: 1,
      rangeEnd: Math.min(50, vocabData.length),
      filteredWords: [],
      studyIndex: 0,
      quizItem: null,
      quizLocked: false,
      autoSpeak: false,
      voices: []
    };

    const el = {
      loginOverlay: document.getElementById("loginOverlay"),
      loginName: document.getElementById("loginName"),
      loginBtn: document.getElementById("loginBtn"),
      loginMessage: document.getElementById("loginMessage"),
      currentUserName: document.getElementById("currentUserName"),
      currentUserScore: document.getElementById("currentUserScore"),
      switchUserBtn: document.getElementById("switchUserBtn"),
      rangeStart: document.getElementById("rangeStart"),
      rangeEnd: document.getElementById("rangeEnd"),
      applyRangeBtn: document.getElementById("applyRangeBtn"),
      fullRangeBtn: document.getElementById("fullRangeBtn"),
      rangeSummary: document.getElementById("rangeSummary"),
      rangeCount: document.getElementById("rangeCount"),
      totalCount: document.getElementById("totalCount"),
      leaderboardList: document.getElementById("leaderboardList"),
      studyProgress: document.getElementById("studyProgress"),
      studyWord: document.getElementById("studyWord"),
      studyMeaning: document.getElementById("studyMeaning"),
      studyId: document.getElementById("studyId"),
      studyPos: document.getElementById("studyPos"),
      prevCardBtn: document.getElementById("prevCardBtn"),
      nextCardBtn: document.getElementById("nextCardBtn"),
      speakBtn: document.getElementById("speakBtn"),
      speechHint: document.getElementById("speechHint"),
      autoSpeakToggle: document.getElementById("autoSpeakToggle"),
      quizRangePill: document.getElementById("quizRangePill"),
      quizWord: document.getElementById("quizWord"),
      quizMeta: document.getElementById("quizMeta"),
      quizOptions: document.getElementById("quizOptions"),
      quizFeedback: document.getElementById("quizFeedback"),
      nextQuizBtn: document.getElementById("nextQuizBtn"),
      quizSpeakBtn: document.getElementById("quizSpeakBtn"),
      tabButtons: [...document.querySelectorAll(".tab-btn")],
      tabPanels: {
        study: document.getElementById("studyPanel"),
        quiz: document.getElementById("quizPanel")
      }
    };

    function safeReadJSON(key, fallback) {
      try {
        const raw = localStorage.getItem(key);
        return raw ? JSON.parse(raw) : fallback;
      } catch (error) {
        console.warn("讀取 localStorage 失敗", error);
        return fallback;
      }
    }

    function safeWriteJSON(key, value) {
      localStorage.setItem(key, JSON.stringify(value));
    }

    function getPlayers() {
      const players = safeReadJSON(STORAGE_KEYS.players, []);
      return Array.isArray(players) ? players : [];
    }

    function savePlayers(players) {
      safeWriteJSON(STORAGE_KEYS.players, players);
    }

    function getCurrentUserRecord() {
      const players = getPlayers();
      return players.find((player) => player.name === state.currentUser) || null;
    }

    function upsertPlayer(name) {
      // localStorage 會保存「所有玩家列表」與「目前登入玩家名稱」。
      // 同名玩家再次登入時沿用原本分數；新名字才新增一筆，這樣就能在同一台電腦做多使用者排行榜。
      const trimmed = name.trim();
      const players = getPlayers();
      const existing = players.find((player) => player.name === trimmed);

      if (!existing) {
        players.push({ name: trimmed, score: 0, updatedAt: Date.now() });
        savePlayers(players);
      }

      state.currentUser = trimmed;
      localStorage.setItem(STORAGE_KEYS.currentUser, trimmed);
      renderCurrentUser();
      renderLeaderboard();
    }

    function addScore(points) {
      if (!state.currentUser) return;
      const players = getPlayers();
      const target = players.find((player) => player.name === state.currentUser);
      if (!target) return;
      target.score += points;
      target.updatedAt = Date.now();
      savePlayers(players);
      renderCurrentUser();
      renderLeaderboard();
    }

    function renderCurrentUser() {
      const record = getCurrentUserRecord();
      el.currentUserName.textContent = state.currentUser || "未登入";
      el.currentUserScore.textContent = record ? String(record.score) : "0";
    }

    function renderLeaderboard() {
      const players = getPlayers()
        .sort((a, b) => (b.score - a.score) || (a.updatedAt - b.updatedAt));

      if (!players.length) {
        el.leaderboardList.innerHTML = '<div class="empty-box">還沒有玩家紀錄，先登入開始挑戰吧。</div>';
        return;
      }

      el.leaderboardList.innerHTML = players.slice(0, 12).map((player, index) => `
        <div class="leaderboard-item">
          <div class="leaderboard-rank">${index + 1}</div>
          <div>
            <strong>${escapeHtml(player.name)}</strong>
            <div class="muted">${player.name === state.currentUser ? "目前登入中" : "本機歷史紀錄"}</div>
          </div>
          <strong>${player.score} 分</strong>
        </div>
      `).join("");
    }

    function escapeHtml(text) {
      return text
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
    }

    function clamp(num, min, max) {
      return Math.min(Math.max(num, min), max);
    }

    function normalizeRange(start, end) {
      const safeStart = clamp(Number(start) || 1, 1, vocabData.length);
      const safeEnd = clamp(Number(end) || safeStart, 1, vocabData.length);
      return safeStart <= safeEnd ? [safeStart, safeEnd] : [safeEnd, safeStart];
    }

    function applyRange(start = el.rangeStart.value, end = el.rangeEnd.value) {
      const [rangeStart, rangeEnd] = normalizeRange(start, end);
      state.rangeStart = rangeStart;
      state.rangeEnd = rangeEnd;
      state.filteredWords = vocabData.filter((item) => item.id >= rangeStart && item.id <= rangeEnd);
      state.studyIndex = 0;

      el.rangeStart.value = rangeStart;
      el.rangeEnd.value = rangeEnd;
      el.rangeSummary.textContent = `${rangeStart} - ${rangeEnd}`;
      el.rangeCount.textContent = String(state.filteredWords.length);
      el.quizRangePill.textContent = `範圍 ${rangeStart} - ${rangeEnd}`;

      renderStudyCard();
      loadQuizQuestion();
    }

    function renderStudyCard(shouldAutoSpeak = false) {
      const item = state.filteredWords[state.studyIndex];
      if (!item) {
        el.studyProgress.textContent = "目前沒有單字";
        el.studyWord.textContent = "請先設定有效範圍";
        el.studyMeaning.textContent = "系統找不到這段編號的單字。";
        el.studyId.textContent = "-";
        el.studyPos.textContent = "-";
        el.prevCardBtn.disabled = true;
        el.nextCardBtn.disabled = true;
        return;
      }

      el.studyProgress.textContent = `第 ${state.studyIndex + 1} / ${state.filteredWords.length} 張`;
      el.studyWord.textContent = item.word;
      el.studyMeaning.textContent = item.meaning;
      el.studyId.textContent = String(item.id);
      el.studyPos.textContent = item.pos;
      el.prevCardBtn.disabled = state.studyIndex === 0;
      el.nextCardBtn.disabled = state.studyIndex === state.filteredWords.length - 1;

      if (state.autoSpeak && shouldAutoSpeak) {
        speakWord(item.word);
      }
    }

    function moveStudyCard(step) {
      if (!state.filteredWords.length) return;
      state.studyIndex = clamp(state.studyIndex + step, 0, state.filteredWords.length - 1);
      renderStudyCard(true);
    }

    function loadVoices() {
      if (!("speechSynthesis" in window)) return;
      state.voices = window.speechSynthesis.getVoices();
    }

    function speakWord(word) {
      // 使用瀏覽器內建 Web Speech API，在本機直接合成英文發音，不會呼叫外部伺服器。
      if (!("speechSynthesis" in window)) {
        el.speechHint.textContent = "這個瀏覽器不支援語音朗讀，仍可繼續使用其他功能。";
        return;
      }

      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(word);
      utterance.lang = "en-US";
      utterance.rate = 0.92;
      utterance.pitch = 1.02;

      const voice = state.voices.find((item) => item.lang === "en-US")
        || state.voices.find((item) => item.lang.toLowerCase().startsWith("en"));

      if (voice) {
        utterance.voice = voice;
      }

      window.speechSynthesis.speak(utterance);
    }

    function pickRandomItem(list) {
      return list[Math.floor(Math.random() * list.length)];
    }

    function shuffle(array) {
      // 使用 Fisher-Yates 洗牌，讓四個選項每次都以真正隨機的順序出現，避免答案位置被記住。
      const cloned = [...array];
      for (let i = cloned.length - 1; i > 0; i -= 1) {
        const j = Math.floor(Math.random() * (i + 1));
        [cloned[i], cloned[j]] = [cloned[j], cloned[i]];
      }
      return cloned;
    }

    function buildQuizOptions(answerItem) {
      // 先從目前範圍找 3 個不重複干擾項；如果範圍太小，再從整份單字庫補齊。
      const meaningSet = new Set([answerItem.meaning]);
      const distractors = [];
      const primaryPool = shuffle(state.filteredWords.filter((item) => item.id !== answerItem.id));
      const fallbackPool = shuffle(vocabData.filter((item) => item.id !== answerItem.id));

      for (const source of [primaryPool, fallbackPool]) {
        for (const item of source) {
          if (meaningSet.has(item.meaning)) continue;
          meaningSet.add(item.meaning);
          distractors.push(item.meaning);
          if (distractors.length === 3) break;
        }
        if (distractors.length === 3) break;
      }

      const optionList = [answerItem.meaning, ...distractors];
      return shuffle(optionList);
    }

    function loadQuizQuestion() {
      if (!state.filteredWords.length) {
        el.quizWord.textContent = "請先設定有效範圍";
        el.quizMeta.textContent = "目前沒有可抽題的單字。";
        el.quizOptions.innerHTML = "";
        el.quizFeedback.textContent = "";
        return;
      }

      state.quizLocked = false;
      state.quizItem = pickRandomItem(state.filteredWords);
      const options = buildQuizOptions(state.quizItem);

      el.quizWord.textContent = state.quizItem.word;
      el.quizMeta.textContent = `${state.quizItem.pos}｜請選出正確的中文意思`;
      el.quizFeedback.textContent = "";
      el.quizFeedback.className = "feedback";

      el.quizOptions.innerHTML = options.map((meaning) => `
        <button class="option-btn" data-meaning="${escapeHtml(meaning)}">${escapeHtml(meaning)}</button>
      `).join("");

      [...el.quizOptions.querySelectorAll(".option-btn")].forEach((button) => {
        button.addEventListener("click", () => checkAnswer(button));
      });
    }

    function checkAnswer(button) {
      if (state.quizLocked || !state.quizItem) return;
      state.quizLocked = true;

      const correctMeaning = state.quizItem.meaning;
      const buttons = [...el.quizOptions.querySelectorAll(".option-btn")];
      const selectedMeaning = button.textContent;

      buttons.forEach((itemButton) => {
        const isCorrect = itemButton.textContent === correctMeaning;
        itemButton.disabled = true;
        if (isCorrect) itemButton.classList.add("correct");
      });

      if (selectedMeaning === correctMeaning) {
        button.classList.add("correct");
        addScore(10);
        el.quizFeedback.textContent = `答對了！「${state.quizItem.word}」就是「${correctMeaning}」。`;
        el.quizFeedback.className = "feedback success";
      } else {
        button.classList.add("wrong");
        el.quizFeedback.textContent = `答錯了，正確答案是「${correctMeaning}」。`;
        el.quizFeedback.className = "feedback error";
      }
    }

    function showLogin(force = false) {
      const savedUser = localStorage.getItem(STORAGE_KEYS.currentUser);
      if (!force && savedUser) {
        state.currentUser = savedUser;
        renderCurrentUser();
        renderLeaderboard();
        el.loginOverlay.classList.remove("show");
        return;
      }

      if (force) {
        localStorage.removeItem(STORAGE_KEYS.currentUser);
        state.currentUser = null;
        renderCurrentUser();
      }

      el.loginName.value = "";
      el.loginMessage.textContent = "";
      el.loginOverlay.classList.add("show");
      setTimeout(() => el.loginName.focus(), 60);
    }

    function submitLogin() {
      const name = el.loginName.value.trim();
      if (!name) {
        el.loginMessage.textContent = "請先輸入姓名。";
        return;
      }
      upsertPlayer(name);
      el.loginOverlay.classList.remove("show");
      applyRange();
    }

    function switchTab(tab) {
      el.tabButtons.forEach((button) => {
        button.classList.toggle("active", button.dataset.tab === tab);
      });
      Object.entries(el.tabPanels).forEach(([name, panel]) => {
        panel.classList.toggle("active", name === tab);
      });
    }

    function init() {
      el.totalCount.textContent = String(vocabData.length);
      el.rangeStart.value = state.rangeStart;
      el.rangeEnd.value = state.rangeEnd;

      state.autoSpeak = localStorage.getItem(STORAGE_KEYS.autoSpeak) === "true";
      el.autoSpeakToggle.checked = state.autoSpeak;

      loadVoices();
      if ("speechSynthesis" in window) {
        window.speechSynthesis.onvoiceschanged = loadVoices;
      } else {
        el.speechHint.textContent = "這個瀏覽器不支援語音朗讀，仍可繼續使用學習卡與測驗。";
      }

      el.loginBtn.addEventListener("click", submitLogin);
      el.loginName.addEventListener("keydown", (event) => {
        if (event.key === "Enter") submitLogin();
      });
      el.switchUserBtn.addEventListener("click", () => showLogin(true));
      el.applyRangeBtn.addEventListener("click", () => applyRange());
      el.fullRangeBtn.addEventListener("click", () => applyRange(1, vocabData.length));
      el.prevCardBtn.addEventListener("click", () => moveStudyCard(-1));
      el.nextCardBtn.addEventListener("click", () => moveStudyCard(1));
      el.speakBtn.addEventListener("click", () => {
        const item = state.filteredWords[state.studyIndex];
        if (item) speakWord(item.word);
      });
      el.quizSpeakBtn.addEventListener("click", () => {
        if (state.quizItem) speakWord(state.quizItem.word);
      });
      el.nextQuizBtn.addEventListener("click", loadQuizQuestion);
      el.autoSpeakToggle.addEventListener("change", (event) => {
        state.autoSpeak = event.target.checked;
        localStorage.setItem(STORAGE_KEYS.autoSpeak, String(state.autoSpeak));
      });

      el.tabButtons.forEach((button) => {
        button.addEventListener("click", () => switchTab(button.dataset.tab));
      });

      renderLeaderboard();
      renderCurrentUser();
      applyRange();
      showLogin();
    }

    init();
  </script>
</body>
</html>
""".replace("__VOCAB_DATA__", vocab_json)


def main() -> None:
    vocab_list = load_vocab()
    html = build_html(vocab_list)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH} with {len(vocab_list)} vocab items.")


if __name__ == "__main__":
    main()
