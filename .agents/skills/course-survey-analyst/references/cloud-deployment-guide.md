# 結業問卷分析師：雲端部署、環境變數與跨裝置操作手冊

本手冊提供在 Render 雲端平台部署、維護、設定環境變數與跨裝置存取時的完整標準作業程序（SOP）。

---

## 一、 雲端架構與存取端點

| 項目 | 網址 / 端點 | 權限要求 | 說明 |
| :--- | :--- | :--- | :--- |
| **學員填答端** | `https://dawei-survey.onrender.com/` | 公開（免密碼） | 適合發佈至 LINE 班群、學員社團供手機填答 |
| **管理後台端** | `https://dawei-survey.onrender.com/admin` | Basic Auth | 視覺化多代理人儀表板、名冊兌換與報告匯出 |
| **診斷報告書** | `https://dawei-survey.onrender.com/report/html` | Basic Auth | 適合直接列印（A4 PDF）或分享給教務長審閱 |
| **本機測試端** | `http://localhost:8080/admin` | Basic Auth | 僅限開發本機電腦使用 |

---

## 二、 管理後台安全登入憑證 (HTTP Basic Auth)

為嚴格保護學員電話、LINE ID 與個人填答不外洩，進入 `/admin` 時瀏覽器會自動彈出原生安全驗證框：
* **預設使用者名稱 (Username)**：`admin`
* **預設密碼 (Password)**：`art888`
* **自訂方式**：可在 `.env`（本機）或 Render 後台 `Environment Variables` 中設定 `ADMIN_USERNAME` 與 `ADMIN_PASSWORD`。

---

## 三、 Render 雲端後台設定 Gemini API Key (SOP)

GitHub 安全機制會攔截任何含有 API Key 的程式碼推送，因此金鑰必須手動配置於 Render 環境變數：

1. 登入 [Render Dashboard](https://dashboard.render.com/)。
2. 在 **Projects** 頁面點擊 **`My project`**。
3. 點選您的 Web Service 服務：**`dawei-survey`**。
4. 點選左側選單的 **`Environment`**。
5. 點擊 **`Add Environment Variable`**：
   * **Key**：`GEMINI_API_KEY`
   * **Value**：填入您的 Google AI Studio 金鑰（例如 `AQ.Ab8RN6...`）
   * *(選填)* **Key**：`GEMINI_MODEL`，**Value**：`gemini-3.5-flash-lite`
6. 點擊頁面底部的 **`Save Changes`**。
7. 儲存後，Render 會自動重新部署生效（約 1~2 分鐘）。

---

## 四、 跨裝置操作常見疑難雜症 (FAQ)

### Q1：我在公司或別台電腦輸入 `http://localhost:8080/admin` 卻無法連線？
* **原因**：`localhost` 代表「當前這台電腦本身」，在別台電腦輸入代表連線到該台電腦，上面並沒有執行伺服器。
* **解法**：在任何外出電腦、筆電或手機上，請一律使用雲端網址：  
  `https://dawei-survey.onrender.com/admin`

### Q2：在別台電腦初次打開網址時，轉圈圈讀取很久（約 30~50 秒）？
* **原因**：Render 免費版伺服器在無人造訪 15 分鐘後會進入省電休眠模式。
* **解法**：初次喚醒（Cold Start）需約 30~50 秒，只要等待主機開機完成即可正常操作，後續請求皆為秒開。

### Q3：學員填寫後，我的電腦如何同步？
* **機制**：後台管理端已內建 10 秒自動輪詢同步機制（`/api/sync-responses`），學員填寫後雲端與本地端皆會自動刷新呈現。
