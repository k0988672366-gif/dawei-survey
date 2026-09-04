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

        prompt = f"""
你是一位專業的教育培訓與課程評鑑顧問。請根據以下【{state.course_name}】（講師：{teacher_label}）結業問卷分析數據，精準回答教師或教務主管的問題。

【問卷核心數據總覽】
- 填答人數：{state.inspection_summary.get('total_responses', 0)} 人
- {teacher_label} 教學均分：{state.quant_metrics.get('avg_instructor', 5.0)}★
- 助教支援均分：{state.quant_metrics.get('avg_ta', 5.0)}★
- NPS 淨推薦值：{'+' if state.quant_metrics.get('nps', 0) >= 0 else ''}{state.quant_metrics.get('nps', 0)}
- 核心發現與痛點：{insight_summary}
- 學員代表性回饋：{gold_summary}

【用戶提問】
{question}

請以專業、客觀且具備教育同理心的繁體中文回答，條理分明，並提供具體可行的教學與營運建議。
"""
        return self.llm.generate_text(prompt)
