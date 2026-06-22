from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")

replacements = [
    ('<input type="password" id="loginPassword" maxlength="20" placeholder="請輸入密語" />',
     '<input type="password" id="loginPassword" maxlength="20" placeholder="請輸入通關密語" />\n        <label>\n          角色代碼\n          <input type="text" id="adminCode" maxlength="20" placeholder="Nutanix 為管理者" />\n        </label>'),
    ('<p>先輸入通關密碼與姓名。只要密碼正確，系統就會在這台電腦裡記住目前使用者與累積分數，之後同一個分頁可直接繼續使用。</p>',
     '<p>先輸入通關密語與姓名。只要密語正確，系統就會在這台電腦裡記住目前使用者與累積分數，之後同一個分頁可直接繼續使用。</p>'),
    ('<div class="meta-grid">\n                <div class="meta-card">\n                  <small>編號</small>\n                  <strong id="studyId">1</strong>\n                </div>\n                <div class="meta-card">\n                  <small>詞性</small>\n                  <strong id="studyPos">名詞</strong>\n                </div>\n                <div class="meta-card">\n                  <small>KK 音標</small>\n                  <strong id="studyKK">əˈdʌlt</strong>\n                </div>\n                <div class="meta-card">\n                  <small>英文發音</small>\n                  <strong>en-US</strong>\n                </div>\n              </div>',
     '<div class="meta-grid">\n                <div class="meta-card">\n                  <small>編號 / 詞性 / 音標</small>\n                  <strong id="studyMeta">1 / 名詞 / əˈdʌlt</strong>\n                </div>\n                <div class="meta-card">\n                  <small>中文提示</small>\n                  <strong id="studyMeaning">成年人</strong>\n                </div>\n              </div>'),
]

for old, new in replacements:
    if old not in text and new not in text:
        raise SystemExit(f"missing snippet: {old[:60]}")
    text = text.replace(old, new)

text = text.replace(
    '      currentUser: "summer2000king.currentUser",\n      autoSpeak: "summer2000king.autoSpeak"\n    };\n\n    const ACCESS_PASSWORD = "541115";',
    '      currentUser: "summer2000king.currentUser",\n      autoSpeak: "summer2000king.autoSpeak",\n      history: "summer2000king.history",\n      admin: "summer2000king.admin"\n    };\n\n    const ACCESS_PASSWORD = window.__APP_PASSWORD__ || "541115";\n    const ADMIN_CODE = "Nutanix";'
)

text = text.replace(
    '      studyId: document.getElementById("studyId"),\n      studyPos: document.getElementById("studyPos"),\n      studyKK: document.getElementById("studyKK"),',
    '      studyMeta: document.getElementById("studyMeta"),'
)

text = text.replace(
    '      quizItem: null,\n      quizLocked: false,\n      autoSpeak: false,\n      voices: []',
    '      quizItem: null,\n      quizLocked: false,\n      autoSpeak: false,\n      soundOn: true,\n      challengeHistory: safeReadJSON(STORAGE_KEYS.history, []),\n      isAdmin: sessionStorage.getItem(STORAGE_KEYS.admin) === "true",\n      voices: []'
)

text = text.replace(
    '      currentUserScore: document.getElementById("currentUserScore"),',
    '      currentUserScore: document.getElementById("currentUserScore"),\n      scoreHistory: document.getElementById("scoreHistory"),'
)

text = text.replace(
    '      quizSpeakBtn: document.getElementById("quizSpeakBtn"),',
    '      quizSpeakBtn: document.getElementById("quizSpeakBtn"),\n      soundToggle: document.getElementById("soundToggle"),\n      fillToggle: document.getElementById("fillToggle"),\n      historyToggle: document.getElementById("historyToggle"),\n      resetScoresBtn: document.getElementById("resetScoresBtn"),'
)

text = text.replace(
    '      el.currentUserName.textContent = state.currentUser || "未登入";\n      el.currentUserScore.textContent = record ? String(record.score) : "0";',
    '      el.currentUserName.textContent = state.currentUser ? state.currentUser + (state.isAdmin ? " 👑" : "") : "未登入";\n      el.currentUserScore.textContent = record ? String(record.score) : "0";'
)

text = text.replace(
    '      const players = getPlayers()\n        .sort((a, b) => (b.score - a.score) || (a.updatedAt - b.updatedAt));',
    '      const players = getPlayers().sort((a, b) => (b.score - a.score) || (a.updatedAt - b.updatedAt));'
)

text = text.replace(
    '      el.leaderboardList.innerHTML = players.slice(0, 12).map((player, index) => `',
    '      el.leaderboardList.innerHTML = players.slice(0, 12).map((player, index) => `'
)

text = text.replace(
    '            <strong>${escapeHtml(player.name)}</strong>',
    '            <strong>${escapeHtml(player.name)}${index === 0 ? " 👑" : ""}</strong>'
)

text = text.replace(
    '      target.score += points;\n      target.updatedAt = Date.now();\n      savePlayers(players);\n      renderCurrentUser();\n      renderLeaderboard();',
    '      target.score += points;\n      target.history = target.history || [];\n      target.history.push({ at: Date.now(), delta: points, total: target.score });\n      target.updatedAt = Date.now();\n      savePlayers(players);\n      state.challengeHistory = safeReadJSON(STORAGE_KEYS.history, []);\n      state.challengeHistory.push({ name: state.currentUser, delta: points, total: target.score, at: Date.now() });\n      localStorage.setItem(STORAGE_KEYS.history, JSON.stringify(state.challengeHistory));\n      renderCurrentUser();\n      renderLeaderboard();\n      renderScoreHistory();'
)

text = text.replace(
    '        el.studyProgress.textContent = "目前沒有單字";\n        el.studyWord.textContent = "請先設定有效範圍";\n        el.studyMeaning.textContent = "系統找不到這段編號的單字。";\n        el.studyId.textContent = "-";\n        el.studyPos.textContent = "-";\n        el.studyKK.textContent = "-";',
    '        el.studyProgress.textContent = "目前沒有單字";\n        el.studyWord.textContent = "請先設定有效範圍";\n        el.studyMeaning.textContent = "系統找不到這段編號的單字。";\n        el.studyMeta.textContent = "- / - / -";'
)

text = text.replace(
    '      el.studyProgress.textContent = `第 ${state.studyIndex + 1} / ${state.filteredWords.length} 張`;\n      el.studyWord.textContent = item.word;\n      el.studyMeaning.textContent = item.meaning;\n      el.studyId.textContent = String(item.id);\n      el.studyPos.textContent = item.pos;\n      el.studyKK.textContent = item.kk || "待補";',
    '      el.studyProgress.textContent = `第 ${state.studyIndex + 1} / ${state.filteredWords.length} 張`;\n      el.studyWord.textContent = item.word;\n      el.studyMeaning.textContent = item.meaning;\n      el.studyMeta.textContent = `${item.id} / ${item.pos} / ${item.kk || "待補"}`;'
)

text = text.replace(
    '      el.quizFeedback.className = "feedback";\n\n      el.quizOptions.innerHTML = options.map((meaning) => `\n        <button class="option-btn" data-meaning="${escapeHtml(meaning)}">${escapeHtml(meaning)}</button>\n      `).join("");',
    '      el.quizFeedback.className = "feedback";\n\n      el.quizOptions.innerHTML = options.map((meaning, index) => `\n        <button class="option-btn" data-meaning="${escapeHtml(meaning)}">${index + 1}. ${escapeHtml(meaning)}</button>\n      `).join("");'
)

text = text.replace(
    '      const name = el.loginName.value.trim();\n      const passed = sessionStorage.getItem(SESSION_KEYS.accessPassed) === "true";\n      const password = el.loginPassword.value.trim();\n\n      if (!passed && password !== ACCESS_PASSWORD) {\n        el.loginMessage.textContent = "通關密碼不正確。";\n        return;\n      }\n      if (!name) {\n        el.loginMessage.textContent = "請先輸入姓名。";\n        return;\n      }\n\n      sessionStorage.setItem(SESSION_KEYS.accessPassed, "true");\n      upsertPlayer(name);\n      el.loginOverlay.classList.remove("show");\n      applyRange();',
    '      const name = el.loginName.value.trim();\n      const passed = sessionStorage.getItem(SESSION_KEYS.accessPassed) === "true";\n      const password = el.loginPassword.value.trim();\n      const adminCode = el.adminCode?.value?.trim() || "";\n\n      if (!passed && password !== ACCESS_PASSWORD) {\n        el.loginMessage.textContent = "通關密語不正確。";\n        return;\n      }\n      if (!name) {\n        el.loginMessage.textContent = "請先輸入姓名。";\n        return;\n      }\n\n      state.isAdmin = adminCode === ADMIN_CODE;\n      sessionStorage.setItem(SESSION_KEYS.accessPassed, "true");\n      sessionStorage.setItem(STORAGE_KEYS.admin, String(state.isAdmin));\n      upsertPlayer(name);\n      el.loginOverlay.classList.remove("show");\n      applyRange();'
)

text = text.replace(
    '      el.loginPassword.value = "";\n      el.loginName.value = force && savedUser ? savedUser : "";\n      el.loginMessage.textContent = "";\n      el.loginOverlay.classList.add("show");\n      setTimeout(() => (passed ? el.loginName : el.loginPassword).focus(), 60);',
    '      el.loginPassword.value = "";\n      if (el.adminCode) el.adminCode.value = "";\n      el.loginName.value = force && savedUser ? savedUser : "";\n      el.loginMessage.textContent = "";\n      el.loginOverlay.classList.add("show");\n      setTimeout(() => (passed ? el.loginName : el.loginPassword).focus(), 60);'
)

text = text.replace(
    '      el.loginBtn.addEventListener("click", submitLogin);',
    '      el.loginBtn.addEventListener("click", submitLogin);'
)

insert_after = '      el.quizSpeakBtn.addEventListener("click", () => {\n        if (state.quizItem) speakWord(state.quizItem.word);\n      });\n'
addition = '''      el.soundToggle.addEventListener("change", (event) => {
        state.soundOn = event.target.checked;
      });
      el.fillToggle.addEventListener("change", (event) => {
        state.fillMode = event.target.checked;
        renderQuizQuestion();
      });
      el.historyToggle?.addEventListener("change", renderScoreHistory);
      el.resetScoresBtn?.addEventListener("click", resetAllScores);
      document.addEventListener("keydown", handleKeyboard);

'''
text = text.replace(insert_after, insert_after + addition)

text = text.replace(
    '      renderLeaderboard();\n      renderCurrentUser();\n      applyRange();\n      showLogin();',
    '      renderLeaderboard();\n      renderCurrentUser();\n      renderScoreHistory();\n      applyRange();\n      showLogin();'
)

extra = '''
    function renderScoreHistory() {
      if (!el.scoreHistory) return;
      const entries = [...state.challengeHistory].slice(-20).reverse();
      el.scoreHistory.innerHTML = entries.length ? entries.map((item) => `<div class="empty-box">${escapeHtml(item.name)} +${item.delta} => ${item.total}</div>`).join("") : '<div class="empty-box">還沒有挑戰紀錄。</div>';
    }

    function resetAllScores() {
      if (!state.isAdmin) return;
      const players = getPlayers().map((player) => ({ ...player, score: 0, updatedAt: Date.now(), history: [] }));
      savePlayers(players);
      localStorage.removeItem(STORAGE_KEYS.history);
      state.challengeHistory = [];
      renderCurrentUser();
      renderLeaderboard();
      renderScoreHistory();
    }

    function handleKeyboard(event) {
      if (event.key === "ArrowLeft") moveStudyCard(-1);
      if (event.key === "ArrowRight") moveStudyCard(1);
      if (event.key === " ") {
        event.preventDefault();
        const item = state.filteredWords[state.studyIndex];
        if (item) speakWord(item.word);
      }
    }

    function renderQuizQuestion() {
      loadQuizQuestion();
    }
'''
text = text.replace('    function init() {', extra + '\n    function init() {')

text = text.replace(
    '      state.autoSpeak = localStorage.getItem(STORAGE_KEYS.autoSpeak) === "true";\n      el.autoSpeakToggle.checked = state.autoSpeak;',
    '      state.autoSpeak = localStorage.getItem(STORAGE_KEYS.autoSpeak) === "true";\n      el.autoSpeakToggle.checked = state.autoSpeak;\n      state.soundOn = true;'
)

text = text.replace(
    '      el.autoSpeakToggle.addEventListener("change", (event) => {\n        state.autoSpeak = event.target.checked;\n        localStorage.setItem(STORAGE_KEYS.autoSpeak, String(state.autoSpeak));\n      });',
    '      el.autoSpeakToggle.addEventListener("change", (event) => {\n        state.autoSpeak = event.target.checked;\n        localStorage.setItem(STORAGE_KEYS.autoSpeak, String(state.autoSpeak));\n      });'
)

path.write_text(text, encoding="utf-8")
print("feature upgrade complete")
