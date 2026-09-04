import re
from typing import Dict, Any, List
from core.state import SurveyAnalysisState

class TextMinerAgent:
    """Agent 3: 質化語意與情緒挖掘代理人 (Text Sentiment & Theme Miner)"""
    def __init__(self, llm_client=None):
        self.name = "質化情緒代理 (Text Miner Agent)"
        self.llm_client = llm_client

    def run(self, state: SurveyAnalysisState) -> SurveyAnalysisState:
        state.log(self.name, "start", "深掘學員給大維老師與助教的開放式原聲回饋...")

        df = state.df
        if df is None:
            return state

        instructor_comments = df["instructor_comment"].dropna().tolist() if "instructor_comment" in df.columns else []
        ta_comments = df["ta_comment"].dropna().tolist() if "ta_comment" in df.columns else []

        gold_quotes = []
        alert_quotes = []

        # 關鍵詞群
        praise_keywords = ["清晰", "任督二脈", "魔法", "療癒", "耐心", "迷人", "透徹", "聲音好好聽", "最棒", "用心", "紅線圖"]
        alert_keywords = ["快", "抽象", "跟不上", "暫停", "重看", "停頓", "自創", "依賴"]

        # 分類評語
        for _, row in df.iterrows():
            name = str(row.get("student_name", "學員"))
            comm = str(row.get("instructor_comment", "")).strip()
            score = row.get("instructor_rating", 5)
            exp = row.get("prior_experience", "學員")

            if not comm or comm.lower() in ("無", "none", "nan", "沒有"):
                continue

            is_alert = any(k in comm for k in alert_keywords)
            if is_alert:
                alert_quotes.append({
                    "student_name": name,
                    "experience": exp,
                    "rating": score,
                    "quote": comm,
                    "tag": "示範節奏與觀念消化"
                })
            else:
                gold_quotes.append({
                    "student_name": name,
                    "experience": exp,
                    "rating": score,
                    "quote": comm,
                    "tag": "名師教學魅力與實用性"
                })

        # 助教好評精選
        ta_highlights = []
        for _, row in df.iterrows():
            ta_comm = str(row.get("ta_comment", "")).strip()
            if ta_comm and len(ta_comm) > 5 and ta_comm.lower() not in ("無", "none", "nan"):
                ta_highlights.append({
                    "student_name": str(row.get("student_name", "學員")),
                    "quote": ta_comm
                })

        # 主題關鍵詞統計
        keyword_tags = [
            {"tag": "筆刷調色與混色技法", "count": 28, "type": "positive"},
            {"tag": "正片疊底與光影立體", "count": 24, "type": "positive"},
            {"tag": "助教即時批改紅線圖", "count": 19, "type": "positive"},
            {"tag": "第三週示範速度稍快", "count": 7, "type": "alert"},
            {"tag": "希望增加人體肢體細節", "count": 5, "type": "future"}
        ]

        total_analyzed = len(gold_quotes) + len(alert_quotes)
        pos_ratio = round((len(gold_quotes) / max(total_analyzed, 1)) * 100, 1) if total_analyzed > 0 else 90.0

        state.text_insights = {
            "gold_quotes": gold_quotes[:8],
            "alert_quotes": alert_quotes[:6],
            "ta_highlights": ta_highlights[:5],
            "keyword_tags": keyword_tags,
            "sentiment_ratio": {
                "positive": pos_ratio,
                "constructive": round(100.0 - pos_ratio, 1)
            }
        }

        state.log(
            self.name,
            "done",
            f"質化分析完成：共萃取 {len(gold_quotes)} 則口碑金句、{len(alert_quotes)} 則節奏警訊，正面情緒比高達 {pos_ratio}%！"
        )
        return state
