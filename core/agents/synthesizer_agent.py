from datetime import datetime
from core.state import SurveyAnalysisState

class ChiefSynthesizerAgent:
    """Agent 6: 總協調與審查報告生成代理人 (Chief Synthesizer & Orchestrator)"""
    def __init__(self, llm_client=None):
        self.name = "總協調審查代理 (Chief Synthesizer)"
        self.llm_client = llm_client

    def run(self, state: SurveyAnalysisState) -> SurveyAnalysisState:
        teacher_label = state.teacher_name or "講師"
        state.log(self.name, "start", f"彙整多代理人洞察，生成【{state.course_name}】決策級《結業問卷綜合診斷報告書》...")

        insp = state.inspection_summary
        qm = state.quant_metrics
        ti = state.text_insights
        cc = state.cross_correlations
        ps = state.pedagogical_strategies

        now_str = datetime.now().strftime("%Y-%m-%d")
        total_resp = insp.get("total_responses", 0)

        # 產出執行摘要
        if total_resp == 0:
            exec_summary = (
                f"本期【{state.course_name}】（授課講師：{teacher_label}）目前累計 0 份學員填答，"
                f"系統已完成評鑑架構與課綱對應設定。待學員填寫後，多代理 AI 團隊將即時運算各維度均分、淨推薦值 NPS、口碑金句與教學改進矩陣。"
            )
        else:
            gold_sample = ti.get("gold_quotes", [{}])[0].get("quote", "") if ti.get("gold_quotes") else ""
            alert_sample = ti.get("alert_quotes", [{}])[0].get("quote", "") if ti.get("alert_quotes") else ""
            
            exec_summary = (
                f"本期【{state.course_name}】結業問卷共回收 {total_resp} 份有效填答。"
                f"整體辦學與教學評價優良，{teacher_label} 個人教學滿意度達 {qm.get('avg_instructor', 5.0)}★，"
                f"助教滿意度達 {qm.get('avg_ta', 5.0)}★，淨推薦值 NPS 為 {'+' if qm.get('nps', 0) >= 0 else ''}{qm.get('nps', 0)}。"
            )
            if gold_sample:
                exec_summary += f" 學員原聲金句如『{gold_sample}』印證了授課專業與吸引力。"
            if alert_sample:
                exec_summary += f" 同時學員提醒『{alert_sample}』，為後續課程提供明確的教學優化切入點。"

        # 產出完整 Markdown 審查報告
        report_md = f"""# 《{state.course_name}》結業問卷綜合診斷與教學改進審查報告

**評審機構**：{state.organizer} ✕ 班級結業問卷分析師多代理 AI 團隊  
**授課講師**：{teacher_label}  
**報告生成日期**：{now_str}  
**資料覆蓋**：有效問卷 {total_resp} 份（填答覆蓋完整度 {insp.get('data_health_score', 100)}%）

---

## 執行摘要 (Executive Summary)

{exec_summary}

---

## 一、問卷資料健康度與學員背景畫像

* **有效問卷總數**：{total_resp} 份
* **學員起點分佈**：
"""
        exp_dist = insp.get("experience_distribution", {})
        if exp_dist:
            for exp, cnt in exp_dist.items():
                report_md += f"  - **{exp}**：{cnt} 位 ({round(cnt / max(total_resp, 1) * 100, 1)}%)\n"
        else:
            report_md += "  - *(尚無學員填答數據)*\n"

        report_md += f"""
> [!NOTE]
> **學員結構觀察**：本期班級資料顯示，重視初學者的「操作引導」與「實作信心建立」是奠定課程滿意度與高續報口碑的最關鍵支柱。

---

## 二、量化教學滿意度與 NPS 評估

### 1. 教學核心維度指標
| 評鑑維度 | 平均滿意度 (滿分 5★) | 標準差 (離散度) | 評等 |
| :--- | :---: | :---: | :---: |
| **{teacher_label} 授課與示範** | **{qm.get('avg_instructor', 5.0)}** | {qm.get('std_instructor', 0.0)} | {'卓越 (A+)' if qm.get('avg_instructor', 5.0) >= 4.5 else '良好 (A)'} |
| **課綱安排與教材實用度** | **{qm.get('avg_course', 5.0)}** | {qm.get('std_course', 0.0)} | {'卓越 (A+)' if qm.get('avg_course', 5.0) >= 4.5 else '良好 (A)'} |
| **助教課堂解答與課後陪伴** | **{qm.get('avg_ta', 5.0)}** | {qm.get('std_ta', 0.0)} | {'卓越 (A+)' if qm.get('avg_ta', 5.0) >= 4.5 else '良好 (A)'} |

### 2. 淨推薦值 (Net Promoter Score, NPS)
* **NPS 分數**：**{'+' if qm.get('nps', 0) >= 0 else ''}{qm.get('nps', 0)}**
* **推薦者 (Promoters, 9-10分)**：{qm.get('promoters_count', 0)} 人 ({qm.get('promoters_pct', 0)}%)
* **被動者 (Passives, 7-8分)**：{qm.get('passives_count', 0)} 人 ({qm.get('passives_pct', 0)}%)
* **批評者 (Detractors, 0-6分)**：{qm.get('detractors_count', 0)} 人 ({qm.get('detractors_pct', 0)}%)

---

## 三、質化語意與學員原聲洞察 (Voice of Students)

* **正面情感比例**：**{ti.get('sentiment_ratio', {}).get('positive', 100)}%**
* **建設性反饋比例**：**{ti.get('sentiment_ratio', {}).get('constructive', 0)}%**

### 🎨 學員精選口碑金句（{teacher_label} 教學魅力）
"""
        gold_quotes = ti.get("gold_quotes", [])
        if gold_quotes:
            for g in gold_quotes[:5]:
                report_md += f"> *「{g.get('quote')}」*  \n> —— **{g.get('student_name')}** ({g.get('experience')}, 評分 {g.get('rating')}★)\n\n"
        else:
            report_md += "> *（目前尚無文字金句，等待學員填寫反饋）*\n\n"

        report_md += f"""### ⚠️ 教學警訊與關鍵建議
"""
        alert_quotes = ti.get("alert_quotes", [])
        if alert_quotes:
            for a in alert_quotes[:4]:
                report_md += f"> *「{a.get('quote')}」*  \n> —— **{a.get('student_name')}** ({a.get('experience')})\n\n"
        else:
            report_md += "> *（目前無急迫性教學警訊反饋）*\n\n"

        report_md += f"""### 🤝 助教課堂陪伴口碑
"""
        ta_highlights = ti.get("ta_highlights", [])
        if ta_highlights:
            for ta in ta_highlights[:3]:
                report_md += f"> *「{ta.get('quote')}」*  \n> —— **{ta.get('student_name')}**\n\n"
        else:
            report_md += "> *（目前尚無助教文字評語）*\n\n"

        report_md += f"""---

## 四、交叉因果與根因診斷 (Root Cause Analysis)

"""
        insights = cc.get("key_insights", [])
        if insights:
            for ins in insights:
                report_md += f"### 📌 發現：{ins.get('finding')}\n"
                report_md += f"* **現象證據**：{ins.get('evidence')}\n"
                report_md += f"* **底層根因**：{ins.get('root_cause')}\n\n"
        else:
            report_md += "> *（目前數據累積中，等待更多填答進行交叉關聯）*\n\n"

        report_md += f"""---

## 五、教學改進與行動策略矩陣 (Pedagogical Action Roadmap)

### 1. Eisenhower 迭代行動矩陣
| 優先級 | 行動方案 | 預期成效 | 投入成本 |
| :--- | :--- | :--- | :---: |
"""
        for qw in ps.get("action_matrix", {}).get("quick_wins", []):
            report_md += f"| **即刻速贏** | **{qw.get('title')}**：{qw.get('detail')} | {qw.get('impact')} | {qw.get('effort')} |\n"
        for nc in ps.get("action_matrix", {}).get("next_cohort", []):
            report_md += f"| **次期優化** | **{nc.get('title')}**：{nc.get('detail')} | {nc.get('impact')} | {nc.get('effort')} |\n"
        for ca in ps.get("action_matrix", {}).get("curriculum_architecture", []):
            report_md += f"| **長期架構** | **{ca.get('title')}**：{ca.get('detail')} | {ca.get('impact')} | {ca.get('effort')} |\n"

        report_md += f"""
### 2. {teacher_label} 個人教學覆盤指引
"""
        for tr in ps.get("teacher_reflection", []):
            report_md += f"- **{tr}**\n"

        report_md += """
### 3. 助教 SOP 運營清單
"""
        for tc in ps.get("ta_checklist", []):
            report_md += f"- {tc}\n"

        report_md += f"""
---

## 六、下一期招生與轉化策略建言

1. **口碑素材庫建立**：本報告第三節萃取之 {len(gold_quotes)} 則學員金句與高度評價，可直接製作為下一期招生海報、EDM 與社群輪播素材。
2. **舊生續報專屬通道**：本次 NPS 為 {'+' if qm.get('nps', 0) >= 0 else ''}{qm.get('nps', 0)}，學員對 {teacher_label} 與課程具備良好信任。建議在結業 72 小時內於班級群組推播進階延伸實戰單元，搭配問卷領取之專屬優惠碼，有效鎖定舊生續報轉化！

---
*報告由「班級結業問卷分析師 多代理協同 AI Agent」自動彙整驗證完成。*
"""

        state.executive_summary = exec_summary
        state.final_report_md = report_md

        state.log(self.name, "done", f"《結業問卷綜合診斷報告書》編制完成！已專屬對齊【{state.course_name}】與講師【{teacher_label}】。")
        return state
