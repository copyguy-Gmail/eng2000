import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "tmp" / "vocab6000.csv"
TEMPLATE_PATH = ROOT / "index.html"
OUTPUT_PATH = ROOT / "eng6000" / "index.html"
LEVEL1_KK_PATH = ROOT / "eng6000" / "level1_kk.json"


def load_vocab():
    level1_kk = {}
    if LEVEL1_KK_PATH.exists():
        level1_kk = json.loads(LEVEL1_KK_PATH.read_text(encoding="utf-8"))

    items = []
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            if len(row) < 6:
                continue
            item_id, level, word, pos, display, meaning = [cell.strip() for cell in row[:6]]
            if not item_id or not word:
                continue
            items.append({
                "id": int(item_id),
                "level": int(level) if level.isdigit() else 0,
                "word": word,
                "pos": pos,
                "display": display,
                "meaning": meaning,
                "kk": level1_kk.get(word, "")
            })
    return items


def replace_between(text, start_pattern, end_pattern, replacement):
    pattern = re.compile(start_pattern + r"[\s\S]*?" + end_pattern)
    return pattern.sub(replacement, text, count=1)


def main():
    vocab = load_vocab()
    html = TEMPLATE_PATH.read_text(encoding="utf-8")
    vocab_json = json.dumps(vocab, ensure_ascii=False, indent=2)

    html = replace_between(
        html,
        r"const vocabData = \[",
        r"\n\];",
        "const vocabData = " + vocab_json + ";"
    )

    replacements = {
        "暑期 2000 單字王": "國高中英文 6000 單字王",
        "本機就能背單字、聽發音、做四選一測驗，排行榜也會永久保存在這台瀏覽器裡。":
            "依 1-6 級循序背學測 6000 單字，支援學習卡、四選一與填空測驗。",
        "使用全部 1-2000": "使用全部 1-6009",
        "系統總單字": "系統總單字",
        "summer2000king.players": "eng6000king.players",
        "summer2000king.currentUser": "eng6000king.currentUser",
        "summer2000king.autoSpeak": "eng6000king.autoSpeak",
        "summer2000king.history": "eng6000king.history",
        "summer2000king.accessPassed": "eng6000king.accessPassed",
        "若未來有新版單字表，可直接替換上方 vocabData 內容，維持同樣欄位格式即可。":
            "此 vocabData 由學測6000字_加編號.csv 產生，欄位包含 id、level、word、pos、display、meaning。"
    }
    for old, new in replacements.items():
        html = html.replace(old, new)

    # Login title currently uses numeric entities in the template to avoid encoding issues.
    html = html.replace("&#26257;&#26399; 2000 &#21934;&#23383;&#29579;", "國高中英文 6000 單字王")

    html = re.sub(
        r'const REMOTE_SCORE_API_URL = ".*?";',
        'const REMOTE_SCORE_API_URL = "";',
        html,
        count=1
    )

    html = html.replace(
        '<div class="actions">\n'
        '            <button class="btn btn-primary" id="applyRangeBtn">套用範圍</button>\n'
        '            <button class="btn btn-secondary" id="fullRangeBtn">使用全部 1-6009</button>\n'
        '          </div>',
        '<div class="actions">\n'
        '            <button class="btn btn-primary" id="applyRangeBtn">套用範圍</button>\n'
        '            <button class="btn btn-secondary" id="fullRangeBtn">使用全部 1-6009</button>\n'
        '          </div>\n\n'
        '          <div class="level-panel">\n'
        '            <div class="muted">依程度快速選擇：CSV 第 1 級約等於 0-1 級/國一基礎，2-3 級約國中畢業，5-6 級約高中畢業。</div>\n'
        '            <div class="level-buttons">\n'
        '              <button class="level-btn active" data-levels="1,2,3,4,5,6">全部 1-6 級</button>\n'
        '              <button class="level-btn" data-levels="1">第 1 級（國一）</button>\n'
        '              <button class="level-btn" data-levels="2,3">第 2-3 級</button>\n'
        '              <button class="level-btn" data-levels="4">第 4 級</button>\n'
        '              <button class="level-btn" data-levels="5,6">第 5-6 級</button>\n'
        '            </div>\n'
        '          </div>'
    )

    html = html.replace(
        "const state = {\n      currentUser: null,",
        "const state = {\n      currentUser: null,\n      selectedLevels: [1, 2, 3, 4, 5, 6],"
    )
    html = html.replace(
        'tabButtons: [...document.querySelectorAll(".tab-btn")],',
        'levelButtons: [...document.querySelectorAll(".level-btn")],\n      tabButtons: [...document.querySelectorAll(".tab-btn")],'
    )
    html = html.replace(
        "state.filteredWords = vocabData.filter((item) => item.id >= rangeStart && item.id <= rangeEnd);",
        "state.filteredWords = vocabData.filter((item) => item.id >= rangeStart && item.id <= rangeEnd && state.selectedLevels.includes(item.level));"
    )
    html = html.replace(
        'el.studyMeta.textContent = `${item.id} / ${item.pos} / ${item.kk || "待補"}`;',
        'el.studyMeta.textContent = `${item.id} / 第 ${item.level} 級 / ${item.pos}${item.kk ? " / " + item.kk : ""}`;'
    )
    html = html.replace(
        'el.quizMeta.textContent = `${state.quizItem.pos}｜請選出正確的中文意思`;',
        'el.quizMeta.textContent = `第 ${state.quizItem.level} 級｜${state.quizItem.pos}｜請選出正確的中文意思`;'
    )
    html = html.replace(
        'el.fillHint.textContent = `編號 ${state.fillItem.id}，請輸入完整英文單字。`;',
        'el.fillHint.textContent = `編號 ${state.fillItem.id}｜第 ${state.fillItem.level} 級，請輸入完整英文單字。`;'
    )
    html = html.replace(
        "function switchTab(tab) {",
        "function setLevelFilter(levelText) {\n"
        "      state.selectedLevels = levelText.split(',').map(Number);\n"
        "      el.levelButtons.forEach((button) => button.classList.toggle('active', button.dataset.levels === levelText));\n"
        "      applyRange(1, vocabData.length);\n"
        "    }\n\n"
        "    function switchTab(tab) {"
    )
    html = html.replace(
        "el.tabButtons.forEach((button) => {\n        button.addEventListener(\"click\", () => switchTab(button.dataset.tab));\n      });",
        "el.levelButtons.forEach((button) => {\n        button.addEventListener(\"click\", () => setLevelFilter(button.dataset.levels));\n      });\n\n"
        "      el.tabButtons.forEach((button) => {\n        button.addEventListener(\"click\", () => switchTab(button.dataset.tab));\n      });"
    )

    css = """

    .level-panel {
      margin-top: 16px;
      display: grid;
      gap: 12px;
      padding: 14px;
      border-radius: 20px;
      background: rgba(255, 255, 255, 0.72);
      border: 1px solid var(--line);
    }

    .level-buttons {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }

    .level-btn {
      border: 0;
      border-radius: 999px;
      padding: 10px 14px;
      font-weight: 900;
      color: var(--ink);
      background: #eef5fc;
      cursor: pointer;
    }

    .level-btn.active {
      color: white;
      background: var(--primary);
      box-shadow: 0 10px 18px rgba(255, 138, 61, 0.24);
    }
"""
    html = html.replace("\n  </style>", css + "\n  </style>", 1)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html, encoding="utf-8", newline="\n")
    print(f"generated {OUTPUT_PATH} with {len(vocab)} words")


if __name__ == "__main__":
    main()
