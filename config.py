import os
import json
from pathlib import Path

# 基礎路徑
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
DATA_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)

CLASSES_JSON_PATH = DATA_DIR / "classes.json"

def load_classes_config():
    if CLASSES_JSON_PATH.exists():
        try:
            with open(CLASSES_JSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "active_class_id": "dawei_studio_01",
        "classes": {
            "dawei_studio_01": {
                "class_id": "dawei_studio_01",
                "course_name": "劉大維畫室直播課程",
                "teacher_name": "劉大維",
                "organizer": "赫綵設計學院",
                "platform_name": "OKBOM直播平台",
                "syllabus_topics": [
                    "單元 1：Procreate 核心介面與筆刷調配邏輯",
                    "單元 2：線稿構圖技巧與空間比例拆解",
                    "單元 3：光影明暗分階與正片疊底色彩邏輯",
                    "單元 4：質感紋理融合與風格化完稿實戰"
                ],
                "reward_courses": [
                    "單元課 A：【筆刷神技】Procreate 10大必學手勢與效率自訂筆刷 (市價 $1,200)",
                    "單元課 B：【光影魔法】商業插畫光影氛圍感進階實戰 (市價 $1,500)",
                    "單元課 C：【調色秘笈】色彩心理學與私房調色盤全解析 (市價 $1,200)",
                    "單元課 D：【動態人體】角色五官比例與肢體骨架速繪 (市價 $1,600)"
                ]
            }
        }
    }

def get_class_info(class_id: str = None) -> dict:
    cfg = load_classes_config()
    classes = cfg.get("classes", {})
    target_id = class_id or cfg.get("active_class_id", "dawei_studio_01")
    if target_id in classes:
        return classes[target_id]
    elif classes:
        return list(classes.values())[0]
    return {
        "class_id": "default",
        "course_name": "專業直播培訓課程",
        "teacher_name": "授課講師",
        "organizer": "赫綵設計學院",
        "platform_name": "OKBOM直播平台",
        "syllabus_topics": [],
        "reward_courses": []
    }

_default_info = get_class_info()
COURSE_NAME = _default_info.get("course_name", "劉大維畫室直播課程")
TEACHER_NAME = _default_info.get("teacher_name", "劉大維")
ORGANIZER = _default_info.get("organizer", "赫綵設計學院")
PLATFORM_NAME = _default_info.get("platform_name", "OKBOM直播平台")

# 資料儲存路徑
RESPONSES_CSV_PATH = DATA_DIR / "survey_responses.csv"
SAMPLE_CSV_PATH = DATA_DIR / "sample_survey_responses.csv"

# 伺服器連接埠設定
SURVEY_SERVER_PORT = int(os.getenv("PORT", os.getenv("SURVEY_SERVER_PORT", 8080)))
STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", 8501))

# 後台安全密碼 (保護學員電話、LINE ID 不外洩)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "art888")  # 可隨時自訂修改

# Gemini AI 配置
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
