from typing import Callable, Optional
from core.state import SurveyAnalysisState
from core.llm_client import LLMClient
from core.agents.inspector_agent import InspectorAgent
from core.agents.quant_agent import QuantAgent
from core.agents.text_miner_agent import TextMinerAgent
from core.agents.correlation_agent import CrossCorrelationAgent
from core.agents.strategist_agent import PedagogicalStrategistAgent
from core.agents.synthesizer_agent import ChiefSynthesizerAgent
from core.agents.chat_agent import SurveyChatAdvisorAgent

class SurveyOrchestrator:
    """多代理協同分析調度中樞 (Multi-Agent Pipeline Orchestrator)"""
    def __init__(self, api_key: Optional[str] = None):
        self.llm_client = LLMClient(api_key=api_key)
        self.agent1 = InspectorAgent(self.llm_client)
        self.agent2 = QuantAgent(self.llm_client)
        self.agent3 = TextMinerAgent(self.llm_client)
        self.agent4 = CrossCorrelationAgent(self.llm_client)
        self.agent5 = PedagogicalStrategistAgent(self.llm_client)
        self.agent6 = ChiefSynthesizerAgent(self.llm_client)
        self.agent7 = SurveyChatAdvisorAgent(self.llm_client)

    def run_pipeline(
        self, 
        state: SurveyAnalysisState, 
        progress_callback: Optional[Callable[[str, int, str], None]] = None
    ) -> SurveyAnalysisState:
        """執行 6 大代理人協同分析流水線"""
        def update_progress(agent_name: str, percent: int, msg: str):
            if progress_callback:
                progress_callback(agent_name, percent, msg)

        # 步驟 1: 資料檢驗
        update_progress(self.agent1.name, 15, "檢驗問卷欄位完整性與資料健康度...")
        state = self.agent1.run(state)

        # 步驟 2: 量化與 NPS
        update_progress(self.agent2.name, 35, "計算滿意度指標與淨推薦值 NPS...")
        state = self.agent2.run(state)

        # 步驟 3: 質化情緒與主題
        update_progress(self.agent3.name, 55, "深掘學員原聲評價與正負向情緒主題...")
        state = self.agent3.run(state)

        # 步驟 4: 交叉歸因
        update_progress(self.agent4.name, 75, "關聯學員起點與卡關點，剖析教學根因...")
        state = self.agent4.run(state)

        # 步驟 5: 教學行動策略
        update_progress(self.agent5.name, 90, "擬定教學行動矩陣與講師覆盤清單...")
        state = self.agent5.run(state)

        # 步驟 6: 總協調綜合報告
        update_progress(self.agent6.name, 100, "編制高階結業問卷審查報告書...")
        state = self.agent6.run(state)

        return state

    def ask_advisor(self, question: str, state: SurveyAnalysisState) -> str:
        """調用 Agent 7 即席諮詢顧問"""
        return self.agent7.answer_question(question, state)
