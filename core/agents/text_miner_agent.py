import re
from typing import Dict, Any, List
from core.state import SurveyAnalysisState

class TextMinerAgent:
    """Agent 3: 質化語意與情緒挖掘代理人 (Text Sentiment & Theme Miner)"""
    def __init__(self, llm_client=None):
        self.name = "質化情緒代理 (Text Miner Agent)"
        self.llm_client = llm_client

    def run(self, state: SurveyAnalysisState) -> SurveyAnalysisState:
        teacher_label = state.teacher_name or "講師"
        state.log(self.name, "start", f"深掘學員給{teacher_label}與助教的開放式原聲回饋...")

        df = state.df
        if df is None or len(df) == 0:
            state.text_insights = {
                "gold_quotes": [],
                "alert_quotes": [],
                "ta_highlights": [],
                "keyword_tags": [],
                "sentiment_ratio": {
                    "positive": 100.0,
                    "constructive": 0.0
                }
            }
            state.log(self.name, "done", "質化分析完成：目前此班級尚無文字回饋資料。")
            return state

        gold_quotes = []
        alert_quotes = []

        # 關鍵詞群
        praise_keywords = ["清晰", "任督二脈", "魔法", "療癒", "耐心", "迷人", "透徹", "聲音", "最棒", "用心", "讚", "超棒", "清楚", "收穫", "豐富", "喜歡", "順暢", "好棒"]
        alert_keywords = ["快", "抽象", "跟不上", "暫停", "重看", "停頓", "自創", "依賴", "卡", "問題", "難", "不懂", "吃力", "？", "?", "延遲", "改善", "建議"]

        # 分類講師評語
        for _, row in df.iterrows():
            name = str(row.get("student_name", "學員"))
            comm = str(row.get("instructor_comment", "")).strip()
            score = float(row.get("instructor_rating", 5.0))
            exp = str(row.get("prior_experience", "學員"))

            if not comm or comm.lower() in ("無", "none", "nan", "沒有", "還行", "還好", "-"):
                continue

            is_alert = any(k in comm for k in alert_keywords) or score <= 3.5
            if is_alert:
                alert_quotes.append({
                    "student_name": name,
                    "experience": exp,
                    "rating": score,
                    "quote": comm,
                    "tag": "教學節奏與問題回饋"
                })
            else:
                gold_quotes.append({
                    "student_name": name,
                    "experience": exp,
                    "rating": score,
                    "quote": comm,
                    "tag": "講師教學魅力與收穫"
                })

        # 助教好評精選
        ta_highlights = []
        for _, row in df.iterrows():
            ta_comm = str(row.get("ta_comment", "")).strip()
            if ta_comm and len(ta_comm) >= 2 and ta_comm.lower() not in ("無", "none", "nan", "沒有", "-"):
                ta_highlights.append({
                    "student_name": str(row.get("student_name", "學員")),
                    "quote": ta_comm
                })

        # 動態統計主題標籤（依據實際卡關點與回饋）
        keyword_tags = []
        if "struggle_point" in df.columns:
            s_counts = df["struggle_point"].value_counts().to_dict()
            for s_text, count in s_counts.items():
                s_str = str(s_text).strip()
                if not s_str or s_str.lower() in ("nan", "none"):
                    continue
                tag_type = "positive" if any(w in s_str for w in ["順暢", "剛好", "充實", "無"]) else "alert"
                keyword_tags.append({
                    "tag": s_str if len(s_str) <= 20 else s_str[:19] + "...",
                    "count": int(count),
                    "type": tag_type
                })

        total_analyzed = len(gold_quotes) + len(alert_quotes)
        if total_analyzed > 0:
            pos_ratio = round((len(gold_quotes) / total_analyzed) * 100, 1)
        else:
            pos_ratio = 100.0

        state.text_insights = {
            "gold_quotes": gold_quotes[:8],
            "alert_quotes": alert_quotes[:6],
            "ta_highlights": ta_highlights[:5],
            "keyword_tags": keyword_tags[:8],
            "sentiment_ratio": {
                "positive": pos_ratio,
                "constructive": round(100.0 - pos_ratio, 1)
            }
        }

        state.log(
            self.name,
            "done",
            f"質化分析完成：共萃取 {len(gold_quotes)} 則口碑金句、{len(alert_quotes)} 則關鍵反饋，正面情緒比 {pos_ratio}%！"
        )
        return state
