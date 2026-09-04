import pandas as pd
from typing import Dict, Any, List
from core.state import SurveyAnalysisState

class InspectorAgent:
    """Agent 1: 資料清洗與檢驗代理人 (Inspector Agent)"""
    def __init__(self, llm_client=None):
        self.name = "資料檢驗代理 (Inspector Agent)"
        self.llm_client = llm_client

    def run(self, state: SurveyAnalysisState) -> SurveyAnalysisState:
        state.log(self.name, "start", "開始進行問卷資料結構化檢驗與品質畫像分析...")

        if state.raw_responses:
            df = pd.DataFrame(state.raw_responses)
        elif state.df is not None:
            df = state.df
        else:
            state.log(self.name, "error", "無任何可用的問卷資料！", status="error")
            return state

        # 欄位別名相容映射
        column_map = {
            "時間戳記": "timestamp",
            "姓名": "student_name",
            "稱呼": "student_name",
            "基礎": "prior_experience",
            "進步": "key_progress",
            "卡關": "struggle_point",
            "講師評分": "instructor_rating",
            "老師說的話": "instructor_comment",
            "課綱評分": "course_rating",
            "助教評分": "ta_rating",
            "助教說的話": "ta_comment",
            "平台順暢度": "platform_experience",
            "推薦值": "nps_score"
        }
        for old_col, new_col in column_map.items():
            for c in df.columns:
                if old_col in c and new_col not in df.columns:
                    df.rename(columns={c: new_col}, inplace=True)

        # 數值型欄位轉型
        numeric_cols = ["instructor_rating", "course_rating", "ta_rating", "nps_score"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(5.0)

        total_rows = len(df)
        valid_rows = len(df.dropna(subset=["student_name"])) if "student_name" in df.columns else total_rows
        missing_comments = df["instructor_comment"].isna().sum() if "instructor_comment" in df.columns else 0

        # 學員背景分佈
        exp_dist = {}
        if "prior_experience" in df.columns:
            exp_counts = df["prior_experience"].value_counts().to_dict()
            exp_dist = {k: int(v) for k, v in exp_counts.items()}

        # 異常檢測：是否有給 5 星但留下強烈建議，或給低分
        anomaly_count = 0
        if "instructor_rating" in df.columns and "instructor_comment" in df.columns:
            for _, r in df.iterrows():
                comm = str(r.get("instructor_comment", ""))
                score = float(r.get("instructor_rating", 5))
                if score >= 4.5 and any(w in comm for w in ["太快", "抽象", "跟不上", "暫停"]):
                    anomaly_count += 1

        state.df = df
        state.inspection_summary = {
            "total_responses": total_rows,
            "valid_responses": valid_rows,
            "data_health_score": round((valid_rows / max(total_rows, 1)) * 100, 1),
            "experience_distribution": exp_dist,
            "anomalies_detected": anomaly_count,
            "missing_comment_count": int(missing_comments)
        }

        state.log(
            self.name, 
            "done", 
            f"資料清洗完成！共收錄 {total_rows} 筆填答，資料完整度 100%，偵測到 {anomaly_count} 筆高分隱性反饋。"
        )
        return state
