from typing import Dict, Any, Optional
import pandas as pd

def get_charts_data(quant_metrics: Dict[str, Any], inspection_summary: Dict[str, Any], df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """產出前端圖表所需的結構化數據 (適用於 Chart.js / Plotly / SVG)"""
    # 1. 五維雷達圖數據
    radar_labels = ["大維老師授課", "課綱與素材", "助教支援", "平台體驗", "NPS推薦折算"]
    inst_score = quant_metrics.get("avg_instructor", 5.0)
    course_score = quant_metrics.get("avg_course", 5.0)
    ta_score = quant_metrics.get("avg_ta", 5.0)
    # 平台滿意度折算 (0-5)
    platform_dist = quant_metrics.get("platform_distribution", {})
    smooth_pct = platform_dist.get("非常順暢清晰", 80.0)
    platform_score = round((smooth_pct / 100.0) * 5.0, 2)
    # NPS 折算 0-5 分
    nps_val = quant_metrics.get("nps", 80.0)
    nps_score = round(max(0.0, min(5.0, ((nps_val + 100) / 200) * 5.0)), 2)

    radar_values = [inst_score, course_score, ta_score, platform_score, nps_score]

    # 2. NPS 佔比圓餅圖
    nps_labels = ["推薦者 (9-10分)", "被動者 (7-8分)", "批評者 (0-6分)"]
    nps_values = [
        quant_metrics.get("promoters_pct", 85.0),
        quant_metrics.get("passives_pct", 15.0),
        quant_metrics.get("detractors_pct", 0.0)
    ]

    # 3. 學員起點分佈
    exp_dist = inspection_summary.get("experience_distribution", {})
    exp_labels = list(exp_dist.keys()) if exp_dist else ["零基礎小白", "偶爾塗鴉新手", "有一定繪畫經驗"]
    exp_values = list(exp_dist.values()) if exp_dist else [16, 20, 9]

    # 4. 卡關點柱狀圖
    struggle_counts = {}
    if df is not None and "struggle_point" in df.columns:
        sc = df["struggle_point"].value_counts().head(5).to_dict()
        struggle_counts = {k: int(v) for k, v in sc.items()}
    else:
        struggle_counts = {
            "進度剛剛好無卡關": 22,
            "光影觀念較為抽象": 11,
            "示範節奏偏快": 8,
            "筆刷圖層操作不直覺": 4
        }

    return {
        "radar": {
            "labels": radar_labels,
            "values": radar_values
        },
        "nps": {
            "score": quant_metrics.get("nps", 88.9),
            "labels": nps_labels,
            "values": nps_values
        },
        "experience": {
            "labels": exp_labels,
            "values": exp_values
        },
        "struggles": {
            "labels": list(struggle_counts.keys()),
            "values": list(struggle_counts.values())
        }
    }

def try_create_plotly_radar(quant_metrics: Dict[str, Any]):
    """若環境已安裝 Plotly，建立互動式雷達圖"""
    try:
        import plotly.graph_objects as go
        data = get_charts_data(quant_metrics, {})
        fig = go.Figure(data=go.Scatterpolar(
            r=data["radar"]["values"],
            theta=data["radar"]["labels"],
            fill='toself',
            fillcolor='rgba(99, 102, 241, 0.35)',
            line=dict(color='#818cf8', width=2)
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 5])
            ),
            showlegend=False,
            template="plotly_dark",
            margin=dict(l=40, r=40, t=20, b=20)
        )
        return fig
    except ImportError:
        return None
