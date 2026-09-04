import io
import re
import json
from typing import Dict, Any, List, Optional
import pypdf

from core.llm_client import LLMClient
import config

class SyllabusSurveyAgent:
    """Agent 8: 課綱分析與客製化問卷規劃師 (Syllabus-to-Survey Instructional Agent)
    
    職責：
    1. 解析講師上傳的課綱 PDF 檔案，提取文字內容
    2. 研讀課程結構、單元主題、教學目標與實作技能
    3. 自動生成高度契合該門課的問卷題目（單元痛點、吸收度、教學亮點、延伸單元課獎勵）
    4. 支援 Gemini 2.5 Flash 深度教育推論與智慧本機啟發式降級引擎
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.name = "課綱問卷規劃師 (Syllabus Survey Agent)"
        self.llm = llm_client or LLMClient()

    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """從 PDF 二進位資料中提取全部文字"""
        try:
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            text_parts = []
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    text_parts.append(f"--- [第 {i+1} 頁] ---\n" + page_text.strip())
            full_text = "\n\n".join(text_parts)
            return full_text.strip()
        except Exception as e:
            print(f"[SyllabusAgent Error] PDF 解析失敗: {e}", flush=True)
            return ""

    def generate_survey_config(self, syllabus_text: str, hints: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """依據課綱文字與輔助提示，自動規劃完整問卷設定"""
        hints = hints or {}
        custom_course = hints.get("course_name", "").strip()
        custom_teacher = hints.get("teacher_name", "").strip()
        custom_org = hints.get("organizer", "").strip()

        if self.llm.is_live_llm():
            try:
                result = self._generate_with_gemini(syllabus_text, custom_course, custom_teacher, custom_org)
                if result and isinstance(result, dict) and "course_name" in result:
                    return result
            except Exception as e:
                print(f"[SyllabusAgent Warning] Gemini 生成失敗，切換至本機智慧引擎: {e}", flush=True)

        return self._heuristic_generate(syllabus_text, custom_course, custom_teacher, custom_org)

    def _generate_with_gemini(self, text: str, c_name: str, t_name: str, org: str) -> Dict[str, Any]:
        """使用 Gemini API 進行深度教學法課綱問卷設計"""
        truncated_text = text[:8000] # 避免過長
        prompt = f"""
你是一位擁有 15 年經驗的資深教學設計總監（Instructional Designer）與課程評鑑專家。
請仔細研讀以下由講師提供的【課程大綱內容（由 PDF/文件提取）】：

==== 課綱內容開始 ====
{truncated_text}
==== 課綱內容結束 ====

已知自訂提示（若有提供請優先採用，若無則由課綱研讀）：
- 課程名稱提示: {c_name or '請從課綱研判'}
- 講師姓名提示: {t_name or '請從課綱研判'}
- 主辦單位提示: {org or '赫綵設計學院'}

【你的任務】
請為本門課程量身規劃一套「高完填率、深度對齊課綱單元、且能精準抓出學員學習痛點」的手機端結業問卷配置，以及 3~4 門極具吸引力的「完課免費兌換單元課」獎勵選項。

請嚴格輸出合法的 JSON 物件，格式如下（請勿包含 Markdown 標記以外的額外解釋）：
```json
{{
  "class_id": "auto_class_id",
  "course_name": "課程完整正式名稱",
  "course_subtitle": "吸睛、有溫度且切合本課程主題的副標題",
  "badge_text": "🎁 結業回饋 ✕ 限時專屬好禮",
  "teacher_name": "授課講師姓名",
  "organizer": "主辦機構名稱",
  "platform_name": "OKBOM直播平台",
  "gift_banner_title": "完課專屬好禮：任選一門線上單元課！",
  "gift_banner_desc": "感謝您的認真參與，填寫完畢即可於文末免費勾選一門量身打造的進階單元課，將由專員聯繫為您開通！",
  "pill_1": "⏱ 只需 90 秒",
  "pill_2": "📱 手機極速點選",
  "pill_3": "🎁 完填即贈單元課",
  "syllabus_topics": [
    "單元 1：核心單元名稱與實作重點",
    "單元 2：核心單元名稱與實作重點",
    "單元 3：核心單元名稱與實作重點",
    "單元 4：核心單元名稱與實作重點"
  ],
  "struggle_options": [
    "對應單元1的常見痛點或節奏問題",
    "對應單元2的觀念理解或軟體操作問題",
    "對應單元3的進階實務應用問題",
    "進度與難度剛剛好，整體非常順暢！"
  ],
  "reward_courses": [
    "單元課 A：【核心延伸】高吸引力單元課名稱 (市價 $1,200)",
    "單元課 B：【進階突破】高吸引力單元課名稱 (市價 $1,500)",
    "單元課 C：【風格實戰】高吸引力單元課名稱 (市價 $1,200)",
    "單元課 D：【獨立創作】高吸引力單元課名稱 (市價 $1,600)"
  ]
}}
```
"""
        raw = self.llm.generate_text(prompt)
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            return data
        return {}

    def _heuristic_generate(self, text: str, c_name: str, t_name: str, org: str) -> Dict[str, Any]:
        """本機規則型教學語義提取引擎（離線或無 API Key 時 100% 穩定可用）"""
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        
        # 1. 識別課程名稱
        detected_course = c_name
        if not detected_course:
            for line in lines[:10]:
                if any(k in line for k in ["課程", "課綱", "畫室", "直播", "班", "實戰", "工作坊", "教學"]):
                    clean = re.sub(r'^(課綱|課程名稱|主題|科目)[:：\s]*', '', line).strip()
                    if 4 <= len(clean) <= 40:
                        detected_course = clean
                        break
        if not detected_course:
            detected_course = lines[0] if lines else "專業精實直播培訓班"

        # 2. 識別講師姓名
        detected_teacher = t_name
        if not detected_teacher:
            for line in lines[:20]:
                m = re.search(r'(?:講師|老師|授課|Instructor)[:：\s]*([^\s,，、]+)', line)
                if m:
                    detected_teacher = m.group(1).replace("老師", "").strip()
                    break
        if not detected_teacher:
            detected_teacher = "授課老師"

        # 3. 識別單元/章節清單
        topics = []
        unit_pattern = re.compile(
            r'^(?:第[一二三四五六七八九十0-9]+[週周單單元講章節課]|Week\s*\d+|Unit\s*\d+|Day\s*\d+|[0-9]{1,2}[\.、])\s*(.*)',
            re.IGNORECASE
        )
        for line in lines:
            line_str = line.strip()
            # 排除純標題（如「課程單元規劃：」、「課綱大綱：」）
            if line_str.endswith(("：", ":", "如下", "如下：")):
                continue
            m = unit_pattern.match(line_str)
            if m:
                if len(line_str) <= 50 and line_str not in topics:
                    topics.append(line_str)
            elif any(k in line_str for k in ["單元", "模組", "實戰階段", "核心重點"]) and len(line_str) <= 40:
                if line_str not in topics and not any(h in line_str for h in ["規劃", "大綱", "總覽", "內容"]):
                    topics.append(line_str)

        if len(topics) < 3:
            topics = [
                f"單元 1：{detected_course} 核心基礎架構與工具掌握",
                f"單元 2：實戰技巧拆解與關鍵方法示範",
                f"單元 3：進階商業應用與整合練習",
                f"單元 4：獨立作品完稿與成果優化"
            ]
        else:
            topics = topics[:6]

        text_lower = text.lower()
        is_art = any(k in text_lower for k in ["procreate", "繪畫", "插畫", "筆刷", "光影", "色彩", "電繪", "透視", "線稿", "畫室", "大維"])
        is_code = any(k in text_lower for k in ["python", "程式", "ai", "pandas", "演算法", "code", "數據", "爬蟲", "prompt"])
        is_design = any(k in text_lower for k in ["ui", "ux", "figma", "平面設計", "視覺", "品牌", "排版", "ps", "ai"])

        if is_art:
            struggle_options = [
                "光影分階與明暗對比掌握較生疏",
                "正片疊底與色彩氛圍疊加需更多練習",
                "線稿構圖比例與人體透視容易跑形",
                "課堂示範節奏偏快，來不及邊聽邊畫",
                "進度與難度剛剛好，吸收非常充實順暢！"
            ]
            reward_courses = [
                "單元課 A：【筆刷神技】大師級手勢快捷鍵與自訂紋理筆刷庫 (市價 $1,200)",
                "單元課 B：【氛圍魔法】商業插畫日夜光影與氛圍感全解析 (市價 $1,500)",
                "單元課 C：【調色秘笈】色彩心理學與高級感配色盤速成 (市價 $1,200)",
                "單元課 D：【動態骨架】角色五官精準比例與動態速繪指南 (市價 $1,600)"
            ]
            subtitle = "結業成果驗收 ＆ 免費加碼單元課兌換"
        elif is_code:
            struggle_options = [
                "資料型別與邏輯迴圈觀念較抽象",
                "資料清洗與缺失值處理實務較吃力",
                "自訂函式與第三方套件串接報錯排查",
                "課堂程式碼敲打速度快，需多暫停吸收",
                "進度與難度掌握適中，實戰成果滿滿！"
            ]
            reward_courses = [
                "單元課 A：【辦公自動化】Python 與 Excel 報表排程全自動處理 (市價 $1,200)",
                "單元課 B：【網路爬蟲】動態網頁資料採集與輿情監控快打術 (市價 $1,500)",
                "單元課 C：【AI 賦能】Prompt 工程與大語言模型 API 串接實戰 (市價 $1,500)"
            ]
            subtitle = "結業技術盤點 ＆ 實戰單元課免費兌換"
        elif is_design:
            struggle_options = [
                "格線系統與響應式排版規則較難適應",
                "組件化 Design System 規範與變體建立",
                "使用者研究訪談與洞察發想不易收斂",
                "設計軟體快捷鍵與高保真原型動效交互",
                "進度與難度剛剛好，整體收穫極大！"
            ]
            reward_courses = [
                "單元課 A：【高階原型】Figma 變體元件庫與微交互動效實務 (市價 $1,200)",
                "單元課 B：【視覺提案】商業設計提案簡報與作品集包裝 (市價 $1,500)",
                "單元課 C：【排版心法】網頁與 App 資訊層級黃金架構 (市價 $1,200)"
            ]
            subtitle = "結業能力評估 ＆ 精選單元課免費兌換"
        else:
            struggle_options = [
                "核心方法論與理論框架較為龐大",
                "實作案例練習時間稍嫌不足",
                "課堂步驟示範速度希望能更從容",
                "課後缺乏客製化即時反饋",
                "節奏明快扎實，完全跟得上且收穫豐碩！"
            ]
            reward_courses = [
                "單元課 A：【高效思維】核心方法論實戰精華拆解 (市價 $1,200)",
                "單元課 B：【工具加速】必備生產力工具與模板大禮包 (市價 $1,500)",
                "單元課 C：【職涯晉升】實戰專案演練與關鍵能力突破 (市價 $1,200)"
            ]
            subtitle = "結業學習評量 ＆ 精選加值單元課免費兌換"

        import time
        auto_id = f"class_{int(time.time())}"

        return {
            "class_id": auto_id,
            "course_name": detected_course,
            "course_subtitle": subtitle,
            "badge_text": "🎁 結業回饋 ✕ 限時專屬好禮",
            "gift_banner_title": "完課專屬好禮：任選一門線上單元課！",
            "gift_banner_desc": "感謝您的認真參與，填寫完畢即可於文末免費勾選一門量身打造的線上單元課，將由客服聯繫為您開通！",
            "teacher_name": detected_teacher,
            "organizer": org or "赫綵設計學院",
            "platform_name": "OKBOM直播平台",
            "pill_1": "⏱ 只需 90 秒",
            "pill_2": "📱 手機極速點選",
            "pill_3": "🎁 完填即贈單元課",
            "syllabus_topics": topics,
            "struggle_options": struggle_options,
            "reward_courses": reward_courses
        }
