import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
SAMPLE_CSV = DATA_DIR / "sample_survey_responses.csv"
RESPONSES_CSV = DATA_DIR / "survey_responses.csv"

# 擬真姓名庫
NAMES = [
    "小艾", "廷廷", "阿文", "Vivian", "宣妤", "Chen", "佩蓉", "Kevin", 
    "佳霖", "大雄", "思涵", "Leo", "雅婷", "詠晴", "Ray", "宇廷", 
    "千惠", "Maggie", "博宇", "品蓉", "冠宇", "宜靜", "家豪", "Emily", 
    "威廷", "雅涵", "建宏", "Joyce", "宗翰", "欣穎", "冠廷", "Alice", 
    "承恩", "芷萱", "柏翰", "Peggy", "俊賢", "依婷", "彥廷", "Chloe", 
    "政宏", "若涵", "宏偉", "Jessica", "志豪"
]

EXPERIENCES = [
    ("零基礎小白", 0.35),
    ("偶爾塗鴉新手", 0.45),
    ("有一定繪畫經驗", 0.20)
]

PROGRESS_OPTIONS = [
    "線稿構圖更有信心",
    "掌握光影與立體感",
    "熟練圖層與筆刷混合",
    "順利畫出完整作品",
    "重燃持續畫畫熱情"
]

STRUGGLES = [
    "光影觀念與色調搭配較抽象，需要更多拆解",
    "課堂示範節奏偏快，來不及邊聽邊畫",
    "筆刷特性與圖層模式運用不夠直覺",
    "進度與難度剛剛好，學習非常順暢！"
]

INSTRUCTOR_COMMENTS_HIGH = [
    "大維老師講解太清晰了！原本完全不懂圖層正片疊底，這堂課終於打通任督二脈！",
    "超愛老師示範筆刷調色的過程，看老師畫畫真的像魔法一樣療癒！",
    "老師在直播中很有耐心，問了笨問題老師還特地切換畫面重新示範，超感動～",
    "老師的繪畫風格超級迷人！跟著老師一步一步畫，居然我也能畫出像樣的作品！",
    "教學節奏很舒服，觀念講得很透徹，不是只有死板的抄畫，而是教背後的邏輯！",
    "謝謝大維老師，這是我上過最棒的電繪直播課，已經期待下一期了！",
    "大維老師聲音好好聽，上課完全不枯燥，兩個半小時一下就過去了！",
    "原本買了 iPad 都在吃灰，上完老師的課現在每天下班都想抓著筆畫畫！"
]

INSTRUCTOR_COMMENTS_CRITIQUE = [
    "老師教得很好，但第三週講光影過渡時節奏稍微有點快，如果能再多停頓 30 秒等大家會更好！",
    "希望老師未來能多給一點自創構圖的引導，目前還是比較依賴參考底圖。",
    "示範很精彩，但偶爾切換筆刷太快沒看清楚是哪一支，好在有錄影回放可以暫停看。",
    "希望下一期能有更多人體五官比例的細節拆解，這期覺得風景光影很棒！"
]

TA_COMMENTS = [
    "助教超級棒！半夜交作業居然隔天一早就收到批改紅線圖，太用心了！",
    "助教在直播聊天室的補充筆記非常即時，幫大維老師分擔很多提問！",
    "謝謝助教耐心的解答我 Procreate 手勢卡住的問題，回覆很親切又專業！",
    "批改作業時給的建議很具體，不是只有讚美，有指出暗部反光該怎麼修！",
    "助教辛苦了！每次發問都迅速給予正面回饋，讓新手超級安心～"
]

FUTURE_TOPICS = [
    "風景光影與氛圍實戰",
    "人物角色動態與五官肢體",
    "商業插畫與個人接案風格",
    "實體面對面手把手工作坊",
    "色彩學與進階筆刷調配"
]

def generate_responses(count=45):
    rows = []
    base_time = datetime.now() - timedelta(days=3)

    for i in range(count):
        name = NAMES[i % len(NAMES)]
        email = f"{name.lower()}{i+1}@example.com"
        submitted_at = (base_time + timedelta(hours=i*1.5 + random.randint(1, 30))).strftime("%Y-%m-%d %H:%M:%S")

        # 基礎分配
        exp_rand = random.random()
        if exp_rand < 0.35:
            exp = "零基礎小白"
        elif exp_rand < 0.80:
            exp = "偶爾塗鴉新手"
        else:
            exp = "有一定繪畫經驗"

        # 進步點 (選 1~2 項)
        prog_sample = random.sample(PROGRESS_OPTIONS, random.randint(1, 2))
        key_prog = "、".join(prog_sample)

        # 卡關點與評分關聯
        if exp == "零基礎小白":
            struggle = random.choice([
                "課堂示範節奏偏快，來不及邊聽邊畫",
                "光影觀念與色調搭配較抽象，需要更多拆解",
                "筆刷特性與圖層模式運用不夠直覺"
            ])
            inst_score = random.choices([4, 5], weights=[0.25, 0.75])[0]
            course_score = random.choices([3, 4, 5], weights=[0.15, 0.45, 0.40])[0]
            nps = random.choices([8, 9, 10], weights=[0.2, 0.4, 0.4])[0]
        else:
            struggle = random.choice([
                "進度與難度剛剛好，學習非常順暢！",
                "光影觀念與色調搭配較抽象，需要更多拆解",
                "進度與難度剛剛好，學習非常順暢！"
            ])
            inst_score = random.choices([4, 5], weights=[0.1, 0.9])[0]
            course_score = random.choices([4, 5], weights=[0.2, 0.8])[0]
            nps = random.choices([9, 10], weights=[0.3, 0.7])[0]

        ta_score = random.choices([4, 5], weights=[0.1, 0.9])[0]

        # 評語隨機分配
        if random.random() < 0.35 and exp == "零基礎小白":
            inst_comm = random.choice(INSTRUCTOR_COMMENTS_CRITIQUE)
        else:
            inst_comm = random.choice(INSTRUCTOR_COMMENTS_HIGH)

        ta_comm = random.choice(TA_COMMENTS) if random.random() < 0.8 else ""

        # 平台
        platform = random.choices(
            ["非常順暢清晰", "偶有小延遲但不影響", "經常卡頓影響觀看"],
            weights=[0.80, 0.16, 0.04]
        )[0]

        # 未來主題
        future_samp = random.sample(FUTURE_TOPICS, random.randint(1, 3))
        future_str = "、".join(future_samp)

        rows.append({
            "timestamp": submitted_at,
            "student_name": name,
            "email": email,
            "prior_experience": exp,
            "key_progress": key_prog,
            "struggle_point": struggle,
            "instructor_rating": inst_score,
            "instructor_comment": inst_comm,
            "course_rating": course_score,
            "ta_rating": ta_score,
            "ta_comment": ta_comm,
            "platform_experience": platform,
            "nps_score": nps,
            "future_topics": future_str
        })

    return rows

def save_csv(filename, rows):
    fieldnames = [
        "timestamp", "student_name", "email", "prior_experience", 
        "key_progress", "struggle_point", "instructor_rating", 
        "instructor_comment", "course_rating", "ta_rating", 
        "ta_comment", "platform_experience", "nps_score", "future_topics"
    ]
    with open(filename, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} rows to {filename}")

if __name__ == "__main__":
    data = generate_responses(45)
    save_csv(SAMPLE_CSV, data)
    save_csv(RESPONSES_CSV, data)
