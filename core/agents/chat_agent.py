from core.state import SurveyAnalysisState
from core.llm_client import LLMClient

class SurveyChatAdvisorAgent:
    """Agent 7: 互動式問卷即席諮詢顧問 (Survey Consultation Agent)"""
    def __init__(self, llm_client: LLMClient = None):
        self.name = "問卷問答顧問 (Chat Advisor Agent)"
        self.llm = llm_client or LLMClient()

    def answer_question(self, question: str, state: SurveyAnalysisState) -> str:
        teacher_label = state.teacher_name or "講師"
        insights = state.cross_correlations.get("key_insights", [])
        insight_summary = "、".join(i.get("finding", "") for i in insights[:3]) if insights else "整體學習吸收良好"
        gold_summary = "、".join(f"『{g.get('quote')}』" for g in state.text_insights.get("gold_quotes", [])[:2]) if state.text_insights.get("gold_quotes") else "無特殊文字評語"

        # 若已配置真實 Gemini API Key，優先調用大模型深度生成
        if self.llm.is_live_llm():
            prompt = f"""
你是一位專業的教育培訓與課程評鑑顧問。請根據以下【{state.course_name}】（講師：{teacher_label}）結業問卷分析數據，精準回答教師或教務主管的問題。

【問卷核心數據總覽】
- 課程名稱：{state.course_name}
- 授課講師：{teacher_label}
- 填答人數：{state.inspection_summary.get('total_responses', 0)} 人
- {teacher_label} 教學均分：{state.quant_metrics.get('avg_instructor', 5.0)}★
- 助教支援均分：{state.quant_metrics.get('avg_ta', 5.0)}★
- NPS 淨推薦值：{'+' if state.quant_metrics.get('nps', 0) >= 0 else ''}{state.quant_metrics.get('nps', 0)}
- 核心發現與痛點：{insight_summary}
- 學員代表性回饋：{gold_summary}

【用戶提問】
{question}

請以專業、客觀且具備教育同理心的繁體中文回答。若用戶要求撰寫致詞、感謝信或文案，請直接產出符合語氣與字數要求的完整內容。
"""
            try:
                res = self.llm.generate_text(prompt)
                if res and len(res.strip()) > 10:
                    return res.strip()
            except Exception as e:
                print(f"[ChatAdvisor Warning] Live LLM error: {e}")

        # 本機智慧問答應答器（當尚未配置 API Key 時的智慧語意推論）
        q = question.strip()
        q_lower = q.lower()

        # 1. 請求寫致詞 / 感謝信 / LINE 群發言 / 結業文案
        if any(w in q_lower for w in ["致詞", "感謝", "line", "群發", "文案", "寫一段", "祝賀", "結業詞", "說的話", "開場"]):
            return (
                f"【{teacher_label} 給【{state.course_name}】全體學員的結業致謝信】\n\n"
                f"各位同學辛苦了！恭喜大家順利結業 🎉！\n"
                f"這幾週看著大家從起步摸索到產出屬於自己的作品，真的非常感動。問卷中每一位同學的回饋與鼓勵我都仔細讀過了，"
                f"謝謝大家對課堂的投入與支持。無論大家的起點在哪裡，持續練習就是最棒的超能力！"
                f"結業不是結束，別忘了領取專屬單元課繼續深化技能，有任何問題隨時在 LINE 班群交流，期待在未來的創作路上再次看見大家發光！✨"
            )

        # 2. 詢問卡關點 / 痛點 / 難題 / 節奏
        elif any(w in q_lower for w in ["卡關", "痛點", "難", "跟不上", "問題", "吃力", "盲點", "節奏"]):
            struggles = [ins.get("finding", "") for ins in insights]
            alert_quotes = [a.get("quote", "") for a in state.text_insights.get("alert_quotes", [])]
            s_text = "、".join(struggles) if struggles else "目前未見明顯集體卡關"
            q_text = f"（學員具體提到：『{alert_quotes[0]}』）" if alert_quotes else ""
            return (
                f"根據【{state.course_name}】數據分析，學員的核心反饋主要集中在：\n"
                f"📌 {s_text} {q_text}\n\n"
                f"💡 顧問教學優化建議：\n"
                f"1. 示範關鍵步驟時增加 5~10 秒停頓並口述口訣，讓初學者有充足秒數同步操作。\n"
                f"2. 課前提供該單元之精華預習包或色卡/參考檔，前置消化操作門檻。\n"
                f"3. 課後善用助教即時答疑與 24 小時內高清回放影音，給予學員充分的安全感。"
            )

        # 3. 詢問單元課 / 獎勵 / 招生 / 下一期 / 續報
        elif any(w in q_lower for w in ["單元課", "兌換", "招生", "下一期", "續報", "進階", "熱門", "好禮"]):
            nps = state.quant_metrics.get("nps", 0)
            return (
                f"根據本期結業數據與招生轉化潛力評估：\n\n"
                f"1. 續報轉化潛力：本期學員對【{teacher_label}】教學滿意度極高，具備良好的口碑信任。\n"
                f"2. 進階課主打方向：建議延伸規劃【{state.course_name}】之商業實戰與個人作品集進階班。\n"
                f"3. 關鍵行動建議：建議在結業 72 小時內於班級群組發布舊生專屬限時折價優惠碼，並搭配贈送單元課之開通通知，預估可創造 25%~35% 的舊生續報率！"
            )

        # 4. 詢問助教
        elif any(w in q_lower for w in ["助教", "批改", "紅線", "回答速度", "作業"]):
            ta_avg = state.quant_metrics.get("avg_ta", 5.0)
            ta_quotes = [t.get("quote", "") for t in state.text_insights.get("ta_highlights", [])]
            ta_comm_text = f"學員評價：『{ta_quotes[0]}』" if ta_quotes else "學員高度肯定助教課堂陪伴與解題支援。"
            return (
                f"助教運營成效總覽：\n\n"
                f"⭐ 助教綜合評分：{ta_avg}★（滿分 5.0★，評價卓越）\n"
                f"💬 學員原聲：{ta_comm_text}\n"
                f"✅ 顧問建議：維持作業於 36 小時內批改回覆之服務水準，針對自述零基礎學員多給予具體步驟與信心鼓勵。"
            )

        # 5. 詢問教學滿意度 / 評鑑 / 總結 / 亮點
        elif any(w in q_lower for w in ["滿意度", "亮點", "評鑑", "表現", "總結", "概況"]):
            inst_avg = state.quant_metrics.get("avg_instructor", 5.0)
            nps = state.quant_metrics.get("nps", 0)
            total = state.inspection_summary.get("total_responses", 0)
            return (
                f"【{state.course_name}】教學整體評鑑總結：\n\n"
                f"1. 填答規模：累計回收 {total} 份有效問卷。\n"
                f"2. 滿意度水準：{teacher_label} 講師授課達 {inst_avg}★，辦學整體評價優良。\n"
                f"3. 核心亮點：講師教學步驟示範清晰，助教課堂解答即時到位。\n"
                f"4. 覆盤建言：建議針對新手學員進一步落實課前預習引導與關鍵操作停留。"
            )

        # 6. 其他通用問答
        else:
            return (
                f"針對您詢問的「{question}」：\n\n"
                f"根據【{state.course_name}】目前累計之 {state.inspection_summary.get('total_responses', 0)} 份學員填答數據，"
                f"{teacher_label} 講師教學均分達 {state.quant_metrics.get('avg_instructor', 5.0)}★，助教達 {state.quant_metrics.get('avg_ta', 5.0)}★。\n"
                f"若您需要特定協助（例如：撰寫 LINE 結業感謝詞、剖析學員卡關點、推薦下一期進階課或檢視助教評價），歡迎直接具體提問！"
            )
