import pandas as pd
from typing import Dict, Any, List
from core.state import SurveyAnalysisState

class CrossCorrelationAgent:
    """Agent 4: 交叉因果與根因診斷代理人 (Cross-Correlation Diagnostician)"""
    def __init__(self, llm_client=None):
        self.name = "交叉歸因代理 (Correlation Agent)"
        self.llm_client = llm_client

    def run(self, state: SurveyAnalysisState) -> SurveyAnalysisState:
        teacher_label = state.teacher_name or "講師"
        state.log(self.name, "start", f"進行【{state.course_name}】學員背景與學習痛點交叉歸因分析...")

        df = state.df
        if df is None or len(df) == 0:
            state.cross_correlations = {
                "segment_ratings": {},
                "struggles_by_exp": {},
                "key_insights": []
            }
            state.log(self.name, "done", "目前尚無問卷資料供交叉歸因分析。")
            return state

        # 交叉分析 1: 各背景學員在各維度的滿意度均分
        segment_ratings = {}
        if "prior_experience" in df.columns:
            for exp, group in df.groupby("prior_experience"):
                segment_ratings[str(exp)] = {
                    "count": len(group),
                    "instructor_avg": round(float(group["instructor_rating"].mean()), 2) if "instructor_rating" in group else 5.0,
                    "course_avg": round(float(group["course_rating"].mean()), 2) if "course_rating" in group else 5.0,
                    "nps_avg": round(float(group["nps_score"].mean()), 2) if "nps_score" in group else 10.0
                }

        # 交叉分析 2: 各背景學員之卡關點分佈
        struggles_by_exp = {}
        if "prior_experience" in df.columns and "struggle_point" in df.columns:
            for exp, group in df.groupby("prior_experience"):
                counts = group["struggle_point"].value_counts().to_dict()
                struggles_by_exp[str(exp)] = {str(k): int(v) for k, v in counts.items()}

        # 深度因果洞察（動態依據真實填答產生）
        key_insights = []

        all_struggles = df["struggle_point"].dropna().tolist() if "struggle_point" in df.columns else []
        all_platforms = df["platform_experience"].dropna().tolist() if "platform_experience" in df.columns else []

        # 1. 檢視節奏問題
        pacing_count = sum(1 for s in all_struggles if any(w in str(s) for w in ["快", "偏快", "跟不上", "暫停"]))
        if pacing_count > 0:
            key_insights.append({
                "finding": "示範節奏與操作同步負荷",
                "evidence": f"本期有 {pacing_count} 位學員反映示範節奏偏快或需要更多停頓思考時間。",
                "root_cause": f"初學者在直播當下需同時觀看示範與實作，{teacher_label}的操作熟練度較高，初學者需要明確的口訣提示與緩衝秒數。"
            })

        # 2. 檢視平台串流
        platform_lag_count = sum(1 for p in all_platforms if any(w in str(p) for w in ["卡頓", "延遲", "中斷"]))
        if platform_lag_count > 0:
            key_insights.append({
                "finding": "直播串流穩定度與回放依賴",
                "evidence": f"有 {platform_lag_count} 位學員回饋直播偶有卡頓或延遲，影響觀看體驗。",
                "root_cause": "受限於學員端個別網路環境或串流推流碼率波動，需確保課後 24 小時內即時釋出高清回放影音。"
            })

        # 3. 檢視自訂或其他卡關點
        custom_struggles = [str(s) for s in all_struggles if "其他" in str(s) or "：" in str(s)]
        if custom_struggles:
            custom_sample = custom_struggles[0].replace("其他：", "").replace("其他:", "")
            key_insights.append({
                "finding": f"學員個別化回饋需求（如『{custom_sample}』）",
                "evidence": f"學員特別提出自訂反饋：「{custom_sample}」。",
                "root_cause": "不同學員起點期待多元，針對個別化需求提供定向答疑可有效強化口碑黏著度。"
            })

        # 4. 助教或常態表現
        avg_ta = state.quant_metrics.get("avg_ta", 5.0)
        if avg_ta >= 4.0:
            key_insights.append({
                "finding": "助教與課堂支援發揮護航效益",
                "evidence": f"助教服務滿意度高達 {avg_ta}★，有效解答課堂疑難。",
                "root_cause": "及時的助教互動與課後支援能即時補位課堂疑問，大幅提升整體完課滿意度。"
            })

        if not key_insights:
            key_insights.append({
                "finding": f"【{state.course_name}】整體教學成效卓越",
                "evidence": f"講師滿意度達 {state.quant_metrics.get('avg_instructor', 5.0)}★，學員反饋學習吸收充實。",
                "root_cause": f"{teacher_label} 的教學結構完整，示範清晰，高度契合學員需求。"
            })

        state.cross_correlations = {
            "segment_ratings": segment_ratings,
            "struggles_by_exp": struggles_by_exp,
            "key_insights": key_insights
        }

        state.log(
            self.name, 
            "done", 
            f"交叉歸因完成！成功萃取 {len(key_insights)} 項學習痛點與教學成效核心洞察。"
        )
        return state
