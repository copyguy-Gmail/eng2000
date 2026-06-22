from __future__ import annotations

import json
import re
from pathlib import Path

import pronouncing


INDEX_PATH = Path(r"C:\Users\chungyi\Documents\LAB\codex_lab\index.html")

ARPABET_TO_KK = {
    "AA": "ɑ",
    "AE": "æ",
    "AH": "ʌ",
    "AO": "ɔ",
    "AW": "aʊ",
    "AY": "aɪ",
    "B": "b",
    "CH": "tʃ",
    "D": "d",
    "DH": "ð",
    "EH": "ɛ",
    "ER": "ɝ",
    "EY": "e",
    "F": "f",
    "G": "g",
    "HH": "h",
    "IH": "ɪ",
    "IY": "i",
    "JH": "dʒ",
    "K": "k",
    "L": "l",
    "M": "m",
    "N": "n",
    "NG": "ŋ",
    "OW": "o",
    "OY": "ɔɪ",
    "P": "p",
    "R": "r",
    "S": "s",
    "SH": "ʃ",
    "T": "t",
    "TH": "θ",
    "UH": "ʊ",
    "UW": "u",
    "V": "v",
    "W": "w",
    "Y": "j",
    "Z": "z",
    "ZH": "ʒ",
}

SPECIAL_KK = {
    "a": "ə",
    "i": "aɪ",
    "i'm": "aɪm",
    "o'clock": "əˈklɑk",
    "t-shirt": "ˈti ʃɝt",
    "e-mail": "ˈi meɪl",
    "double": "ˈdʌbəl",
    "tenth": "tɛnθ",
    "double tenth day": "ˈdʌbəl tɛnθ de",
    "dragon-boat festival": "ˈdrægən bot ˈfɛstəvəl",
    "chinese new year": "tʃaɪˈniz nu jɪr",
    "new year's eve": "nu jɪrz iv",
}


def replace_once(text: str, old: str, new: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f"Snippet not found: {old[:80]}")
    return text.replace(old, new, 1)


def phones_to_kk(phones: str) -> str:
    tokens = phones.split()
    output: list[str] = []
    for token in tokens:
        stress = ""
        base = token
        if token[-1:].isdigit():
            stress_digit = token[-1]
            base = token[:-1]
            if stress_digit == "1":
                stress = "ˈ"
            elif stress_digit == "2":
                stress = "ˌ"
        mapped = ARPABET_TO_KK.get(base, base.lower())
        output.append(f"{stress}{mapped}")
    return "".join(output)


def word_to_kk(word: str) -> str:
    normalized = word.strip().lower().replace("’", "'")
    if normalized in SPECIAL_KK:
        return SPECIAL_KK[normalized]

    parts = re.findall(r"[a-zA-Z]+(?:['’][a-zA-Z]+)?", normalized.replace("-", " "))
    kk_parts: list[str] = []

    for part in parts:
        if part in SPECIAL_KK:
            kk_parts.append(SPECIAL_KK[part])
            continue
        phones = pronouncing.phones_for_word(part)
        if not phones and part.endswith("'s"):
            phones = pronouncing.phones_for_word(part[:-2])
            if phones:
                kk_parts.append(f"{phones_to_kk(phones[0])}z")
                continue
        if phones:
            kk_parts.append(phones_to_kk(phones[0]))
        else:
            kk_parts.append(part)

    return " / ".join(kk_parts) if kk_parts else normalized


def update_vocab(text: str) -> str:
    marker = "const vocabData = "
    start = text.find(marker)
    if start == -1:
        raise RuntimeError("Could not locate vocabData array start.")
    json_start = start + len(marker)
    array_start = text.find("[", json_start)
    array_end = text.find("\n];\n    // 若未來有新版單字表", array_start)
    if array_start == -1 or array_end == -1:
        raise RuntimeError("Could not locate vocabData array bounds.")

    vocab = json.loads(text[array_start:array_end + 2])
    for item in vocab:
        item["kk"] = word_to_kk(item["word"])

    vocab_json = json.dumps(vocab, ensure_ascii=False, indent=2)
    return text[:array_start] + vocab_json + text[array_end + 2:]


def main() -> None:
    text = INDEX_PATH.read_text(encoding="utf-8")
    text = update_vocab(text)

    text = replace_once(
        text,
        '<p>先輸入小朋友的姓名，系統就會在這台電腦裡記住目前使用者與累積分數，之後打開同一個 HTML 檔案就能接著玩。</p>\n      <label>\n        姓名\n        <input type="text" id="loginName" maxlength="20" placeholder="例如：小宇、小安" />\n      </label>\n      <div class="actions" style="margin-top: 16px;">',
        '<p>先輸入通關密碼與姓名。只要密碼正確，系統就會在這台電腦裡記住目前使用者與累積分數，之後同一個分頁可直接繼續使用。</p>\n      <label>\n        通關密碼\n        <input type="password" id="loginPassword" maxlength="20" placeholder="請輸入 541115" />\n      </label>\n      <label>\n        姓名\n        <input type="text" id="loginName" maxlength="20" placeholder="例如：小宇、小安" />\n      </label>\n      <div class="actions" style="margin-top: 16px;">',
    )
    text = replace_once(
        text,
        '<div class="meta-grid">\n                <div class="meta-card">\n                  <small>編號</small>\n                  <strong id="studyId">1</strong>\n                </div>\n                <div class="meta-card">\n                  <small>詞性</small>\n                  <strong id="studyPos">名詞</strong>\n                </div>\n                <div class="meta-card">\n                  <small>英文發音</small>\n                  <strong>en-US</strong>\n                </div>\n              </div>',
        '<div class="meta-grid">\n                <div class="meta-card">\n                  <small>編號</small>\n                  <strong id="studyId">1</strong>\n                </div>\n                <div class="meta-card">\n                  <small>詞性</small>\n                  <strong id="studyPos">名詞</strong>\n                </div>\n                <div class="meta-card">\n                  <small>KK 音標</small>\n                  <strong id="studyKK">əˈdʌlt</strong>\n                </div>\n                <div class="meta-card">\n                  <small>英文發音</small>\n                  <strong>en-US</strong>\n                </div>\n              </div>',
    )
    text = replace_once(
        text,
        '      players: "summer2000king.players",\n      currentUser: "summer2000king.currentUser",\n      autoSpeak: "summer2000king.autoSpeak"\n    };',
        '      players: "summer2000king.players",\n      currentUser: "summer2000king.currentUser",\n      autoSpeak: "summer2000king.autoSpeak"\n    };\n\n    const ACCESS_PASSWORD = "541115";\n    const SESSION_KEYS = {\n      accessPassed: "summer2000king.accessPassed"\n    };',
    )
    text = replace_once(
        text,
        '      loginOverlay: document.getElementById("loginOverlay"),\n      loginName: document.getElementById("loginName"),\n      loginBtn: document.getElementById("loginBtn"),',
        '      loginOverlay: document.getElementById("loginOverlay"),\n      loginPassword: document.getElementById("loginPassword"),\n      loginName: document.getElementById("loginName"),\n      loginBtn: document.getElementById("loginBtn"),',
    )
    text = replace_once(
        text,
        '      studyId: document.getElementById("studyId"),\n      studyPos: document.getElementById("studyPos"),\n      prevCardBtn: document.getElementById("prevCardBtn"),',
        '      studyId: document.getElementById("studyId"),\n      studyPos: document.getElementById("studyPos"),\n      studyKK: document.getElementById("studyKK"),\n      prevCardBtn: document.getElementById("prevCardBtn"),',
    )
    text = replace_once(
        text,
        '        el.studyId.textContent = "-";\n        el.studyPos.textContent = "-";\n        el.prevCardBtn.disabled = true;',
        '        el.studyId.textContent = "-";\n        el.studyPos.textContent = "-";\n        el.studyKK.textContent = "-";\n        el.prevCardBtn.disabled = true;',
    )
    text = replace_once(
        text,
        '      el.studyMeaning.textContent = item.meaning;\n      el.studyId.textContent = String(item.id);\n      el.studyPos.textContent = item.pos;\n      el.prevCardBtn.disabled = state.studyIndex === 0;',
        '      el.studyMeaning.textContent = item.meaning;\n      el.studyId.textContent = String(item.id);\n      el.studyPos.textContent = item.pos;\n      el.studyKK.textContent = item.kk || "待補";\n      el.prevCardBtn.disabled = state.studyIndex === 0;',
    )
    text = replace_once(
        text,
        '    function showLogin(force = false) {\n      const savedUser = localStorage.getItem(STORAGE_KEYS.currentUser);\n      if (!force && savedUser) {\n        state.currentUser = savedUser;\n        renderCurrentUser();\n        renderLeaderboard();\n        el.loginOverlay.classList.remove("show");\n        return;\n      }\n\n      if (force) {\n        localStorage.removeItem(STORAGE_KEYS.currentUser);\n        state.currentUser = null;\n        renderCurrentUser();\n      }\n\n      el.loginName.value = "";\n      el.loginMessage.textContent = "";\n      el.loginOverlay.classList.add("show");\n      setTimeout(() => el.loginName.focus(), 60);\n    }',
        '    function showLogin(force = false) {\n      const savedUser = localStorage.getItem(STORAGE_KEYS.currentUser);\n      const passed = sessionStorage.getItem(SESSION_KEYS.accessPassed) === "true";\n      if (!force && savedUser && passed) {\n        state.currentUser = savedUser;\n        renderCurrentUser();\n        renderLeaderboard();\n        el.loginOverlay.classList.remove("show");\n        return;\n      }\n\n      if (force) {\n        localStorage.removeItem(STORAGE_KEYS.currentUser);\n        state.currentUser = null;\n        renderCurrentUser();\n      }\n\n      el.loginPassword.value = "";\n      el.loginName.value = force && savedUser ? savedUser : "";\n      el.loginMessage.textContent = "";\n      el.loginOverlay.classList.add("show");\n      setTimeout(() => (passed ? el.loginName : el.loginPassword).focus(), 60);\n    }',
    )
    text = replace_once(
        text,
        '    function submitLogin() {\n      const name = el.loginName.value.trim();\n      if (!name) {\n        el.loginMessage.textContent = "請先輸入姓名。";\n        return;\n      }\n      upsertPlayer(name);\n      el.loginOverlay.classList.remove("show");\n      applyRange();\n    }',
        '    function submitLogin() {\n      const name = el.loginName.value.trim();\n      const passed = sessionStorage.getItem(SESSION_KEYS.accessPassed) === "true";\n      const password = el.loginPassword.value.trim();\n\n      if (!passed && password !== ACCESS_PASSWORD) {\n        el.loginMessage.textContent = "通關密碼不正確。";\n        return;\n      }\n      if (!name) {\n        el.loginMessage.textContent = "請先輸入姓名。";\n        return;\n      }\n\n      sessionStorage.setItem(SESSION_KEYS.accessPassed, "true");\n      upsertPlayer(name);\n      el.loginOverlay.classList.remove("show");\n      applyRange();\n    }',
    )
    text = replace_once(
        text,
        '      el.loginBtn.addEventListener("click", submitLogin);\n      el.loginName.addEventListener("keydown", (event) => {\n        if (event.key === "Enter") submitLogin();\n      });',
        '      el.loginBtn.addEventListener("click", submitLogin);\n      el.loginPassword.addEventListener("keydown", (event) => {\n        if (event.key === "Enter") submitLogin();\n      });\n      el.loginName.addEventListener("keydown", (event) => {\n        if (event.key === "Enter") submitLogin();\n      });',
    )

    INDEX_PATH.write_text(text, encoding="utf-8")
    print("index.html upgraded")


if __name__ == "__main__":
    main()
