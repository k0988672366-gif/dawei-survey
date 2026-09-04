import numpy as np
import pandas as pd
from typing import Dict, Any
from core.state import SurveyAnalysisState

class QuantAgent:
    """Agent 2: 量化統計與 NPS 分析代理人 (Quant & NPS Analyst)"""
    def __init__(self, llm_client=None):
        self.name = "量化統計代理 (Quant Agent)"
        self.llm_client = llm_client

    def run(self, state: SurveyAnalysisState) -> SurveyAnalysisState:
        state.log(self.name, "start", "計算教學維度均分、離散度與淨推薦值 (NPS)...")

        df = state.df
        if df is None or len(df) == 0:
            state.quant_metrics = {
                "avg_instructor": 0.0,
                "std_instructor": 0.0,
                "avg_course": 0.0,
                "std_course": 0.0,
                "avg_ta": 0.0,
                "std_ta": 0.0,
                "nps": 0.0,
                "promoters_count": 0,
                "promoters_pct": 0.0,
                "passives_count": 0,
                "passives_pct": 0.0,
                "detractors_count": 0,
                "detractors_pct": 0.0,
                "platform_distribution": {}
            }
            state.log(self.name, "done", "目前尚無問卷量化數據。")
            return state

        total = len(df)

        # 維度均分與標準差
        def get_stat(col):
            if col in df.columns:
                series = pd.to_numeric(df[col], errors="coerce").dropna()
                if len(series) > 0:
                    return round(float(series.mean()), 2), round(float(series.std()), 2)
            return 5.0, 0.0

        inst_mean, inst_std = get_stat("instructor_rating")
        course_mean, course_std = get_stat("course_rating")
        ta_mean, ta_std = get_stat("ta_rating")

        # NPS 計算 (0~10分)
        nps_scores = pd.to_numeric(df.get("nps_score", 10), errors="coerce").dropna()
        promoters = int((nps_scores >= 9).sum())
        passives = int(((nps_scores >= 7) & (nps_scores < 9)).sum())
        detractors = int((nps_scores < 7).sum())

        promoter_pct = round((promoters / total) * 100, 1)
        passive_pct = round((passives / total) * 100, 1)
        detractor_pct = round((detractors / total) * 100, 1)
        nps = round(promoter_pct - detractor_pct, 1)

        # 平台觀看順暢度分佈
        platform_dist = {}
        if "platform_experience" in df.columns:
            p_counts = df["platform_experience"].value_counts().to_dict()
            for k, v in p_counts.items():
                platform_dist[k] = round((v / total) * 100, 1)

        # 彙整指標
        state.quant_metrics = {
            "avg_instructor": inst_mean,
            "std_instructor": inst_std,
            "avg_course": course_mean,
            "std_course": course_std,
            "avg_ta": ta_mean,
            "std_ta": ta_std,
            "nps": nps,
            "promoters_count": promoters,
            "promoters_pct": promoter_pct,
            "passives_count": passives,
            "passives_pct": passive_pct,
            "detractors_count": detractors,
            "detractors_pct": detractor_pct,
            "platform_distribution": platform_dist
        }

        teacher_label = state.teacher_name or "講師"
        state.log(
            self.name, 
            "done", 
            f"量化指標計算完成：{teacher_label}滿意度 {inst_mean}★，助教滿意度 {ta_mean}★，NPS 達 {'+' if nps >= 0 else ''}{nps}！"
        )
        return state
