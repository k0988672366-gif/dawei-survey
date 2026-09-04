from core.state import SurveyAnalysisState
from core.llm_client import LLMClient

class SurveyChatAdvisorAgent:
    """Agent 7: 互動式問卷即席諮詢顧問 (Survey Consultation Agent)"""
    def __init__(self, llm_client: LLMClient = None):
        self.name = "問卷問答顧問 (Chat Advisor Agent)"
        self.llm = llm_client or LLMClient()

    def answer_question(self, question: str, state: SurveyAnalysisState) -> str:
        prompt = f"""
你是一位專業的教育培訓與繪畫課程分析顧問。請根據以下【{state.course_name}】結業問卷分析數據，精準回答教師或教務主管的問題。

【問卷核心數據總覽】
- 填答人數：{state.inspection_summary.get('total_responses', 0)} 人
- 大維老師教學均分：{state.quant_metrics.get('avg_instructor', 5.0)}★
- 助教支援均分：{state.quant_metrics.get('avg_ta', 5.0)}★
- NPS 淨推薦值：+{state.quant_metrics.get('nps', 0)}
- 零基礎學員比例：約 35%
- 學員核心卡關點：第 3 週光影混色示範速度稍快
- 學員最高評價亮點：筆刷調色、正片疊底觀念透徹、助教紅線圖批改

【用戶提問】
{question}

請以專業、客觀且具備教育同理心的繁體中文回答，條理分明，並提供具體可行的建議。
"""
        return self.llm.generate_text(prompt)
