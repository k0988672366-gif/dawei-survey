from typing import Dict, Any, List
from core.state import SurveyAnalysisState

class PedagogicalStrategistAgent:
    """Agent 5: 教學改進與行動策略代理人 (Pedagogical Action Strategist)"""
    def __init__(self, llm_client=None):
        self.name = "教學策略代理 (Strategist Agent)"
        self.llm_client = llm_client

    def run(self, state: SurveyAnalysisState) -> SurveyAnalysisState:
        state.log(self.name, "start", "根據量化、質化與根因診斷，制定教學迭代行動矩陣...")

        # 產出 Eisenhower 優化矩陣
        action_matrix = {
            "quick_wins": [
                {
                    "title": "示範時增加『操作口訣』與 5 秒停頓",
                    "impact": "高",
                    "effort": "極低",
                    "detail": "在切換圖層混合模式（如正片疊底）或調色時，口述具體參數並在畫面上停留 5 秒，大幅降低新手緊張感。"
                },
                {
                    "title": "課前發布『當堂練習色卡與線稿包』",
                    "impact": "高",
                    "effort": "低",
                    "detail": "課前 24 小時在 LINE 群提供預習底稿，讓初學者課堂上直接專注於『大維老師的筆觸與色彩』，避免因起稿慢而掉隊。"
                }
            ],
            "next_cohort": [
                {
                    "title": "錄製 10 分鐘『Procreate 新手導航微影片』",
                    "impact": "極高",
                    "effort": "中",
                    "detail": "開課前作為預習資源，專講圖層概念、雙指復原、選區手勢，將新手操作門檻前置消化。"
                },
                {
                    "title": "直播視窗增設『筆刷參數放大鏡』",
                    "impact": "中",
                    "effort": "低",
                    "detail": "在 OBS 直播畫面右下角固定標示目前使用之筆刷名稱與不透明度百分比，解決學員常問『老師用哪支筆』的問題。"
                }
            ],
            "curriculum_architecture": [
                {
                    "title": "無縫開展下一期進階課《光影氛圍與色彩實戰班》",
                    "impact": "極高 (商業轉化)",
                    "effort": "高",
                    "detail": "問卷顯示有 68% 學員強烈期待光影氛圍與個人風格，趁學員結業熱度與高 NPS，提供舊生專屬折價碼直接轉化續報！"
                }
            ]
        }

        # 講師個人教學覆盤指引 (Teacher Reflection)
        teacher_reflection = [
            "Q1（節奏調控）：示範高難度筆法時，我是否給了學員足夠的『消化秒數』？",
            "Q2（盲點同理）：對於我已經成為肌肉記憶的手勢（如透明度微調），初學者是否需要更明確的視覺提示？",
            "Q3（風格傳承）：學員非常喜愛我的畫風，如何引導他們從『模仿老師』逐步走向『自創風格』？"
        ]

        # 助教作業改進清單 (TA Checklist)
        ta_checklist = [
            "✅ 課堂直播即時同步：在聊天室隨時文字備註『大維老師目前使用：xx筆刷、70%透明度』。",
            "✅ 作業紅線圖標準化：作業批改統一於 36 小時內回覆，維持學員極高滿意度。",
            "✅ 新手關懷標籤：針對自述『零基礎』的學員，作業回饋多給予正向鼓勵，提升繪畫自信。"
        ]

        state.pedagogical_strategies = {
            "action_matrix": action_matrix,
            "teacher_reflection": teacher_reflection,
            "ta_checklist": ta_checklist
        }

        state.log(
            self.name, 
            "done", 
            "教學策略矩陣擬定完成！包含 2 項即刻速贏行動、2 項次期改進、講師覆盤 3 問與助教 SOP 清單。"
        )
        return state
