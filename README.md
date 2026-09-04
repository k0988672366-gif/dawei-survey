# 🎨 劉大維畫室直播課程 ✕ 班級結業問卷多代理協同 AI Agent 系統

專為教育機構、設計學院、線上訓練營量身打造的**「端到端結業問卷閉環系統」**。

徹底解決傳統問卷在 **LINE 群發送時填答率低、Google 表單手機體驗差、SurveyCake 免費版無法自訂下載按鈕（收費昂貴）** 等痛點。本專案提供：
1. **📱 前台：專屬手機端高顏值問卷 Web App**（免登入、90秒快填、完填立即解鎖下載【大維老師私房筆刷包 & 課堂速查手冊】）。
2. **🤖 後台：6+1 專業多代理協同 AI 分析師**（資料檢驗 ➔ 量化與 NPS ➔ 質化情緒金句 ➔ 交叉歸因 ➔ 教學行動矩陣 ➔ 總協調審查報告 ➔ AI 即席諮詢顧問）。

---

## 🌟 核心特點與優勢

### 1. 徹底解決 LINE 群填寫率低的「三大秘密武器」
* **⏱ 90 秒手機極速填答**：專為手機螢幕設計的滑動卡片與大按鈕，去除所有令人反感的「設備型號」雜題，大幅降低填答阻力。
* **🎁 完課好禮價值交換 (WIIFM)**：學員點擊「提交」後，頁面**立即跳出解鎖彈窗**，一鍵下載【大維老師私房筆刷包 & 技法速查表】！
* **🔒 零個資防備**：無需強制填寫電話，僅需稱呼與 Email（用於接收禮包），大幅提升學員填寫意願。

### 2. 6+1 專業多代理協同分析陣容 (Multi-Agent Squad)
* **Agent 1: 資料檢驗代理 (Inspector)**：自動清洗欄位、檢查填答覆蓋率與異常反饋。
* **Agent 2: 量化統計代理 (Quant)**：精算大維老師、課綱、助教三大教學維度均分，並計算標準 NPS 淨推薦值。
* **Agent 3: 質化情緒代理 (Text Miner)**：高精度萃取學員給老師的原聲口碑金句與教學改進警訊。
* **Agent 4: 交叉歸因代理 (Correlation)**：深掘「學員起點（零基礎 vs 有經驗）」與「卡關點（光影/混色/節奏）」之關聯。
* **Agent 5: 教學策略代理 (Strategist)**：制定 Eisenhower 優化行動矩陣（即刻速贏、次期優化、長線課綱）、講師覆盤 3 問與助教 SOP。
* **Agent 6: 總協調審查代理 (Chief Synthesizer)**：自動編制 C-Level 高階《結業問卷綜合診斷報告書》（可一鍵列印/另存 PDF）。
* **Agent 7: 問卷即席諮詢顧問 (Chat Advisor)**：支援以自然語言提問（例如：「零基礎學員主要卡關在哪裡？」）。

### 3. 雙推理引擎架構
* **Google Gemini 2.5 雲端大模型**：配置 `GEMINI_API_KEY` 時自動啟用深度語意推理。
* **智慧本機啟發式引擎**：即使未設定 API Key，也能基於統計分佈與教育規則產出專業分析，**100% 開箱即用！**

---

## 🚀 快速開始 (Quick Start)

本系統內建極速 HTTP 伺服器，**無需安裝額外繁重套件**，使用 Python 內建環境即可秒開！

### 1. 啟動伺服器（學員問卷 ＋ 管理後台）
在終端機進入專案目錄執行：

```bash
python3 main.py --serve
```

啟動後將看到：
* 📱 **學員手機端填答網址**：`http://localhost:8080/`
* 📊 **多代理 AI 分析管理儀表板**：`http://localhost:8080/admin`
* 📑 **可直接列印/存為 PDF 的高階診斷報告**：`http://localhost:8080/report/html`
* 🎁 **筆刷禮包下載測試端點**：`http://localhost:8080/download/brushes`

---

### 2. 終端機一鍵批次分析（CLI 模式）
若想直接在命令列執行 6 大代理人協同分析並匯出報告：

```bash
python3 main.py --analyze
```

執行後會自動在終端機顯示進度條、NPS 指標，並匯出：
* `data/final_report.md` (Markdown 報告)
* `data/final_report.html` (美觀列印版 HTML 報告)

---

### 3. (選用) 啟動 Streamlit 視覺化儀表板
若您的環境已安裝 Streamlit 與 Plotly：

```bash
python3 -m pip install -r requirements.txt
streamlit run app.py
```

---

## 📲 如何在 LINE 群推播並引爆填答率？

請助教或老師在直播課程即將結束時（最後 10 分鐘），在 LINE 群發送以下文案：

```text
🎨【劉大維畫室】結業啦！領取老師的完課祕密禮物 🎁

各位同學辛苦了！跟著大維老師完成了這幾週的直播練習，大家都超級棒的！👏

為了能持續端出最適合大家的繪畫課，想邀請大家花「90 秒」給我們最真實的想法～

👉 快速填寫連結：http://[您的主機IP或網址]:8080/
⏱ 只要 90 秒（手機超好點選，免登入）
🎁 填完送【大維老師私房筆刷包＋課堂技法速查表】（送出後立刻點擊下載）

大家的每句回饋，大維老師跟助教都會一條條親自看喔！❤️
填完可以在群裡回傳「已領取筆刷」，讓助教知道你完成囉～
```

---

## ⚙️ 如何替換為真實的 Google Drive 筆刷連結？

打開專案根目錄下的 `config.py`，找到：

```python
# 問卷完課禮物下載設定
GIFT_DOWNLOAD_URL = "https://drive.google.com/drive/folders/您的真實雲端硬碟分享連結"
```

將其修改為您的 Google Drive 連結後儲存，學員在手機送出問卷後，點擊下載按鈕就會自動跳轉到您的 Google Drive 領取筆刷包！

---

## 📂 專案目錄結構說明

```
結業分析師 ai agent/
├── survey_server.py           # 核心伺服器 (提供學員手機問卷、管理儀表板、報告匯出與下載)
├── main.py                    # 系統 CLI 入口 (支援 --serve, --analyze, --reset-sample)
├── app.py                     # Streamlit 進階視覺化儀表板
├── config.py                  # 課程名稱、機構、Google Drive 禮包連結設定
├── requirements.txt           # 依賴清單
├── README.md                  # 本操作手冊
├── static/                    # 前端靜態檔案
│   ├── index.html             # 學員手機端問卷（支援卡片點選、NPS 評分與解鎖禮包）
│   ├── style.css              # 藝術畫室深色質感主題樣式
│   ├── app.js                 # 前端互動邏輯與表單 AJAX 提交
│   └── dashboard.html         # 視覺化多代理人管理儀表板 (含圖表與 AI 諮詢)
├── core/                      # 6+1 多代理協同引擎
│   ├── state.py               # 共享狀態資料類別 (SurveyAnalysisState)
│   ├── llm_client.py          # Gemini API + 本機啟發式雙引擎
│   ├── orchestrator.py        # 代理人調度中樞
│   └── agents/                # 7 大專業代理人實現
├── data/                      # 資料庫
│   ├── survey_responses.csv   # 學員填答儲存檔案
│   ├── sample_generator.py    # 擬真範例資料生成器
│   └── brushes_sample.zip     # 內建示範禮包
└── utils/                     # 圖表與匯出模組
    ├── charts.py              # 圖表數據格式化
    └── exporter.py            # Markdown 與專業 HTML 報告匯出器
```
