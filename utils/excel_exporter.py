import io
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def build_comprehensive_workbook(responses: list, class_info: dict, class_id: str) -> openpyxl.Workbook:
    wb = openpyxl.Workbook()
    
    course_name = class_info.get("course_name") or "日本動畫職人 - 背景美術｜線上直播"
    teacher_name = class_info.get("teacher_name") or "授課講師"
    organizer = class_info.get("organizer") or "赫綵教育集團 x Date日琪資訊"
    total = len(responses)
    today_str = datetime.now().strftime("%Y-%m-%d")

    # 1. 樣式規格
    font_main_title = Font(name="微軟正黑體", size=13, bold=True, color="FFFFFF")
    font_meta = Font(name="微軟正黑體", size=9.5, bold=True, color="166534")
    font_sec_hdr = Font(name="微軟正黑體", size=11, bold=True, color="FFFFFF")
    font_tbl_hdr = Font(name="微軟正黑體", size=9.5, bold=True, color="0F172A")
    font_bold = Font(name="微軟正黑體", size=9.5, bold=True, color="0F172A")
    font_regular = Font(name="微軟正黑體", size=9.5, color="334155")
    font_red_bold = Font(name="微軟正黑體", size=9.5, bold=True, color="DC2626")
    font_blue_bold = Font(name="微軟正黑體", size=9.5, bold=True, color="2563EB")
    font_orange_bold = Font(name="微軟正黑體", size=9.5, bold=True, color="D97706")

    fill_main_title = PatternFill(start_color="15803D", fill_type="solid") # 深綠主標
    fill_meta = PatternFill(start_color="F0FDF4", fill_type="solid") # 淺綠中繼資訊列
    fill_sec_struggle = PatternFill(start_color="991B1B", fill_type="solid") # 痛點磚紅
    fill_sec_exp = PatternFill(start_color="1E40AF", fill_type="solid") # 背景皇家藍
    fill_sec_nps = PatternFill(start_color="065F46", fill_type="solid") # 滿意度湖水綠
    fill_sec_reward = PatternFill(start_color="3730A3", fill_type="solid") # 好禮深靛藍
    fill_sec_sched = PatternFill(start_color="334155", fill_type="solid") # 課表板岩灰
    fill_tbl_hdr = PatternFill(start_color="F1F5F9", fill_type="solid") # 表頭灰階

    fill_rank1 = PatternFill(start_color="FEE2E2", fill_type="solid") # 紅
    fill_rank2 = PatternFill(start_color="FFEDD5", fill_type="solid") # 橘
    fill_rank3 = PatternFill(start_color="FEF9C3", fill_type="solid") # 黃
    fill_zebra = PatternFill(start_color="F8FAFC", fill_type="solid")

    thin_border_side = Side(style='thin', color='E2E8F0')
    border_cell = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    border_tbl_hdr = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=Side(style='medium', color='CBD5E1'))

    align_center = Alignment(horizontal="center", vertical="center")
    align_left = Alignment(horizontal="left", vertical="center")
    align_right = Alignment(horizontal="right", vertical="center")

    # 數據統計預處理
    struggle_counts = {}
    exp_counts = {}
    promoters = 0
    passives = 0
    detractors = 0
    inst_sum = 0
    course_sum = 0
    ta_sum = 0
    count_inst = 0
    count_course = 0
    count_ta = 0
    reward_counts = {}
    sched_counts = {}

    for r in responses:
        s = (r.get("struggle_point") or "").strip()
        if not s or s.lower() in ["無", "nan", "none", "-", "未填寫"]:
            s = "無卡關或未填寫"
        struggle_counts[s] = struggle_counts.get(s, 0) + 1

        e = (r.get("prior_experience") or "").strip() or "未填寫背景"
        exp_counts[e] = exp_counts.get(e, 0) + 1

        try:
            nps = float(r.get("nps_score") or 0)
            if nps >= 9:
                promoters += 1
            elif nps >= 7:
                passives += 1
            elif nps > 0:
                detractors += 1
        except Exception:
            pass

        try:
            ir = float(r.get("instructor_rating") or 0)
            if ir > 0:
                inst_sum += ir
                count_inst += 1
        except Exception:
            pass

        try:
            cr = float(r.get("course_rating") or 0)
            if cr > 0:
                course_sum += cr
                count_course += 1
        except Exception:
            pass

        try:
            tr = float(r.get("ta_rating") or 0)
            if tr > 0:
                ta_sum += tr
                count_ta += 1
        except Exception:
            pass

        rew = (r.get("selected_reward_course") or "").strip() or "無需兌換 (純回饋)"
        reward_counts[rew] = reward_counts.get(rew, 0) + 1

        sch = (r.get("followup_schedules_selected") or "").strip() or "未勾選時段"
        sched_counts[sch] = sched_counts.get(sch, 0) + 1

    nps_total = promoters + passives + detractors
    nps_score = round(((promoters - detractors) / nps_total) * 100) if nps_total > 0 else 0
    avg_inst = f"{(inst_sum / count_inst):.2f}" if count_inst > 0 else "-"
    avg_course = f"{(course_sum / count_course):.2f}" if count_course > 0 else "-"
    avg_ta = f"{(ta_sum / count_ta):.2f}" if count_ta > 0 else "-"

    sorted_struggles = sorted(struggle_counts.items(), key=lambda x: x[1], reverse=True)
    sorted_exp = sorted(exp_counts.items(), key=lambda x: x[1], reverse=True)
    sorted_rewards = sorted(reward_counts.items(), key=lambda x: x[1], reverse=True)
    sorted_scheds = sorted(sched_counts.items(), key=lambda x: x[1], reverse=True)

    # ========================================================
    # 【工作表 1】全維度統整統計總表 (精美圖表總匯)
    # ========================================================
    ws1 = wb.active
    ws1.title = "全維度統整統計總表"
    ws1.sheet_properties.tabColor = "15803D"

    # Row 1: 主標題
    ws1.merge_cells("A1:E1")
    c = ws1["A1"]
    c.value = f"🌲 【{course_name}】結業學習成果與多維度統計分析總表"
    c.font = font_main_title
    c.fill = fill_main_title
    c.alignment = align_center
    ws1.row_dimensions[1].height = 36

    # Row 2: 摘要元資料列
    metas = [
        ("A2", f"授課講師：{teacher_name}"),
        ("B2", f"主辦機構：{organizer}"),
        ("C2", f"總填答人數：{total} 人"),
        ("D2", f"NPS 淨推薦值：{'+' if nps_score >= 0 else ''}{nps_score}"),
        ("E2", f"講師滿意均分：{avg_inst} ★")
    ]
    for pos, txt in metas:
        cell = ws1[pos]
        cell.value = txt
        cell.font = font_meta
        cell.fill = fill_meta
        cell.alignment = align_center
        cell.border = border_cell
    ws1.row_dimensions[2].height = 25

    cur_row = 4

    # 區塊一：課綱卡關痛點
    ws1.merge_cells(start_row=cur_row, start_column=1, end_row=cur_row, end_column=5)
    sec1 = ws1.cell(row=cur_row, column=1, value="🎯 區塊一：課綱卡關痛點佔比排行 & 精準推課名單 (按嚴重度降序推薦)")
    sec1.font = font_sec_hdr
    sec1.fill = fill_sec_struggle
    sec1.alignment = align_center
    ws1.row_dimensions[cur_row].height = 28
    cur_row += 1

    headers_1 = ["排名", "課綱痛點項目名稱", "勾選票數", "佔比 (%)", "遇到此卡關點的學員名單 (姓名 / 手機 / 起點)"]
    for col_idx, h in enumerate(headers_1, 1):
        cell = ws1.cell(row=cur_row, column=col_idx, value=h)
        cell.font = font_tbl_hdr
        cell.fill = fill_tbl_hdr
        cell.alignment = align_center
        cell.border = border_tbl_hdr
    ws1.row_dimensions[cur_row].height = 24
    cur_row += 1

    for idx, (s, cnt) in enumerate(sorted_struggles, 1):
        pct_val = f"{(cnt / total * 100):.1f}%" if total > 0 else "0.0%"
        students = [
            f"{r.get('student_name') or '匿名'} ({r.get('phone') or '無電話'} / {r.get('prior_experience') or '未填'})"
            for r in responses if (r.get("struggle_point") or "").strip() == s or (not r.get("struggle_point") and s == "無卡關或未填寫")
        ]
        roster_str = "、".join(students) if students else "-"

        rank_fill = fill_rank1 if idx == 1 else (fill_rank2 if idx == 2 else (fill_rank3 if idx == 3 else None))
        rank_font = font_red_bold if idx <= 2 else font_bold

        row_cells = [
            (1, f"第 {idx} 名", align_center, rank_fill, rank_font),
            (2, s, align_left, None, font_bold if idx <= 2 else font_regular),
            (3, cnt, align_center, None, font_bold),
            (4, pct_val, align_center, None, font_red_bold if idx <= 2 else font_regular),
            (5, roster_str, align_left, None, font_regular)
        ]
        for col_idx, val, algn, fill_bg, fnt in row_cells:
            cell = ws1.cell(row=cur_row, column=col_idx, value=val)
            cell.alignment = algn
            cell.font = fnt
            if fill_bg:
                cell.fill = fill_bg
            cell.border = border_cell
        ws1.row_dimensions[cur_row].height = 22
        cur_row += 1

    cur_row += 1

    # 區塊二：起點背景分布
    ws1.merge_cells(start_row=cur_row, start_column=1, end_row=cur_row, end_column=5)
    sec2 = ws1.cell(row=cur_row, column=1, value="🌱 區塊二：起點背景分布 & 核心進步收穫統計")
    sec2.font = font_sec_hdr
    sec2.fill = fill_sec_exp
    sec2.alignment = align_center
    ws1.row_dimensions[cur_row].height = 28
    cur_row += 1

    headers_2 = ["分析指標群組", "起點背景程度分類", "人數", "佔比 (%)", "對應學員名單"]
    for col_idx, h in enumerate(headers_2, 1):
        cell = ws1.cell(row=cur_row, column=col_idx, value=h)
        cell.font = font_tbl_hdr
        cell.fill = fill_tbl_hdr
        cell.alignment = align_center
        cell.border = border_tbl_hdr
    ws1.row_dimensions[cur_row].height = 24
    cur_row += 1

    for idx, (e, cnt) in enumerate(sorted_exp, 1):
        pct_val = f"{(cnt / total * 100):.1f}%" if total > 0 else "0.0%"
        students = [
            f"{r.get('student_name') or '匿名'} ({r.get('phone') or '無電話'})"
            for r in responses if (r.get("prior_experience") or "").strip() == e or (not r.get("prior_experience") and e == "未填寫背景")
        ]
        roster_str = "、".join(students) if students else "-"

        row_cells = [
            (1, "學員起點背景", align_center, None, font_bold),
            (2, e, align_left, None, font_bold),
            (3, cnt, align_center, None, font_bold),
            (4, pct_val, align_center, None, font_blue_bold),
            (5, roster_str, align_left, None, font_regular)
        ]
        for col_idx, val, algn, fill_bg, fnt in row_cells:
            cell = ws1.cell(row=cur_row, column=col_idx, value=val)
            cell.alignment = algn
            cell.font = fnt
            if fill_bg:
                cell.fill = fill_bg
            cell.border = border_cell
        ws1.row_dimensions[cur_row].height = 22
        cur_row += 1

    cur_row += 1

    # 區塊三：綜合滿意度與 NPS 評價
    ws1.merge_cells(start_row=cur_row, start_column=1, end_row=cur_row, end_column=5)
    sec3 = ws1.cell(row=cur_row, column=1, value="🔥 區塊三：綜合指標與 NPS 評價 (滿分與推薦強度分析)")
    sec3.font = font_sec_hdr
    sec3.fill = fill_sec_nps
    sec3.alignment = align_center
    ws1.row_dimensions[cur_row].height = 28
    cur_row += 1

    headers_3 = ["評估指標", "統計數值 / 人數", "佔比 / 說明", "指標詳細解讀", "團隊行動建議"]
    for col_idx, h in enumerate(headers_3, 1):
        cell = ws1.cell(row=cur_row, column=col_idx, value=h)
        cell.font = font_tbl_hdr
        cell.fill = fill_tbl_hdr
        cell.alignment = align_center
        cell.border = border_tbl_hdr
    ws1.row_dimensions[cur_row].height = 24
    cur_row += 1

    nps_rows = [
        ("淨推薦值 (NPS)", f"{'+' if nps_score >= 0 else ''}{nps_score}", f"推薦率 {(promoters/nps_total*100):.1f}%" if nps_total > 0 else "0%", "淨推薦分數介於 -100 ~ +100 之間", "高於 +50 即屬卓越學習體驗", font_red_bold),
        ("推薦者 (Promoters: 9-10分)", f"{promoters} 人", f"{(promoters/nps_total*100):.1f}%" if nps_total > 0 else "0%", "極度滿意且願意主動推薦之鐵粉學員", "優先邀請進階課程或給予 VIP 福利", font_bold),
        ("被動者 (Passives: 7-8分)", f"{passives} 人", f"{(passives/nps_total*100):.1f}%" if nps_total > 0 else "0%", "滿意但態度中立、需持續經營之學員", "定期提供乾貨教學或小課堂以維持熱度", font_regular),
        ("批評者 (Detractors: 0-6分)", f"{detractors} 人", f"{(detractors/nps_total*100):.1f}%" if nps_total > 0 else "0%", "學習受挫或體驗不佳、需要主動關心之學員", "專員於 1 日內致電傾聽痛點並提供協助", font_regular),
        ("講師授課滿意度均分", f"{avg_inst} ★", "滿分 5.00 星", "學員對講師教學節奏與專業度評價", "維持高水準教學與現場互動反饋", font_orange_bold),
        ("整體課程內容均分", f"{avg_course} ★", "滿分 5.00 星", "課綱內容實用性與編排合理度", "依卡關排行微調講義範例難度", font_orange_bold),
        ("助教支援滿意度均分", f"{avg_ta} ★", "滿分 5.00 星", "課堂與課後助教即時解答品質", "感謝助教群即時解惑與陪伴指導", font_orange_bold)
    ]
    for row_tup in nps_rows:
        name, val, pct_lbl, desc, act, fnt = row_tup
        row_cells = [
            (1, name, align_left, None, font_bold),
            (2, val, align_center, None, fnt),
            (3, pct_lbl, align_center, None, font_bold),
            (4, desc, align_left, None, font_regular),
            (5, act, align_left, None, font_regular)
        ]
        for col_idx, val_c, algn, fill_bg, fnt_c in row_cells:
            cell = ws1.cell(row=cur_row, column=col_idx, value=val_c)
            cell.alignment = algn
            cell.font = fnt_c
            cell.border = border_cell
        ws1.row_dimensions[cur_row].height = 22
        cur_row += 1

    cur_row += 1

    # 區塊四：好禮兌換與開課預約
    ws1.merge_cells(start_row=cur_row, start_column=1, end_row=cur_row, end_column=5)
    sec4 = ws1.cell(row=cur_row, column=1, value="🎁 區塊四：單元課好禮兌換需求 ＆ 開課梯次時段預約統計")
    sec4.font = font_sec_hdr
    sec4.fill = fill_sec_reward
    sec4.alignment = align_center
    ws1.row_dimensions[cur_row].height = 28
    cur_row += 1

    headers_4 = ["排名", "兌換項目 / 即將開課梯次時段", "登記人數", "全班佔比 (%)", "分類說明"]
    for col_idx, h in enumerate(headers_4, 1):
        cell = ws1.cell(row=cur_row, column=col_idx, value=h)
        cell.font = font_tbl_hdr
        cell.fill = fill_tbl_hdr
        cell.alignment = align_center
        cell.border = border_tbl_hdr
    ws1.row_dimensions[cur_row].height = 24
    cur_row += 1

    for idx, (rew, cnt) in enumerate(sorted_rewards, 1):
        pct_val = f"{(cnt / total * 100):.1f}%" if total > 0 else "0.0%"
        row_cells = [
            (1, f"贈禮 {idx}", align_center, None, font_bold),
            (2, rew, align_left, None, font_bold),
            (3, cnt, align_center, None, font_bold),
            (4, pct_val, align_center, None, font_blue_bold),
            (5, "線上單元課兌換好禮", align_left, None, font_regular)
        ]
        for col_idx, val_c, algn, fill_bg, fnt_c in row_cells:
            cell = ws1.cell(row=cur_row, column=col_idx, value=val_c)
            cell.alignment = algn
            cell.font = fnt_c
            cell.border = border_cell
        ws1.row_dimensions[cur_row].height = 22
        cur_row += 1

    for idx, (sch, cnt) in enumerate(sorted_scheds, 1):
        pct_val = f"{(cnt / total * 100):.1f}%" if total > 0 else "0.0%"
        row_cells = [
            (1, f"時段 {idx}", align_center, None, font_bold),
            (2, sch, align_left, None, font_bold),
            (3, cnt, align_center, None, font_bold),
            (4, pct_val, align_center, None, font_orange_bold),
            (5, "預約即將開課線上直播班時段", align_left, None, font_regular)
        ]
        for col_idx, val_c, algn, fill_bg, fnt_c in row_cells:
            cell = ws1.cell(row=cur_row, column=col_idx, value=val_c)
            cell.alignment = algn
            cell.font = fnt_c
            cell.border = border_cell
        ws1.row_dimensions[cur_row].height = 22
        cur_row += 1

    ws1.column_dimensions["A"].width = 16
    ws1.column_dimensions["B"].width = 38
    ws1.column_dimensions["C"].width = 15
    ws1.column_dimensions["D"].width = 16
    ws1.column_dimensions["E"].width = 56

    # ========================================================
    # 【工作表 2】課綱痛點排行與推課表
    # ========================================================
    ws2 = wb.create_sheet(title="課綱痛點排行與推課表")
    ws2.sheet_properties.tabColor = "DC2626"

    ws2.merge_cells("A1:H1")
    t2 = ws2["A1"]
    t2.value = "🎯 課綱卡關痛點深層排行 ＆ 對應學員推廣進階課程表"
    t2.font = font_main_title
    t2.fill = fill_sec_struggle
    t2.alignment = align_center
    ws2.row_dimensions[1].height = 36

    headers_ws2 = ["排名", "課綱痛點項目名稱", "勾選票數", "全班佔比 (%)", "受挫學員姓名", "學員聯絡手機", "學員起點背景", "建議後續推廣課程主題"]
    for col_idx, h in enumerate(headers_ws2, 1):
        cell = ws2.cell(row=2, column=col_idx, value=h)
        cell.font = font_tbl_hdr
        cell.fill = fill_tbl_hdr
        cell.alignment = align_center
        cell.border = border_tbl_hdr
    ws2.row_dimensions[2].height = 24

    cur_row = 3
    for idx, (s, cnt) in enumerate(sorted_struggles, 1):
        pct_val = f"{(cnt / total * 100):.1f}%" if total > 0 else "0.0%"
        students = [
            r for r in responses if (r.get("struggle_point") or "").strip() == s or (not r.get("struggle_point") and s == "無卡關或未填寫")
        ]
        if not students:
            students = [{}]

        rank_fill = fill_rank1 if idx == 1 else (fill_rank2 if idx == 2 else (fill_rank3 if idx == 3 else None))
        for st in students:
            row_cells = [
                (1, f"第 {idx} 名", align_center, rank_fill, font_red_bold if idx <= 2 else font_bold),
                (2, s, align_left, None, font_bold if idx <= 2 else font_regular),
                (3, cnt, align_center, None, font_bold),
                (4, pct_val, align_center, None, font_red_bold if idx <= 2 else font_regular),
                (5, st.get("student_name") or "匿名學員", align_center, None, font_bold),
                (6, st.get("phone") or "-", align_center, None, font_blue_bold),
                (7, st.get("prior_experience") or "未填寫", align_center, None, font_regular),
                (8, st.get("followup_interest_topic") or "建議推薦對應痛點之進階實戰班", align_left, None, font_regular)
            ]
            for col_idx, val_c, algn, fill_bg, fnt_c in row_cells:
                cell = ws2.cell(row=cur_row, column=col_idx, value=val_c)
                cell.alignment = algn
                cell.font = fnt_c
                if fill_bg:
                    cell.fill = fill_bg
                cell.border = border_cell
            ws2.row_dimensions[cur_row].height = 22
            cur_row += 1

    ws2.column_dimensions["A"].width = 12
    ws2.column_dimensions["B"].width = 38
    ws2.column_dimensions["C"].width = 12
    ws2.column_dimensions["D"].width = 14
    ws2.column_dimensions["E"].width = 16
    ws2.column_dimensions["F"].width = 18
    ws2.column_dimensions["G"].width = 18
    ws2.column_dimensions["H"].width = 38

    # ========================================================
    # 【工作表 3】預約時段與贈課跟進名冊 (專員專用 CRM 聯絡表)
    # ========================================================
    ws3 = wb.create_sheet(title="預約時段與贈課跟進名冊")
    ws3.sheet_properties.tabColor = "2563EB"

    ws3.merge_cells("A1:J1")
    t3 = ws3["A1"]
    t3.value = "🎁 學員預約即將開課時段 ＆ 線上單元課兌換聯繫跟進名冊"
    t3.font = font_main_title
    t3.fill = fill_sec_exp
    t3.alignment = align_center
    ws3.row_dimensions[1].height = 36

    headers_ws3 = ["序號", "填單時間", "學員姓名", "聯絡手機", "LINE ID", "Email", "欲兌換線上單元課", "預約後續線上直播時段", "延伸進階主題學習意願", "學員起點背景"]
    for col_idx, h in enumerate(headers_ws3, 1):
        cell = ws3.cell(row=2, column=col_idx, value=h)
        cell.font = font_tbl_hdr
        cell.fill = fill_tbl_hdr
        cell.alignment = align_center
        cell.border = border_tbl_hdr
    ws3.row_dimensions[2].height = 24

    cur_row = 3
    for idx, r in enumerate(responses, 1):
        row_cells = [
            (1, idx, align_center, None, font_bold),
            (2, r.get("timestamp") or "-", align_center, None, font_regular),
            (3, r.get("student_name") or "匿名學員", align_center, None, font_bold),
            (4, r.get("phone") or "-", align_center, None, font_blue_bold),
            (5, r.get("line_id") or "-", align_center, None, font_regular),
            (6, r.get("email") or "-", align_left, None, font_regular),
            (7, r.get("selected_reward_course") or "無需兌換 (純回饋)", align_left, None, font_bold),
            (8, r.get("followup_schedules_selected") or "未勾選時段", align_left, None, font_orange_bold),
            (9, r.get("followup_interest_topic") or "未填寫", align_left, None, font_regular),
            (10, r.get("prior_experience") or "未填寫", align_center, None, font_regular)
        ]
        fill_bg = fill_zebra if idx % 2 == 0 else None
        for col_idx, val_c, algn, fill_custom, fnt_c in row_cells:
            cell = ws3.cell(row=cur_row, column=col_idx, value=val_c)
            cell.alignment = algn
            cell.font = fnt_c
            if fill_bg:
                cell.fill = fill_bg
            cell.border = border_cell
        ws3.row_dimensions[cur_row].height = 22
        cur_row += 1

    ws3.column_dimensions["A"].width = 8
    ws3.column_dimensions["B"].width = 20
    ws3.column_dimensions["C"].width = 14
    ws3.column_dimensions["D"].width = 16
    ws3.column_dimensions["E"].width = 14
    ws3.column_dimensions["F"].width = 26
    ws3.column_dimensions["G"].width = 34
    ws3.column_dimensions["H"].width = 38
    ws3.column_dimensions["I"].width = 30
    ws3.column_dimensions["J"].width = 16

    # ========================================================
    # 【工作表 4】原聲留言與心聲清單
    # ========================================================
    ws4 = wb.create_sheet(title="原聲留言與心聲清單")
    ws4.sheet_properties.tabColor = "7C3AED"

    ws4.merge_cells("A1:F1")
    t4 = ws4["A1"]
    t4.value = "💬 學員原聲文字評語 ＆ 講師／助教／課後建議清單"
    t4.font = font_main_title
    t4.fill = fill_sec_reward
    t4.alignment = align_center
    ws4.row_dimensions[1].height = 36

    headers_ws4 = ["序號", "填單時間", "學員姓名", "回饋類別", "滿意評分", "學員原聲文字評語與建議"]
    for col_idx, h in enumerate(headers_ws4, 1):
        cell = ws4.cell(row=2, column=col_idx, value=h)
        cell.font = font_tbl_hdr
        cell.fill = fill_tbl_hdr
        cell.alignment = align_center
        cell.border = border_tbl_hdr
    ws4.row_dimensions[2].height = 24

    cur_row = 3
    comment_idx = 1
    for r in responses:
        name = r.get("student_name") or "匿名學員"
        time_str = r.get("timestamp") or "-"

        inst_c = (r.get("instructor_comment") or "").strip()
        if inst_c:
            row_cells = [
                (1, comment_idx, align_center, None, font_bold),
                (2, time_str, align_center, None, font_regular),
                (3, name, align_center, None, font_bold),
                (4, "👨‍🏫 講師授課評語", align_center, None, font_orange_bold),
                (5, f"{r.get('instructor_rating')} ★" if r.get('instructor_rating') else "-", align_center, None, font_bold),
                (6, inst_c, align_left, None, font_regular)
            ]
            for col_idx, val_c, algn, fill_bg, fnt_c in row_cells:
                cell = ws4.cell(row=cur_row, column=col_idx, value=val_c)
                cell.alignment = algn
                cell.font = fnt_c
                cell.border = border_cell
            ws4.row_dimensions[cur_row].height = 24
            cur_row += 1
            comment_idx += 1

        fb_t = (r.get("feedback_text") or "").strip()
        if fb_t:
            row_cells = [
                (1, comment_idx, align_center, None, font_bold),
                (2, time_str, align_center, None, font_regular),
                (3, name, align_center, None, font_bold),
                (4, "💬 學員心聲建議", align_center, None, font_blue_bold),
                (5, f"NPS {r.get('nps_score')}" if r.get('nps_score') else "-", align_center, None, font_bold),
                (6, fb_t, align_left, None, font_regular)
            ]
            for col_idx, val_c, algn, fill_bg, fnt_c in row_cells:
                cell = ws4.cell(row=cur_row, column=col_idx, value=val_c)
                cell.alignment = algn
                cell.font = fnt_c
                cell.border = border_cell
            ws4.row_dimensions[cur_row].height = 24
            cur_row += 1
            comment_idx += 1

        ta_c = (r.get("ta_comment") or "").strip()
        if ta_c:
            row_cells = [
                (1, comment_idx, align_center, None, font_bold),
                (2, time_str, align_center, None, font_regular),
                (3, name, align_center, None, font_bold),
                (4, "🤝 助教支援反饋", align_center, None, font_bold),
                (5, f"{r.get('ta_rating')} ★" if r.get('ta_rating') else "-", align_center, None, font_bold),
                (6, ta_c, align_left, None, font_regular)
            ]
            for col_idx, val_c, algn, fill_bg, fnt_c in row_cells:
                cell = ws4.cell(row=cur_row, column=col_idx, value=val_c)
                cell.alignment = algn
                cell.font = fnt_c
                cell.border = border_cell
            ws4.row_dimensions[cur_row].height = 24
            cur_row += 1
            comment_idx += 1

    ws4.column_dimensions["A"].width = 8
    ws4.column_dimensions["B"].width = 20
    ws4.column_dimensions["C"].width = 14
    ws4.column_dimensions["D"].width = 20
    ws4.column_dimensions["E"].width = 12
    ws4.column_dimensions["F"].width = 65

    # ========================================================
    # 【工作表 5】原始填答逐筆明細
    # ========================================================
    ws5 = wb.create_sheet(title="原始填答逐筆明細")
    ws5.sheet_properties.tabColor = "475569"

    raw_fields = [
        ("timestamp", "填答時間", 20),
        ("class_id", "班級代碼", 18),
        ("student_name", "學員姓名", 14),
        ("phone", "手機號碼", 16),
        ("line_id", "LINE ID", 14),
        ("email", "Email", 24),
        ("prior_experience", "起點背景", 16),
        ("key_progress", "核心進步收穫", 28),
        ("struggle_point", "主要卡關點", 28),
        ("instructor_rating", "講師評分", 12),
        ("instructor_comment", "講師原聲評語", 34),
        ("course_rating", "課程評分", 12),
        ("ta_rating", "助教評分", 12),
        ("ta_comment", "助教反饋評語", 24),
        ("platform_experience", "直播平台體驗", 18),
        ("nps_score", "淨推薦值(NPS)", 14),
        ("selected_reward_course", "勾選兌換之線上單元課", 30),
        ("wants_reward", "是否有意願兌換", 14),
        ("followup_interest_topic", "延伸進階主題意願", 28),
        ("followup_schedules_selected", "預約即將開課時段", 32),
        ("feedback_text", "學員心聲建議", 32)
    ]

    for col_idx, (fn, label, width) in enumerate(raw_fields, 1):
        cell = ws5.cell(row=1, column=col_idx, value=label)
        cell.font = font_tbl_hdr
        cell.fill = fill_tbl_hdr
        cell.alignment = align_center
        cell.border = border_tbl_hdr
        col_letter = get_column_letter(col_idx)
        ws5.column_dimensions[col_letter].width = width
    ws5.row_dimensions[1].height = 25

    cur_row = 2
    for idx, r in enumerate(responses, 1):
        fill_bg = fill_zebra if idx % 2 == 0 else None
        for col_idx, (fn, label, _) in enumerate(raw_fields, 1):
            val = r.get(fn, "")
            cell = ws5.cell(row=cur_row, column=col_idx, value=val)
            cell.font = font_regular
            cell.border = border_cell
            if fn in ["timestamp", "class_id", "student_name", "phone", "line_id", "instructor_rating", "course_rating", "ta_rating", "nps_score", "wants_reward"]:
                cell.alignment = align_center
            else:
                cell.alignment = align_left
            if fill_bg:
                cell.fill = fill_bg
        ws5.row_dimensions[cur_row].height = 20
        cur_row += 1

    return wb

def export_comprehensive_xlsx_bytes(responses: list, class_info: dict, class_id: str) -> bytes:
    wb = build_comprehensive_workbook(responses, class_info, class_id)
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()
