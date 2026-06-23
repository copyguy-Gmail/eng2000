# 暑期 2000 單字王 APK 打包說明

這個目錄是 Android WebView 離線版，會載入 `app/src/main/assets/index.html`。

## 使用 Android Studio 打包

1. 安裝 Android Studio。
2. 開啟 `android-apk` 這個資料夾。
3. 等待 Gradle Sync 完成。
4. 選單執行 `Build > Build Bundle(s) / APK(s) > Build APK(s)`。
5. APK 會產生在 `android-apk/app/build/outputs/apk/debug/app-debug.apk`。

## 更新網頁內容

每次修改根目錄的 `index.html` 後，重新複製到：

```powershell
Copy-Item ..\index.html .\app\src\main\assets\index.html -Force
```

再重新 Build APK。

## 單機版注意事項

- 分數會存在 Android WebView 的本機儲存空間。
- 英文發音會優先使用 Android 原生 TextToSpeech。
- 若有設定遠端排行榜 API，APK 也可以連網同步分數；若沒有設定，會完全單機運作。
