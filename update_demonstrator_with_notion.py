import json

# 1. Load updated preset_slots.json
with open("static/preset_slots.json", "r", encoding="utf-8") as f:
    preset_data = json.load(f)

preset_json_str = json.dumps(preset_data, ensure_ascii=False)

html_template = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DATE 線上直播學院｜2027 年度排課落點示範（全師資資料庫互動調配系統）</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700;800&display=swap" rel="stylesheet">

<style>
  :root {
    --primary: #2563eb;
    --primary-dark: #1d4ed8;
    --primary-bg: #eff6ff;
    --green: #16a34a;
    --green-bg: #f0fdf4;
    --amber: #ea580c;
    --amber-bg: #fff7ed;
    --purple: #9333ea;
    --purple-bg: #faf5ff;
    --text-main: #0f172a;
    --text-sub: #334155;
    --text-muted: #64748b;
    --border: #cbd5e1;
    --border-light: #e2e8f0;
    --bg: #f8fafc;
    --surface: #ffffff;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'Noto Sans TC', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background-color: var(--bg);
    color: var(--text-main);
    line-height: 1.5;
    padding: 24px;
    -webkit-font-smoothing: antialiased;
  }

  .page-container {
    max-width: 1540px;
    margin: 0 auto;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    overflow: hidden;
  }

  /* Header banner */
  .header-banner {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #1e3a8a 100%);
    color: #ffffff;
    padding: 26px 32px;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 16px;
    border-bottom: 3px solid #3b82f6;
  }

  .header-title-group h1 {
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -0.02em;
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
  }

  .tag-live {
    font-size: 11px;
    background: #ef4444;
    color: white;
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 700;
    text-transform: uppercase;
  }

  .tag-interactive {
    font-size: 11px;
    background: #0284c7;
    color: white;
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 700;
  }

  .tag-teachers {
    font-size: 11px;
    background: #10b981;
    color: white;
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 700;
  }

  .header-title-group p {
    color: #94a3b8;
    font-size: 13.5px;
    margin-top: 8px;
    max-width: 900px;
    line-height: 1.6;
  }

  .header-title-group p strong {
    color: #f1f5f9;
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
  }

  .btn-action {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--primary);
    color: #ffffff;
    font-size: 13px;
    font-weight: 700;
    padding: 9px 16px;
    border-radius: 6px;
    border: none;
    cursor: pointer;
    text-decoration: none;
    transition: all 0.15s;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  }
  .btn-action:hover {
    background: var(--primary-dark);
    transform: translateY(-1px);
  }
  .btn-action.secondary {
    background: #ffffff;
    color: #334155;
    border: 1px solid var(--border);
  }
  .btn-action.secondary:hover {
    background: #f1f5f9;
    border-color: #94a3b8;
  }
  .btn-action.green {
    background: var(--green);
  }
  .btn-action.green:hover {
    background: #15803d;
  }

  /* Toolbar */
  .control-toolbar {
    background: #f8fafc;
    padding: 14px 32px;
    border-bottom: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
  }

  .tab-group {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
  }

  .tab-pill {
    padding: 7px 14px;
    font-size: 12.5px;
    font-weight: 700;
    border-radius: 20px;
    border: 1px solid var(--border);
    background: #ffffff;
    color: var(--text-sub);
    cursor: pointer;
    transition: all 0.15s;
  }
  .tab-pill:hover {
    border-color: var(--primary);
    color: var(--primary);
  }
  .tab-pill.active {
    background: var(--primary);
    color: #ffffff;
    border-color: var(--primary);
    box-shadow: 0 2px 4px rgba(37,99,235,0.25);
  }

  .tools-group {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .tool-tag {
    font-size: 11.5px;
    font-weight: 600;
    color: var(--text-muted);
    background: #e2e8f0;
    padding: 4px 8px;
    border-radius: 4px;
  }

  /* Section Intro Banner */
  .section-intro {
    padding: 18px 32px 12px 32px;
    background: #ffffff;
    border-bottom: 1px solid var(--border-light);
  }
  .intro-sub {
    font-size: 12px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--primary);
    margin-bottom: 4px;
  }
  .intro-main {
    font-size: 17px;
    font-weight: 800;
    color: var(--text-main);
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
  }

  /* The Matrix Table */
  .matrix-wrap {
    padding: 24px 32px;
    overflow-x: auto;
    background: #ffffff;
  }

  table.matrix-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 10px;
    font-size: 12.5px;
  }

  table.matrix-table th {
    background: #f1f5f9;
    color: var(--text-main);
    font-weight: 800;
    padding: 12px 14px;
    border-radius: 8px;
    text-align: center;
    border: 1px solid var(--border);
    font-size: 13px;
  }
  table.matrix-table th.th-past {
    background: #fee2e2;
    border-color: #fca5a5;
    color: #991b1b;
  }
  table.matrix-table th.th-future {
    background: #e0f2fe;
    border-color: #bae6fd;
    color: #0369a1;
  }

  table.matrix-table td {
    vertical-align: top;
    padding: 0;
    width: 18%;
  }

  table.matrix-table td.slot-time-header {
    width: 10%;
    background: #f8fafc;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 14px 10px;
    text-align: center;
    display: table-cell;
    vertical-align: middle;
  }
  .time-day {
    font-size: 15px;
    font-weight: 800;
    color: #0f172a;
  }
  .time-hours {
    font-size: 11px;
    font-weight: 700;
    color: #64748b;
    margin-top: 4px;
    line-height: 1.35;
  }

  .slot-cell-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 120px;
  }

  .slot-cards-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
    flex-grow: 1;
  }

  /* Slot Card */
  .slot-card {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 10px 12px;
    min-height: 100px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all 0.15s;
    cursor: pointer;
    position: relative;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
  }
  .slot-card:hover {
    border-color: var(--primary);
    box-shadow: 0 4px 12px rgba(37,99,235,0.12);
    transform: translateY(-2px);
  }

  .slot-card.is-empty {
    background: #f8fafc;
    border: 1px dashed #cbd5e1;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    cursor: pointer;
    min-height: 90px;
  }
  .slot-card.is-empty:hover {
    background: #eff6ff;
    border-color: #3b82f6;
  }
  .empty-label {
    color: #94a3b8;
    font-size: 12px;
    line-height: 1.5;
  }

  .sc-top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 8px;
    margin-bottom: 6px;
  }

  .badge-level {
    font-size: 11px;
    font-weight: 800;
    padding: 2px 6px;
    border-radius: 4px;
    flex-shrink: 0;
  }
  .badge-a { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
  .badge-b { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
  .badge-c { background: #f3e8ff; color: #6b21a8; border: 1px solid #e9d5ff; }
  .badge-ocean { background: #cffafe; color: #0e7490; border: 1px solid #a5f3fc; }

  .course-name {
    font-size: 13.5px;
    font-weight: 800;
    color: var(--text-main);
    line-height: 1.35;
  }

  .card-btn-group {
    display: inline-flex;
    align-items: center;
    gap: 3px;
    flex-shrink: 0;
    margin-left: auto;
  }

  .btn-card-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 2px 6px;
    font-size: 11px;
    font-weight: 700;
    border-radius: 4px;
    border: 1px solid #cbd5e1;
    background: #f8fafc;
    color: #475569;
    cursor: pointer;
    transition: all 0.15s;
    line-height: 1.3;
  }
  .btn-card-icon.edit:hover {
    background: #eff6ff;
    border-color: #3b82f6;
    color: #1d4ed8;
  }
  .btn-card-icon.del {
    color: #dc2626;
    border-color: #fecaca;
    background: #fef2f2;
  }
  .btn-card-icon.del:hover {
    background: #fee2e2;
    border-color: #ef4444;
    color: #991b1b;
    transform: scale(1.05);
  }

  .btn-cell-add {
    width: 100%;
    margin-top: 6px;
    padding: 6px 10px;
    font-size: 11.5px;
    font-weight: 700;
    border: 1px dashed #94a3b8;
    border-radius: 6px;
    background: #f8fafc;
    color: #475569;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    transition: all 0.15s;
  }
  .btn-cell-add:hover {
    background: #eff6ff;
    border-color: #2563eb;
    color: #2563eb;
    box-shadow: 0 2px 6px rgba(37,99,235,0.12);
    border-style: solid;
  }

  .sc-mid {
    font-size: 12px;
    color: var(--text-sub);
    margin: 4px 0 6px 0;
  }
  .teacher-name { font-weight: 700; color: #1e293b; }
  .student-count { font-weight: 600; color: #64748b; }

  .sc-bottom {
    font-size: 11px;
    font-weight: 700;
    margin-top: auto;
  }
  .tag-past { color: #dc2626; }
  .tag-h1 { color: #16a34a; }
  .tag-h2 { color: #d97706; }
  .tag-empty { color: #94a3b8; font-weight: 500; }

  /* Footer Explanation Cards */
  .footer-notes {
    padding: 24px 32px 32px 32px;
    background: #f8fafc;
    border-top: 1px solid var(--border);
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }

  .note-box {
    background: #ffffff;
    border: 1px solid var(--border-light);
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
  }

  .note-box h3 {
    font-size: 15px;
    font-weight: 800;
    color: var(--text-main);
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .note-list {
    list-style: none;
    font-size: 12.5px;
    color: var(--text-sub);
    display: flex;
    flex-direction: column;
    gap: 10px;
    line-height: 1.6;
  }

  .note-list li {
    display: flex;
    align-items: flex-start;
    gap: 8px;
  }
  .note-list li strong {
    color: var(--text-main);
  }
  .bullet-icon {
    color: #ea580c;
    font-weight: 800;
    flex-shrink: 0;
  }
  .check-icon {
    color: #16a34a;
    font-weight: 800;
    flex-shrink: 0;
  }

  /* Modal Form */
  .modal-overlay {
    display: none;
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(15, 23, 42, 0.65);
    backdrop-filter: blur(4px);
    z-index: 9999;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }
  .modal-overlay.active {
    display: flex;
  }

  .modal-card {
    background: #ffffff;
    border-radius: 12px;
    max-width: 660px;
    width: 100%;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
    border: 1px solid var(--border);
    padding: 28px;
    position: relative;
    animation: modalIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  }
  @keyframes modalIn {
    from { opacity: 0; transform: scale(0.96); }
    to { opacity: 1; transform: scale(1); }
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border-light);
  }
  .modal-header h3 {
    font-size: 18px;
    font-weight: 800;
    color: var(--text-main);
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .modal-close {
    background: #f1f5f9;
    border: none;
    border-radius: 50%;
    width: 32px;
    height: 32px;
    font-size: 16px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-sub);
  }
  .modal-close:hover { background: #e2e8f0; }

  .form-group {
    margin-bottom: 16px;
  }
  .form-group label {
    display: block;
    font-size: 12.5px;
    font-weight: 700;
    color: var(--text-main);
    margin-bottom: 6px;
  }
  .form-group input, .form-group select, .form-group textarea {
    width: 100%;
    padding: 9px 12px;
    font-size: 13px;
    border: 1px solid var(--border);
    border-radius: 6px;
    font-family: inherit;
    outline: none;
    background: #ffffff;
  }
  .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
    border-color: var(--primary);
    box-shadow: 0 0 0 2px rgba(37,99,235,0.15);
  }

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }

  .modal-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    margin-top: 24px;
    padding-top: 16px;
    border-top: 1px solid var(--border-light);
  }

  /* Toast Notification */
  .toast {
    position: fixed;
    bottom: 28px;
    right: 28px;
    background: #0f172a;
    color: #ffffff;
    padding: 12px 20px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 700;
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.2);
    z-index: 10000;
    display: none;
    align-items: center;
    gap: 8px;
    border-left: 4px solid #16a34a;
  }
  .toast.active {
    display: flex;
  }

  /* Print Styles */
  @media print {
    body {
      padding: 0;
      background: #ffffff;
    }
    .page-container {
      border: none;
      box-shadow: none;
      max-width: 100%;
    }
    .header-actions, .control-toolbar, .edit-hover-icon, .modal-overlay, .toast, .btn-cell-add, .card-btn-group, .btn-card-icon {
      display: none !important;
    }
    .header-banner {
      padding: 16px 20px;
      border-bottom: 2px solid #2563eb;
    }
    .matrix-wrap {
      padding: 0 10px 10px 10px;
    }
    table.matrix-table {
      font-size: 11px;
    }
    .footer-notes {
      padding: 14px 10px;
      page-break-inside: avoid;
    }
    @page {
      size: landscape;
      margin: 8mm;
    }
  }
</style>
</head>
<body>

<div class="page-container">

  <!-- Header Banner -->
  <div class="header-banner">
    <div class="header-title-group">
      <h1>
        DATE 線上直播學院｜2027 年度排課落點示範
        <span class="tag-live">DATE 直播專屬</span>
        <span class="tag-interactive">可自訂選項互動版</span>
        <span class="tag-teachers">255 位在任師資庫已置入</span>
      </h1>
      <p>
        <strong>四大固定時段✕五大期別落點可視化調配系統：</strong>
        已完整整合 Notion 師資庫（255 位在任名師、<strong>《AI室內設計實務班》林延君團隊</strong>）。每個時段欄位均支援<strong>「➕ 新增課程」</strong>與每門課<strong>「🗑️ 刪除課程」</strong>，並提供師資專長智慧推薦與一鍵列印/匯出 PDF 報告。
      </p>
    </div>
    <div class="header-actions">
      <button class="btn-action green" onclick="window.print()">🖨️ 列印落點示範 / 另存 PDF</button>
      <button class="btn-action" onclick="saveSlotsToStorage()">💾 儲存自訂設定</button>
      <button class="btn-action secondary" onclick="resetToPreset()">🔄 還原預設落點</button>
      <a href="online_live_2027_master_plan.html" class="btn-action secondary">📊 回主規劃報告</a>
    </div>
  </div>

  <!-- Control toolbar -->
  <div class="control-toolbar">
    <div class="tab-group">
      <button class="tab-pill active" id="pill-anime" onclick="switchCategory('anime')">
        🎨【動漫、電繪與 Vtuber 生態鏈】怎麼排課
      </button>
      <button class="tab-pill" id="pill-design" onclick="switchCategory('design')">
        📐【視覺平面、AI 遊戲與數位音樂藍海】怎麼排課
      </button>
      <button class="tab-pill" id="pill-interior" onclick="switchCategory('interior')">
        🏛️【空間建築與 AI 室內設計】怎麼排課
      </button>
      <button class="tab-pill" id="pill-all" onclick="switchCategory('all')">
        🌐【全學系排課落點綜合檢視】
      </button>
    </div>
    <div class="tools-group">
      <span class="tool-tag">💡 點選欄位「➕ 新增課程」可隨時加開班級；點選卡片「🗑️」或「✏️」可直接刪除或設定課程</span>
    </div>
  </div>

  <!-- Section Title Intro -->
  <div class="section-intro">
    <div class="intro-sub">05 / 排課邏輯實務示範</div>
    <div class="intro-main">
      <span id="currentCategoryTitle">落點示範：DATE 線上直播【動漫、電繪與 Vtuber 生態鏈】怎麼排課</span>
      <span style="font-size: 13px; font-weight: 600; color: #64748b;" id="currentStats">全年度 14 班部署 ｜ 100% 符合產品部規範</span>
    </div>
  </div>

  <!-- The Interactive Matrix -->
  <div class="matrix-wrap" id="matrixContainer">
    <!-- Populated by JavaScript -->
  </div>

  <!-- Footer Explanations -->
  <div class="footer-notes">
    <div class="note-box">
      <h3>💡 怎麼看這張表（DATE 線上直播專屬固定時段特色）</h3>
      <ul class="note-list" id="notesListLeft">
        <!-- Populated by JS according to category -->
      </ul>
    </div>
    <div class="note-box">
      <h3>☑ 數據對齊指標（四維交叉驗證結果）</h3>
      <ul class="note-list" id="notesListRight">
        <li><span class="check-icon">☑</span> <div><strong>固定上課時段：</strong>平日一三(18:30-21:30)、二四(18:30-21:30)。</div></li>
        <li><span class="check-icon">☑</span> <div><strong>週末固定時段：</strong>六(14-17 / 18-21 休一小)、日(10-13 / 14-17 休一小)。</div></li>
        <li><span class="check-icon">☑</span> <div><strong>自主彈性規劃：</strong>每個欄位皆可隨時「➕ 新增課程」或「🗑️ 刪除課程」，調整即時存檔。</div></li>
        <li><span class="check-icon">☑</span> <div><strong>落實產品部規範：</strong>6 成大排定案 ＋ 4 成彈性保留池，直攻未消耗庫存。</div></li>
      </ul>
    </div>
  </div>

</div>

<!-- Modal: Edit Slot -->
<div class="modal-overlay" id="slotModal" onclick="closeModalOnOverlay(event)">
  <div class="modal-card">
    <div class="modal-header">
      <h3 id="modalTitle">⚙️ 設定排課落點</h3>
      <button class="modal-close" onclick="closeModal()">&times;</button>
    </div>

    <form id="slotForm" onsubmit="saveSlotForm(event)">
      <input type="hidden" id="editSlotId">

      <div class="form-group">
        <label>課程名稱（分類選單挑選或自訂輸入）</label>
        <select id="selectCourse" onchange="onCourseSelectChange(this)">
          <!-- Populated by JS -->
        </select>
        <input type="text" id="inputCustomCourse" placeholder="或自行輸入自訂課程名稱..." style="margin-top: 6px; display: none;">
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>固定排課時段</label>
          <select id="selectTime">
            <option value="一三">一三 18:30-21:30 (平日晚)</option>
            <option value="二四">二四 18:30-21:30 (平日晚)</option>
            <option value="六">週六 14:00-17:00 (休一小) 18:00-21:00 (6h)</option>
            <option value="日">週日 10:00-13:00 (休一小) 14:00-17:00 (6h)</option>
          </select>
        </div>

        <div class="form-group">
          <label>排課季度 / 期別</label>
          <select id="selectQuarter">
            <option value="2026_q4">2026 第 4 期 10-12月 (參考)</option>
            <option value="2027_q1">2027 第 1 期 1-3月 (H1 寒假/春季大排)</option>
            <option value="2027_q2">2027 第 2 期 4-6月 (H1 初夏/進階大排)</option>
            <option value="2027_q3">2027 第 3 期 7-9月 (H2 暑假加開/保留)</option>
            <option value="2027_q4">2027 第 4 期 10-12月 (H2 秋季閉環/保留)</option>
          </select>
        </div>
      </div>

      <div class="form-group">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
          <label style="margin: 0;">主力師資（依課程專長智能推薦 ＋ 255位師資全庫）</label>
          <span style="font-size: 11px; color: #2563eb; font-weight: 700;" id="matchedTeacherCountHint">⭐ 推薦師資已置頂</span>
        </div>
        
        <!-- Quick search box -->
        <div style="display: flex; gap: 8px; margin-bottom: 6px;">
          <input type="text" id="teacherSearchInput" placeholder="🔍 快速搜尋老師姓名或科目 (例如：林延君、室內、漫畫、王仁駿)..." 
                 style="padding: 7px 10px; font-size: 12px; border: 1px solid var(--border); border-radius: 6px; width: 100%;"
                 oninput="onTeacherSearchInput(this.value)">
          <button type="button" class="btn-action secondary" style="padding: 6px 10px; font-size: 12px; white-space: nowrap;" onclick="clearTeacherSearch()">清空搜尋</button>
        </div>

        <select id="selectTeacher" onchange="onTeacherSelectChange(this)">
          <!-- Populated by JS -->
        </select>
        <input type="text" id="inputCustomTeacher" placeholder="或自行填寫師資..." style="margin-top: 6px; display: none;">
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>目標服務人數 / 實績備註</label>
          <input type="text" id="inputCount" placeholder="例如：目標 100 人 或 140 人">
        </div>

        <div class="form-group">
          <label>梯隊階層標籤</label>
          <select id="selectBadge">
            <option value="A|badge-a|A 基礎">A 基礎</option>
            <option value="B|badge-b|B 進階一">B 進階一</option>
            <option value="C|badge-c|C 進階二">C 進階二</option>
            <option value="★|badge-ocean|★新藍海">★新藍海</option>
            <option value="保留|badge-a|4成保留">4成保留</option>
            <option value="無||無標籤">無標籤</option>
          </select>
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>開班決策屬性標籤</label>
          <select id="selectType">
            <option value="tag-h1|● H1 大排定案">● H1 大排定案 (綠色)</option>
            <option value="tag-h2|▲ H2 保留池">▲ H2 保留池 (橙色)</option>
            <option value="tag-past|2026 實績">2026 實績 (紅色)</option>
            <option value="tag-empty|留加開 / 4成保留">[ 保有空檔 ] 留加開</option>
          </select>
        </div>

        <div class="form-group">
          <label>戰略備註說明</label>
          <input type="text" id="inputNote" placeholder="例如：AI空間生成首開！吸納未修庫存">
        </div>
      </div>

      <div class="modal-footer">
        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
          <button type="button" class="btn-action secondary" style="color: #dc2626; border-color: #fca5a5; background: #fff5f5;" onclick="deleteCurrentSlot()">🗑️ 刪除此課程</button>
          <button type="button" class="btn-action secondary" style="color: #64748b;" onclick="clearSlotToEmpty()">⚪ 設為空檔保留</button>
        </div>
        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
          <button type="button" class="btn-action secondary" onclick="closeModal()">取消</button>
          <button type="submit" class="btn-action green">確認套用落點</button>
        </div>
      </div>
    </form>
  </div>
</div>

<div class="toast" id="toastNotice">
  <span id="toastMsg">✅ 已儲存自訂落點設定！</span>
</div>

<script>
// Raw Preset Data
const PRESET_DATA = __PRESET_JSON_PLACEHOLDER__;

// Active state
let currentCategory = 'anime';
let slotState = loadSlotsFromStorage() || JSON.parse(JSON.stringify(PRESET_DATA));

let isCreatingNewSlot = false;

const timeSlots = [
  { id: "一三", label: "一三", hours: "18:30-21:30" },
  { id: "二四", label: "二四", hours: "18:30-21:30" },
  { id: "六", label: "六", hours: "14-17 / 18-21 (6h)" },
  { id: "日", label: "日", hours: "10-13 / 14-17 (6h)" }
];

const quarters = [
  { id: "2026_q4", label: "2026 第 4 期", sub: "10-12 月 (參考)", isPast: true },
  { id: "2027_q1", label: "第 1 期 1-3 月", sub: "(H1 寒假/春季大排)", isPast: false },
  { id: "2027_q2", label: "第 2 期 4-6 月", sub: "(H1 初夏/進階大排)", isPast: false },
  { id: "2027_q3", label: "第 3 期 7-9 月", sub: "(H2 暑假加開/保留)", isPast: false },
  { id: "2027_q4", label: "第 4 期 10-12 月", sub: "(H2 秋季閉環/保留)", isPast: false }
];

function init() {
  populateCourseDropdown();
  renderMatrix();
  renderFooterNotes();
}

function loadSlotsFromStorage() {
  try {
    const saved = localStorage.getItem("date_schedule_slots_custom");
    if (saved) {
      const parsed = JSON.parse(saved);
      if (!parsed.interior && PRESET_DATA.interior) {
        parsed.interior = JSON.parse(JSON.stringify(PRESET_DATA.interior));
      }
      if (!parsed.anime && PRESET_DATA.anime) {
        parsed.anime = JSON.parse(JSON.stringify(PRESET_DATA.anime));
      }
      if (!parsed.design && PRESET_DATA.design) {
        parsed.design = JSON.parse(JSON.stringify(PRESET_DATA.design));
      }
      return parsed;
    }
  } catch (e) {
    console.warn("Storage load error", e);
  }
  return null;
}

function populateCourseDropdown() {
  const courseSel = document.getElementById("selectCourse");
  courseSel.innerHTML = "";
  
  if (PRESET_DATA.courses_grouped) {
    for (const [groupName, cList] of Object.entries(PRESET_DATA.courses_grouped)) {
      const grp = document.createElement("optgroup");
      grp.label = groupName;
      cList.forEach(c => {
        const opt = document.createElement("option");
        opt.value = c;
        opt.textContent = c;
        grp.appendChild(opt);
      });
      courseSel.appendChild(grp);
    }
  } else {
    PRESET_DATA.courses.forEach(c => {
      const opt = document.createElement("option");
      opt.value = c;
      opt.textContent = c;
      courseSel.appendChild(opt);
    });
  }

  const optCustom = document.createElement("option");
  optCustom.value = "__custom__";
  optCustom.textContent = "✏️ 自訂輸入課程名稱...";
  courseSel.appendChild(optCustom);
}

// Map Course Keywords to Teacher Subjects/Categories
function getMatchedTeachersForCourse(courseName) {
  if (!courseName || courseName === '[ 保有空檔 ]' || courseName === '__custom__') {
    return [];
  }
  
  const allTeachers = PRESET_DATA.teachers || [];
  
  if (courseName.includes("AI室內設計") || courseName.includes("林延君")) {
    return allTeachers.filter(t => t.name === "林延君團隊" || (t.categories && t.categories.includes("室內設計")));
  }
  
  if (courseName.includes("室內") || courseName.includes("AutoCAD") || courseName.includes("SketchUp") || courseName.includes("建築")) {
    return allTeachers.filter(t => {
      const inCat = t.categories && t.categories.includes("室內設計");
      const inSub = t.subjects && t.subjects.some(s => s.includes("室內") || s.includes("AutoCAD") || s.includes("SketchUp"));
      return inCat || inSub;
    });
  }

  if (courseName.includes("漫畫")) {
    return allTeachers.filter(t => t.subjects && t.subjects.some(s => s.includes("漫畫")));
  }

  if (courseName.includes("Vtuber") || courseName.includes("Live2D") || courseName.includes("V 皮") || courseName.includes("V皮")) {
    return allTeachers.filter(t => {
      const inSub = t.subjects && t.subjects.some(s => s.includes("Vtuber") || s.includes("2D"));
      const inSoft = t.software && t.software.some(sf => sf.includes("Live 2D") || sf.includes("Live2D"));
      return inSub || inSoft;
    });
  }

  if (courseName.includes("繪畫") || courseName.includes("電繪") || courseName.includes("Procreate") || courseName.includes("IP 角色") || courseName.includes("IP角色")) {
    return allTeachers.filter(t => {
      const inCat = t.categories && t.categories.includes("數位繪畫");
      const inSub = t.subjects && t.subjects.some(s => s.includes("電繪") || s.includes("IPad") || s.includes("IP角色") || s.includes("日本動畫"));
      return inCat || inSub;
    });
  }

  if (courseName.includes("平面") || courseName.includes("品牌") || courseName.includes("UI") || courseName.includes("商用視覺") || courseName.includes("視覺")) {
    return allTeachers.filter(t => {
      const inCat = t.categories && t.categories.includes("商用視覺");
      const inSub = t.subjects && t.subjects.some(s => s.includes("平面") || s.includes("UI") || s.includes("提案") || s.includes("紅點"));
      return inCat || inSub;
    });
  }

  if (courseName.includes("音樂") || courseName.includes("編曲") || courseName.includes("詞曲") || courseName.includes("歌唱")) {
    return allTeachers.filter(t => {
      const inCat = t.categories && t.categories.includes("音樂製作");
      const inSub = t.subjects && t.subjects.some(s => s.includes("音樂") || s.includes("詞曲") || s.includes("歌唱") || s.includes("改編"));
      return inCat || inSub;
    });
  }

  if (courseName.includes("遊戲") || courseName.includes("Unity")) {
    return allTeachers.filter(t => {
      const inCat = t.categories && t.categories.includes("遊戲設計");
      const inSub = t.subjects && t.subjects.some(s => s.includes("遊戲") || s.includes("Unity"));
      return inCat || inSub;
    });
  }

  if (courseName.includes("After Effects") || courseName.includes("AE") || courseName.includes("Cinema 4D") || courseName.includes("C4D") || courseName.includes("特效") || courseName.includes("動態")) {
    return allTeachers.filter(t => {
      const inCat = t.categories && t.categories.includes("影視特效");
      const inSub = t.subjects && t.subjects.some(s => s.includes("AE") || s.includes("C4D") || s.includes("動態"));
      return inCat || inSub;
    });
  }

  if (courseName.includes("攝影") || courseName.includes("自媒體") || courseName.includes("剪輯")) {
    return allTeachers.filter(t => {
      const inCat = t.categories && t.categories.includes("攝影課程");
      const inSub = t.subjects && t.subjects.some(s => s.includes("攝影") || s.includes("自媒體") || s.includes("剪輯"));
      return inCat || inSub;
    });
  }

  return [];
}

// Populate Teachers Dropdown with smart grouping & recommendations
function populateTeachersDropdown(courseName, currentTeacherName, filterKeyword = "") {
  const teacherSel = document.getElementById("selectTeacher");
  teacherSel.innerHTML = "";

  const allTeachers = PRESET_DATA.teachers || [];
  const keyword = filterKeyword.trim().toLowerCase();

  const matchedTeachers = getMatchedTeachersForCourse(courseName);

  const hintEl = document.getElementById("matchedTeacherCountHint");
  if (hintEl) {
    if (matchedTeachers.length > 0) {
      hintEl.textContent = `⭐ 專長推薦 (${matchedTeachers.length} 位名師置頂)`;
      hintEl.style.display = "inline";
    } else {
      hintEl.style.display = "none";
    }
  }

  function formatTeacherLabel(t) {
    const catStr = (t.categories && t.categories.length > 0) ? t.categories.join('/') : '綜合';
    const subStr = (t.subjects && t.subjects.length > 0) ? t.subjects.slice(0, 3).join('·') : '';
    return subStr ? `${t.name} (${catStr} ｜ 專長: ${subStr})` : `${t.name} (${catStr})`;
  }

  function teacherMatchesKeyword(t) {
    if (!keyword) return true;
    const nameMatch = t.name.toLowerCase().includes(keyword);
    const catMatch = t.categories && t.categories.some(c => c.toLowerCase().includes(keyword));
    const subMatch = t.subjects && t.subjects.some(s => s.toLowerCase().includes(keyword));
    const softMatch = t.software && t.software.some(sf => sf.toLowerCase().includes(keyword));
    return nameMatch || catMatch || subMatch || softMatch;
  }

  // A. Recommended Group
  if (matchedTeachers.length > 0) {
    const filteredMatched = matchedTeachers.filter(teacherMatchesKeyword);
    if (filteredMatched.length > 0) {
      const grpRec = document.createElement("optgroup");
      grpRec.label = `⭐ 本課程專長師資推薦 (${filteredMatched.length} 位)`;
      filteredMatched.forEach(t => {
        const opt = document.createElement("option");
        opt.value = t.name;
        opt.textContent = "⭐ " + formatTeacherLabel(t);
        grpRec.appendChild(opt);
      });
      teacherSel.appendChild(grpRec);
    }
  }

  // B. Grouped by Domain
  const categoriesList = ["室內設計", "商用視覺", "數位繪畫", "音樂製作", "遊戲設計", "影視特效", "攝影課程", "其他領域"];
  const catIcons = {
    "室內設計": "🏛️",
    "商用視覺": "📐",
    "數位繪畫": "🎨",
    "音樂製作": "🎵",
    "遊戲設計": "🎮",
    "影視特效": "🎬",
    "攝影課程": "📷",
    "其他領域": "🌐"
  };

  categoriesList.forEach(catName => {
    const inCat = allTeachers.filter(t => {
      const primaryCat = (t.categories && t.categories.length > 0) ? t.categories[0] : "其他領域";
      const matchesCat = (catName === "其他領域") ? (!t.categories || t.categories.length === 0 || primaryCat === "其他領域") : (primaryCat === catName);
      return matchesCat && teacherMatchesKeyword(t);
    });

    if (inCat.length > 0) {
      const icon = catIcons[catName] || "📁";
      const grp = document.createElement("optgroup");
      grp.label = `${icon} ${catName}師資庫 (${inCat.length} 位)`;
      inCat.forEach(t => {
        const opt = document.createElement("option");
        opt.value = t.name;
        opt.textContent = formatTeacherLabel(t);
        grp.appendChild(opt);
      });
      teacherSel.appendChild(grp);
    }
  });

  // Custom option
  const optCustom = document.createElement("option");
  optCustom.value = "__custom__";
  optCustom.textContent = "✏️ 自訂輸入師資姓名...";
  teacherSel.appendChild(optCustom);

  // Set selection
  if (currentTeacherName && allTeachers.some(t => t.name === currentTeacherName)) {
    teacherSel.value = currentTeacherName;
  } else if (matchedTeachers.length > 0 && !currentTeacherName) {
    teacherSel.value = matchedTeachers[0].name;
  }
}

function onTeacherSearchInput(val) {
  const currentCourse = document.getElementById("selectCourse").value;
  const currentTeacher = document.getElementById("selectTeacher").value;
  populateTeachersDropdown(currentCourse, currentTeacher, val);
}

function clearTeacherSearch() {
  document.getElementById("teacherSearchInput").value = "";
  const currentCourse = document.getElementById("selectCourse").value;
  const currentTeacher = document.getElementById("selectTeacher").value;
  populateTeachersDropdown(currentCourse, currentTeacher, "");
}

function onTeacherSelectChange(sel) {
  const custom = document.getElementById("inputCustomTeacher");
  if (sel.value === '__custom__') {
    custom.style.display = "block";
    custom.focus();
  } else {
    custom.style.display = "none";
  }
}

function switchCategory(cat) {
  currentCategory = cat;
  document.querySelectorAll(".tab-pill").forEach(p => p.classList.remove("active"));
  const btn = document.getElementById("pill-" + cat);
  if (btn) btn.classList.add("active");

  const titleEl = document.getElementById("currentCategoryTitle");
  const statsEl = document.getElementById("currentStats");

  if (cat === 'anime') {
    titleEl.textContent = "落點示範：DATE 線上直播【動漫、電繪與 Vtuber 生態鏈】怎麼排課";
    statsEl.textContent = "全年度 14 班部署 ｜ 100% 符合產品部規範";
  } else if (cat === 'design') {
    titleEl.textContent = "落點示範：DATE 線上直播【視覺平面、AI 遊戲與數位音樂藍海】怎麼排課";
    statsEl.textContent = "全年度 14 班部署 ｜ 100% 符合產品部規範";
  } else if (cat === 'interior') {
    titleEl.textContent = "落點示範：DATE 線上直播【空間建築與 AI 室內設計】怎麼排課";
    statsEl.textContent = "全年度 14 班部署 ｜ AI室內設計實務班 (林延君團隊) 週六黃金時段旗艦首開";
  } else {
    titleEl.textContent = "落點示範：DATE 線上直播【全學系排課落點綜合檢視總表】";
    statsEl.textContent = "42 班大排定案 ＋ 彈性保留全覽 ｜ 四大固定時段零衝突";
  }

  renderMatrix();
  renderFooterNotes();
}

function renderMatrix() {
  const container = document.getElementById("matrixContainer");
  let list = [];

  if (currentCategory === 'anime') {
    list = slotState.anime || [];
  } else if (currentCategory === 'design') {
    list = slotState.design || [];
  } else if (currentCategory === 'interior') {
    list = slotState.interior || [];
  } else {
    list = [...(slotState.anime || []), ...(slotState.design || []), ...(slotState.interior || [])];
  }

  let html = `
    <table class="matrix-table">
      <thead>
        <tr>
          <th>固定時段<br><span style="font-size:11px; font-weight:500; color:#64748b;">(全台線上標準時段)</span></th>
  `;

  quarters.forEach(q => {
    html += `
      <th class="${q.isPast ? 'th-past' : 'th-future'}">
        ${q.label}<br>
        <span style="font-size:11px; font-weight:500;">${q.sub}</span>
      </th>
    `;
  });

  html += `
        </tr>
      </thead>
      <tbody>
  `;

  timeSlots.forEach(ts => {
    html += `
      <tr>
        <td class="slot-time-header">
          <div class="time-day">${ts.label}</div>
          <div class="time-hours">${ts.hours}</div>
        </td>
    `;

    quarters.forEach(q => {
      const slotMatches = list.filter(item => item.timeRow === ts.id && item.quarter === q.id);

      html += `<td>`;
      html += `<div class="slot-cell-container">`;
      html += `<div class="slot-cards-list">`;

      if (slotMatches.length === 0) {
        html += `
          <div class="slot-card is-empty" onclick="openCreateModal('${ts.id}', '${q.id}')">
            <div class="empty-label">
              <strong>[ 保有空檔 ]</strong><br>
              <span style="font-size:11px;">點擊新增排課</span>
            </div>
          </div>
        `;
      } else {
        slotMatches.forEach(slot => {
          if (slot.isEmpty) {
            html += `
              <div class="slot-card is-empty" onclick="openEditModal('${slot.slotId}')">
                <div class="empty-label">
                  <strong>[ 保有空檔 ]</strong><br>
                  <span style="font-size:11px;">${slot.typeText || '留加開 / 4成保留'}</span>
                </div>
                <div class="card-btn-group" onclick="event.stopPropagation()">
                  <button type="button" class="btn-card-icon edit" title="設定此空檔" onclick="event.stopPropagation(); openEditModal('${slot.slotId}')">✏️ 設定</button>
                  <button type="button" class="btn-card-icon del" title="刪除此空檔" onclick="event.stopPropagation(); deleteSlotDirectly('${slot.slotId}')">🗑️ 刪除</button>
                </div>
              </div>
            `;
          } else {
            html += `
              <div class="slot-card" onclick="openEditModal('${slot.slotId}')">
                <div class="sc-top">
                  <div style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap; flex: 1; padding-right: 4px;">
                    ${slot.badge ? `<span class="badge-level ${slot.badgeClass}">${slot.badgeText || slot.badge}</span>` : ''}
                    <span class="course-name">${slot.name}</span>
                  </div>
                  <div class="card-btn-group" onclick="event.stopPropagation()">
                    <button type="button" class="btn-card-icon edit" title="編輯設定此課程" onclick="event.stopPropagation(); openEditModal('${slot.slotId}')">✏️</button>
                    <button type="button" class="btn-card-icon del" title="刪除此課程" onclick="event.stopPropagation(); deleteSlotDirectly('${slot.slotId}')">🗑️</button>
                  </div>
                </div>
                <div class="sc-mid">
                  ${slot.teacher ? `<span class="teacher-name">師資: ${slot.teacher}</span>` : ''}
                  ${slot.count ? `<span class="student-count"> (${slot.count})</span>` : ''}
                </div>
                <div class="sc-bottom ${slot.typeTag}">
                  ${slot.typeText}
                </div>
              </div>
            `;
          }
        });
      }

      html += `</div>`; // .slot-cards-list

      // Cell Add Button
      html += `
        <button type="button" class="btn-cell-add" title="在此欄位新增一班" onclick="openCreateModal('${ts.id}', '${q.id}')">
          <span>➕</span> 新增課程
        </button>
      `;

      html += `</div>`; // .slot-cell-container
      html += `</td>`;
    });

    html += `</tr>`;
  });

  html += `
      </tbody>
    </table>
  `;

  container.innerHTML = html;
}

function renderFooterNotes() {
  const notesLeft = document.getElementById("notesListLeft");
  if (currentCategory === 'anime') {
    notesLeft.innerHTML = `
      <li><span class="bullet-icon">•</span> <div><strong>固定時段嚴格對齊：</strong>一三(18:30-21:30)、二四(18:30-21:30)、六(14-17 / 18-21)、日(10-13 / 14-17)。</div></li>
      <li><span class="bullet-icon">•</span> <div><strong>觀察 2026 Q4 銜接到 2027：</strong>曾建華漫畫班於 Q1 寒假(一三晚)強力回補 130 人，終結 231 筆補課民怨！</div></li>
      <li><span class="bullet-icon">•</span> <div><strong>黃俊傑 Vtuber 生態鏈：</strong>（A攻略 ➔ B立繪 ➔ C動畫）全年度運行兩大完整梯隊，完課率超群！</div></li>
      <li><span class="bullet-icon">•</span> <div><strong>柯光曜老師精準佈局：</strong>於 Q2 (二四晚)精準開出《IP角色人物創作》，一口氣清空 163 人完全未登記幽靈庫存！</div></li>
    `;
  } else if (currentCategory === 'design') {
    notesLeft.innerHTML = `
      <li><span class="bullet-icon">•</span> <div><strong>商用視覺平面設計為全校未消耗第一大戶（473人）：</strong>全年部署 4 班（雙師分流），年消化近 500 人！</div></li>
      <li><span class="bullet-icon">•</span> <div><strong>王仁駿老師《平面進階》：</strong>安排於二四晚(18:30-21:30)，無縫銜接 Q1 基礎班結業，發揮 55.4% 高完課率口碑。</div></li>
      <li><span class="bullet-icon">•</span> <div><strong>週日首開《全 AI 音樂創作》與《音樂製作人》：</strong>一舉終結 88.2% 跨區補課痛點與 370 位積壓學員！</div></li>
      <li><span class="bullet-icon">•</span> <div><strong>果斷停開 AutoCAD / SketchUp 停售課：</strong>100% 轉 VOD 自主觀看，時段全數釋放給高產能 AI 課！</div></li>
    `;
  } else if (currentCategory === 'interior') {
    notesLeft.innerHTML = `
      <li><span class="bullet-icon">•</span> <div><strong>首度導入《AI室內設計實務班》：</strong>由「林延君團隊」主力執教，於週六全日 6 小時時段（14:00-17:00 / 18:00-21:00 休一小）強勢首開！</div></li>
      <li><span class="bullet-icon">•</span> <div><strong>直攻空間生成式 AI 藍海：</strong>結合生成式空間渲染、CAD 與實務工程落地，打破傳統實體教室硬體瓶頸，預估年消化 400+ 人次。</div></li>
      <li><span class="bullet-icon">•</span> <div><strong>AutoCAD / SketchUp 平日雙晚分流：</strong>一三晚由廖韶吟、戴旭斌擔綱建築空間製圖；二四晚由林宜廷、蕭博宇擔綱建模，打造室內設計完整修課鏈。</div></li>
      <li><span class="bullet-icon">•</span> <div><strong>完全符合 DATE 4 大固定時段規範：</strong>無教室時段衝突，嚴格落實 6 成大排定案 ＋ 4 成保留池彈性加開。</div></li>
    `;
  } else {
    notesLeft.innerHTML = `
      <li><span class="bullet-icon">•</span> <div><strong>全學系綜合排課全覽視圖：</strong>整合動漫、Vtuber、平面設計、AI遊戲、數位音樂與【空間建築與 AI 室內設計】六大課系。</div></li>
      <li><span class="bullet-icon">•</span> <div><strong>四大時段百分百承載：</strong>平日雙晚間 ＋ 週末全日雙時段，落實「無實體座位上限、無教室時段衝突」。</div></li>
      <li><span class="bullet-icon">•</span> <div><strong>255 位在任師資陣容：</strong>合作中與培訓期名師全數就位，支援專長智慧推薦與一鍵選定。</div></li>
    `;
  }
}

// Modal Edit
let activeEditingSlot = null;

function findSlotById(id) {
  for (const s of (slotState.anime || [])) if (s.slotId === id) return s;
  for (const s of (slotState.design || [])) if (s.slotId === id) return s;
  for (const s of (slotState.interior || [])) if (s.slotId === id) return s;
  return null;
}

function removeSlotFromState(slotId) {
  for (const cat of ['anime', 'design', 'interior']) {
    if (slotState[cat]) {
      const idx = slotState[cat].findIndex(s => s.slotId === slotId);
      if (idx !== -1) {
        slotState[cat].splice(idx, 1);
        return true;
      }
    }
  }
  return false;
}

function deleteSlotDirectly(slotId) {
  const slot = findSlotById(slotId);
  if (!slot) return;
  const slotName = slot.name && slot.name !== '[ 保有空檔 ]' ? slot.name : "此空檔卡片";
  if (confirm(`確定要刪除「${slotName}」嗎？\\n刪除後此課程將從該時段落點中移除。`)) {
    removeSlotFromState(slotId);
    saveSlotsToStorage();
    renderMatrix();
    showToast(`🗑️ 已成功刪除「${slotName}」！`);
  }
}

function deleteCurrentSlot() {
  if (!activeEditingSlot) return;
  const slotName = activeEditingSlot.name && activeEditingSlot.name !== '[ 保有空檔 ]' ? activeEditingSlot.name : "此課程";
  if (confirm(`確定要刪除「${slotName}」嗎？\\n刪除後此課程將從該時段落點中移除。`)) {
    removeSlotFromState(activeEditingSlot.slotId);
    isCreatingNewSlot = false;
    saveSlotsToStorage();
    closeModal();
    renderMatrix();
    showToast(`🗑️ 已成功刪除「${slotName}」！`);
  }
}

function openEditModal(slotId) {
  const slot = findSlotById(slotId);
  if (!slot) return;
  activeEditingSlot = slot;

  document.getElementById("modalTitle").innerHTML = `⚙️ 設定排課落點：<strong>${slot.name}</strong>`;
  document.getElementById("editSlotId").value = slot.slotId;

  // Clear search input
  document.getElementById("teacherSearchInput").value = "";

  // Set course
  const selCourse = document.getElementById("selectCourse");
  const customCourse = document.getElementById("inputCustomCourse");
  
  let courseFound = false;
  for (let i = 0; i < selCourse.options.length; i++) {
    if (selCourse.options[i].value === slot.name) {
      selCourse.selectedIndex = i;
      courseFound = true;
      break;
    }
  }

  if (courseFound) {
    customCourse.style.display = "none";
  } else {
    selCourse.value = "__custom__";
    customCourse.value = slot.name;
    customCourse.style.display = "block";
  }

  // Set time & quarter
  document.getElementById("selectTime").value = slot.timeRow;
  document.getElementById("selectQuarter").value = slot.quarter;

  // Populate teachers for this course and select current teacher
  populateTeachersDropdown(slot.name, slot.teacher, "");

  const selTeacher = document.getElementById("selectTeacher");
  const customTeacher = document.getElementById("inputCustomTeacher");
  
  if (slot.teacher && selTeacher.value === slot.teacher) {
    customTeacher.style.display = "none";
  } else if (slot.teacher) {
    selTeacher.value = "__custom__";
    customTeacher.value = slot.teacher;
    customTeacher.style.display = "block";
  } else {
    customTeacher.style.display = "none";
  }

  document.getElementById("inputCount").value = slot.count || "";

  // Badge
  const selBadge = document.getElementById("selectBadge");
  if (slot.badge === "A") selBadge.value = "A|badge-a|A 基礎";
  else if (slot.badge === "B") selBadge.value = "B|badge-b|B 進階一";
  else if (slot.badge === "C") selBadge.value = "C|badge-c|C 進階二";
  else if (slot.badge === "★") selBadge.value = "★|badge-ocean|★新藍海";
  else if (slot.isEmpty) selBadge.value = "無||無標籤";
  else selBadge.value = "A|badge-a|A 基礎";

  // Type Tag
  const selType = document.getElementById("selectType");
  if (slot.typeTag === "tag-h1") selType.value = "tag-h1|● H1 大排定案";
  else if (slot.typeTag === "tag-h2") selType.value = "tag-h2|▲ H2 保留池";
  else if (slot.typeTag === "tag-past") selType.value = "tag-past|2026 實績";
  else selType.value = "tag-empty|留加開 / 4成保留";

  // Note
  const rawNote = slot.typeText || "";
  document.getElementById("inputNote").value = rawNote ? rawNote.replace(/^[●▲]\\s*(H[12]\\s*大排定案|H[12]\\s*保留池)\\s*\\(/, '').replace(/\\)$/, '') : "";

  document.getElementById("slotModal").classList.add("active");
}

function openCreateModal(timeRow, quarter) {
  let cat = currentCategory;
  if (cat === 'all') {
    cat = 'interior';
  }
  const newId = cat + '_' + timeRow + '_' + quarter + '_' + Date.now();
  
  let defaultCourse = (cat === 'interior') ? "AI室內設計實務班" : ((cat === 'design') ? "商用視覺平面設計" : "數位漫畫班");
  let defaultTeacher = (cat === 'interior') ? "林延君團隊" : ((cat === 'design') ? "王仁駿" : "曾建華");
  
  const newSlot = {
    slotId: newId,
    category: cat,
    timeRow: timeRow,
    timeStr: timeRow === '一三' ? '一三 18:30-21:30' : (timeRow === '二四' ? '二四 18:30-21:30' : (timeRow === '六' ? '六 14-17 / 18-21 (6h)' : '日 10-13 / 14-17 (6h)')),
    quarter: quarter,
    quarterLabel: quarter,
    badge: (cat === 'interior' && defaultCourse.includes("AI")) ? "★" : "A",
    badgeText: (cat === 'interior' && defaultCourse.includes("AI")) ? "★新旗艦" : "A 基礎",
    badgeClass: (cat === 'interior' && defaultCourse.includes("AI")) ? "badge-ocean" : "badge-a",
    name: defaultCourse,
    teacher: defaultTeacher,
    count: "目標 100 人",
    typeTag: quarter.includes('q1') || quarter.includes('q2') ? "tag-h1" : "tag-h2",
    typeText: quarter.includes('q1') || quarter.includes('q2') ? "● H1 大排定案 (新設)" : "▲ H2 保留池 (新設)",
    isEmpty: false
  };

  if (!slotState[cat]) slotState[cat] = [];
  slotState[cat].push(newSlot);
  isCreatingNewSlot = true;

  openEditModal(newId);
}

function onCourseSelectChange(sel) {
  const custom = document.getElementById("inputCustomCourse");
  const courseName = sel.value === '__custom__' ? custom.value.trim() : sel.value;
  
  if (sel.value === '__custom__') {
    custom.style.display = "block";
    custom.focus();
  } else {
    custom.style.display = "none";
  }

  const matched = getMatchedTeachersForCourse(courseName);
  let defaultTeacher = matched.length > 0 ? matched[0].name : "";
  populateTeachersDropdown(courseName, defaultTeacher, document.getElementById("teacherSearchInput").value);
}

function closeModal() {
  if (isCreatingNewSlot && activeEditingSlot) {
    // If canceled without saving new slot, discard it
    removeSlotFromState(activeEditingSlot.slotId);
    isCreatingNewSlot = false;
    renderMatrix();
  }
  document.getElementById("slotModal").classList.remove("active");
  activeEditingSlot = null;
}

function closeModalOnOverlay(e) {
  if (e.target.id === "slotModal") closeModal();
}

function saveSlotForm(e) {
  e.preventDefault();
  if (!activeEditingSlot) return;

  const selCourse = document.getElementById("selectCourse").value;
  const courseName = selCourse === '__custom__' ? document.getElementById("inputCustomCourse").value.trim() : selCourse;

  const selTeacher = document.getElementById("selectTeacher").value;
  const teacherName = selTeacher === '__custom__' ? document.getElementById("inputCustomTeacher").value.trim() : selTeacher;

  const timeRow = document.getElementById("selectTime").value;
  const quarter = document.getElementById("selectQuarter").value;
  const count = document.getElementById("inputCount").value.trim();

  const [bCode, bClass, bText] = document.getElementById("selectBadge").value.split("|");
  const [tTag, tPrefix] = document.getElementById("selectType").value.split("|");
  const note = document.getElementById("inputNote").value.trim();

  activeEditingSlot.name = courseName || "[ 保有空檔 ]";
  activeEditingSlot.isEmpty = (courseName === "[ 保有空檔 ]" || tTag === "tag-empty");
  activeEditingSlot.timeRow = timeRow;
  activeEditingSlot.quarter = quarter;
  activeEditingSlot.teacher = teacherName;
  activeEditingSlot.count = count;
  activeEditingSlot.badge = bCode === "無" ? "" : bCode;
  activeEditingSlot.badgeClass = bClass;
  activeEditingSlot.badgeText = bText;
  activeEditingSlot.typeTag = tTag;
  activeEditingSlot.typeText = note ? `${tPrefix} (${note})` : tPrefix;

  isCreatingNewSlot = false;
  saveSlotsToStorage();
  closeModal();
  renderMatrix();
  showToast("✅ 排課落點已更新並自動存檔！");
}

function clearSlotToEmpty() {
  if (!activeEditingSlot) return;
  activeEditingSlot.name = "[ 保有空檔 ]";
  activeEditingSlot.isEmpty = true;
  activeEditingSlot.teacher = "";
  activeEditingSlot.count = "";
  activeEditingSlot.badge = "";
  activeEditingSlot.badgeClass = "";
  activeEditingSlot.badgeText = "";
  activeEditingSlot.typeTag = "tag-empty";
  activeEditingSlot.typeText = "留加開 / 趨勢 / 4成保留";

  isCreatingNewSlot = false;
  saveSlotsToStorage();
  closeModal();
  renderMatrix();
  showToast("🗑️ 該落點已設為空檔保留！");
}

function saveSlotsToStorage() {
  try {
    localStorage.setItem("date_schedule_slots_custom", JSON.stringify(slotState));
    showToast("💾 自訂落點設定已儲存至瀏覽器！");
  } catch (e) {
    console.warn("Storage error", e);
    showToast("⚠️ 儲存提醒：請確認瀏覽器儲存權限");
  }
}

function resetToPreset() {
  if (confirm("確定要還原為系統標準排課落點示範嗎？所有自訂修改將被重置。")) {
    slotState = JSON.parse(JSON.stringify(PRESET_DATA));
    try { localStorage.removeItem("date_schedule_slots_custom"); } catch(e) {}
    renderMatrix();
    showToast("🔄 已成功還原為標準落點示範！");
  }
}

function showToast(msg) {
  const toast = document.getElementById("toastNotice");
  const msgEl = document.getElementById("toastMsg");
  msgEl.textContent = msg;
  toast.classList.add("active");
  setTimeout(() => {
    toast.classList.remove("active");
  }, 2500);
}

// Initialize
window.onload = init;
</script>

</body>
</html>
"""

final_html = html_template.replace("__PRESET_JSON_PLACEHOLDER__", preset_json_str)

# Save to static/schedule_slot_demonstration.html
with open("static/schedule_slot_demonstration.html", "w", encoding="utf-8") as f:
    f.write(final_html)

print("Successfully generated and saved static/schedule_slot_demonstration.html!")
