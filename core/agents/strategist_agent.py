from typing import Dict, Any, List
from core.state import SurveyAnalysisState

class PedagogicalStrategistAgent:
    """Agent 5: 教學改進與行動策略代理人 (Pedagogical Action Strategist)"""
    def __init__(self, llm_client=None):
        self.name = "教學策略代理 (Strategist Agent)"
        self.llm_client = llm_client

    def run(self, state: SurveyAnalysisState) -> SurveyAnalysisState:
        teacher_label = state.teacher_name or "講師"
        state.log(self.name, "start", f"根據【{state.course_name}】量化、質化與根因診斷，制定教學迭代行動矩陣...")

        df = state.df
        all_struggles = df["struggle_point"].dropna().tolist() if (df is not None and "struggle_point" in df.columns) else []
        all_platforms = df["platform_experience"].dropna().tolist() if (df is not None and "platform_experience" in df.columns) else []

        quick_wins = []
        next_cohort = []
        curriculum_arch = []

        # 1. 偵測節奏
        has_pacing_issue = any(w in str(s) for s in all_struggles for w in ["快", "偏快", "跟不上", "暫停"])
        if has_pacing_issue:
            quick_wins.append({
                "title": f"示範關鍵環節增加『操作口訣』與 5~10 秒停留",
                "impact": "高",
                "effort": "極低",
                "detail": f"{teacher_label} 在切換關鍵工具、設定參數或核心邏輯時，口述明確步驟並在畫面上停留數秒，大幅降低新手緊張感。"
            })

        # 2. 偵測平台
        has_platform_issue = any(w in str(p) for p in all_platforms for w in ["卡頓", "延遲", "影響"])
        if has_platform_issue:
            quick_wins.append({
                "title": "直播串流頻寬優化與 24 小時內即時回放釋出",
                "impact": "高",
                "effort": "低",
                "detail": "檢查直播平台推流碼率與備援伺服器，並於課後 24 小時內上傳完整高清回放供學員隨時複習。"
            })

        # 3. 偵測自訂或其他卡關
        custom_items = [str(s) for s in all_struggles if "其他" in str(s) or "：" in str(s)]
        if custom_items:
            clean_item = custom_items[0].replace("其他：", "").replace("其他:", "").strip()
            quick_wins.append({
                "title": f"針對學員個別回饋實施定向補充（如『{clean_item}』）",
                "impact": "中",
                "effort": "極低",
                "detail": f"學員反映『{clean_item}』，建議於課後社群或班級公告中給予專屬指引與疑難排解。"
            })

        # 4. 預設速贏（若上述均無）
        if not quick_wins:
            quick_wins.append({
                "title": f"課前提供【{state.course_name}】單元精華練習包",
                "impact": "高",
                "effort": "低",
                "detail": f"課前 24 小時在班群發布預習指引與範例檔，讓初學者課堂上直接聚焦於 {teacher_label} 的關鍵示範。"
            })

        # 次期優化
        next_cohort.append({
            "title": f"錄製 10 分鐘【{state.course_name}】新手導航微影片",
            "impact": "極高",
            "effort": "中",
            "detail": "開課前作為預習資源，專講核心軟體介面概念與高頻操作，將新手摸索門檻前置消化。"
        })
        next_cohort.append({
            "title": "課堂畫面增設『關鍵參數與步驟提示標籤』",
            "impact": "中",
            "effort": "低",
            "detail": f"在直播畫面或聊天室固定標示 {teacher_label} 當前使用之核心工具與參數，提升學員跟課即時感。"
        })

        # 長期架構
        curriculum_arch.append({
            "title": f"無縫銜接規劃【{state.course_name}】進階商業實戰班",
            "impact": "極高 (商業轉化)",
            "effort": "高",
            "detail": f"趁學員結業學習熱度與高滿意度口碑，提供舊生專屬折價優惠，延伸進階案例實戰與獨立作品集完稿！"
        })

        action_matrix = {
            "quick_wins": quick_wins[:3],
            "next_cohort": next_cohort[:2],
            "curriculum_architecture": curriculum_arch[:2]
        }

        # 講師個人教學覆盤指引 (Teacher Reflection)
        teacher_reflection = [
            f"Q1（節奏調控）：在示範難度較高的操作步驟時，我是否給了學員足夠的『消化秒數』？",
            f"Q2（盲點同理）：對於我已經成為肌肉記憶的專業習慣，初學者是否需要更明確的口訣或視覺輔助？",
            f"Q3（風格傳承）：學員高度肯定課堂收穫，如何引導他們從『課堂跟隨示範』逐步過渡到『獨立自主實踐』？"
        ]

        # 助教作業改進清單 (TA Checklist)
        ta_checklist = [
            f"✅ 課堂直播即時同步：在聊天室隨時文字筆記『{teacher_label} 目前操作關鍵步驟與設定數值』。",
            f"✅ 作業批改標準化：作業統一於 36 小時內回覆，維持學員極高信任感與學習成就感。",
            f"✅ 新手關懷標籤：針對自述『零基礎』的學員，給予更多正向肯定與具體修改步驟。"
        ]

        state.pedagogical_strategies = {
            "action_matrix": action_matrix,
            "teacher_reflection": teacher_reflection,
            "ta_checklist": ta_checklist
        }

        state.log(
            self.name, 
            "done", 
            f"教學策略矩陣擬定完成！包含 {len(quick_wins)} 項即刻速贏行動、次期優化、講師覆盤 3 問與助教 SOP 清單。"
        )
        return state
