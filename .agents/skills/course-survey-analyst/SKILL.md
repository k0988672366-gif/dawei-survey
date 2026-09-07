---
name: course-survey-analyst
description: >-
  Comprehensive guide and operational runbook for the Course Completion Multi-Agent AI Analyst & Reward Course System. Use this skill whenever developing, maintaining, debugging, deploying, or answering questions about the course survey system, including multi-agent orchestration, dynamic quote walls, real-time data sync, Gemini AI model integration, and cloud deployment.
---

# 班級結業分析師 Multi-Agent AI 系統開發與維運技能手冊 (Course Survey Analyst Skill)

本技能手冊（Skill）總結了「**班級結業問卷多代理 AI 分析師 ✕ 線上單元課兌換系統**」從無到有、歷經多輪真實用戶反饋與系統升級的完整架構、核心準則、排錯手冊與維運指引。

---

## 一、 系統總覽與定位

本系統是一套專為教育培訓機構、線上實體雙軌學院、大師專案課程設計的**端到端結業交付閉環系統**：
1. **學員填答端**：90 秒極速填寫（起點、痛點、講師/助教評鑑、NPS、質化建議），完成即送客製化線上單元課，引導加入客服/班主任開通，大幅提高填答率與黏著度。
2. **多代理人協同分析大腦（7 大 Agents）**：資料檢驗 ➜ 量化/NPS ➜ 質化情緒 ➜ 起點痛點歸因 ➜ 教學行動矩陣 ➜ 結業審查報告書 ➜ 即席諮詢顧問。
3. **管理端儀表板**：班級切換、AI 課綱分析問卷生成、學員兌換名冊（電話/LINE ID 一鍵複製）、即時雙向數據同步、高階報告列印/匯出。

---

## 二、 使用者核心準則與迭代修正規範 (User Commandments)

在開發與後續維護此系統時，必須嚴格遵守以下由使用者實際反饋提煉出的**六大鐵律**：

### 1. 真數據驅動，絕不使用死板靜態範例 (Genuine Data-Driven)
* **使用者原話**：「*我看內容好像都是固定的？包含學員金句牆與行動矩陣，應該要對應學員填寫完後給出的回饋去做調整才對！我現在的版本不是測試版，而是一個完整、且功能性都是我要的版本！*」
* **開發鐵律**：
  * **金句牆（Quote Wall）**：無文字反饋時明確顯示「等待學員提交金句」，有反饋時由 Agent 3 動態篩選高價值真實回饋；**嚴禁使用假資料預填**。
  * **教學覆盤與行動矩陣（Action Matrix）**：必須由學員真實投票出的「第一名卡關點」與「各起點滿意度落差」動態運算產出「即刻速贏 / 次期優化 / 長期架構」，絕不可使用寫死的靜態文字。

### 2. 即時雙向無感同步 (Real-Time Auto-Sync)
* **使用者原話**：「*我請同事填寫完，後台卻沒有跳出來資料～ 他不能自動就同步嗎？*」
* **開發鐵律**：
  * 後台必須常態啟用自動同步機制（`/api/sync-responses`，每 10 秒自動輪詢雲端新提交的問卷），並提供即時綠色同步指示燈與手動「立即同步」按鈕。

### 3. 多班級獨立與 AI 課綱自適應 (Multi-Class & Syllabus AI)
* **開發鐵律**：
  * 支援多班級管理，各班級問卷資料庫與報告完全隔離。
  * 支援上傳 PDF 課綱或貼上大綱文字，由 AI 自動提取講師、章節、卡關選項與贈課清單，秒級生成專屬問卷。

### 4. 高可用大模型調度：零 429 報錯與毫秒容錯鏈 (High-Availability LLM)
* **使用者原話**：「*他回答得非常奇怪很不ai*」、「*回答又是很怪的*」
* **開發鐵律**：
  * 免費版 Google AI Studio API Key 在頂規模型（如 `Gemini 3.7 Flash`）極易觸發每分鐘請求上限（HTTP 429）。
  * **主力模型必須優先採用高額度、極速版 `gemini-3.5-flash-lite`**（0.8 秒反應、零 429 報錯）。
  * 必須配置自動容錯輪詢鏈：`[gemini-3.5-flash-lite ➜ gemini-3.5-flash ➜ gemini-3.7-flash]`，任何單一模型失敗時毫秒無感切換。

### 5. 離線保底精準分類，拒絕答非所問 (Context-Aware Fallback)
* **開發鐵律**：
  * 離線保底規則必須精準辨識意圖：
    * 詢問「節慶祝賀（中秋、端午、新年、連假）」➜ 產出節慶祝賀文案。
    * 詢問「停課、請假、補課、調課」➜ 產出班級調課通知講稿。
    * 僅在明確詢問「結業、完課、畢業」時才產出結業致謝信。
    * **絕不把「中秋文案」誤套成「結業感謝詞」！**

### 6. 全球跨裝置存取與資訊安全 (Cross-Device & Privacy)
* **使用者原話**：「*我想確認，這個網站後台是只能我這台電腦使用嗎？ 我用別的電腦登入都無法。*」
* **開發鐵律**：
  * 本地開發端點 `http://localhost:8080/admin` 僅限本機開發測試。
  * 外出、手機或遠端電腦，一律指引使用 Render 雲端公開網址：`https://dawei-survey.onrender.com/admin`。
  * 安全保護：管理後台採用 HTTP Basic Auth（預設帳號 `admin` / 密碼 `art888`），保護學員電話與 LINE ID。
  * API Key 安全：金鑰僅寫在本地 `.env`（Git 忽略）與 Render 雲端環境變數，嚴禁明文寫入程式庫。

---

## 三、 專案核心代碼結構與路徑

```
結業分析師 ai agent/
├── app.py                     # Streamlit 備用展示端
├── main.py                    # 主 CLI 進入點（--serve / --analyze）
├── survey_server.py           # 原生輕量 HTTP/REST 伺服器 (8080)
├── config.py                  # 全域設定、路徑、帳密與 Gemini 金鑰載入
├── render.yaml / Procfile     # Render 雲端部署配置
├── static/
│   ├── index.html             # 學員手機填答端前端（LINE 友善、極速體驗）
│   └── dashboard.html         # 管理後台前端（視覺化圖表、即席諮詢、名冊導出）
├── core/
│   ├── state.py               # 核心資料狀態 SurveyAnalysisState
│   ├── orchestrator.py        # 7 大代理人排程流水線 SurveyOrchestrator
│   ├── llm_client.py          # Gemini API ✕ 多模型容錯雙引擎客戶端
│   └── agents/
│       ├── data_agent.py      # Agent 1: 資料檢驗
│       ├── quant_agent.py     # Agent 2: 量化與 NPS
│       ├── text_agent.py      # Agent 3: 質化情緒與真聲金句牆
│       ├── corr_agent.py      # Agent 4: 起點痛點交叉歸因
│       ├── strategy_agent.py  # Agent 5: 動態教學行動矩陣
│       ├── report_agent.py    # Agent 6: 結業審查診斷報告書
│       ├── chat_agent.py      # Agent 7: 即席諮詢顧問
│       └── syllabus_agent.py  # AI 課綱智慧解析與問卷生成器
└── data/                      # 班級問卷 CSV 與 classes_config.json
```

---

## 四、 快速啟動與驗證指令 (Cheatsheet)

### 1. 本地啟動完整服務（含管理端與填答端）
```bash
python3 main.py --serve
```
* 本機填答網址：`http://localhost:8080/`
* 本機管理後台：`http://localhost:8080/admin`（帳號 `admin` / 密碼 `art888`）

### 2. 驗證大模型連線與問答
```bash
python3 -c "
from core.orchestrator import SurveyOrchestrator
from core.state import SurveyAnalysisState
orchestrator = SurveyOrchestrator()
state = SurveyAnalysisState(course_name='2D動畫設計班', teacher_name='Zorioz')
ans = orchestrator.ask_advisor('中秋節祝賀文案 50字內', state)
print('回答結果:', ans)
"
```

### 3. 雲端遠端檢查指令
```bash
# 檢查雲端健康狀態
curl -I https://dawei-survey.onrender.com/
# 測試雲端管理員認證
curl -s -u admin:art888 https://dawei-survey.onrender.com/admin | head -n 10
```

---

## 五、 詳細參考文檔 (References)

進一步深入閱讀各專題技術細節：
* [使用者需求與迭代修正全紀錄 (Changelog)](./references/user-requirements-changelog.md)
* [7 大 AI 代理人架構與資料流規範 (Agent Architecture)](./references/agent-architecture.md)
* [雲端部署、環境變數與跨裝置操作手冊 (Cloud & Deployment Guide)](./references/cloud-deployment-guide.md)
