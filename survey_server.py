import os
import json
import csv
import mimetypes
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import pandas as pd

import config
from core.state import SurveyAnalysisState
from core.orchestrator import SurveyOrchestrator
from utils.exporter import export_html

# 全域共用分析狀態實例
current_state = SurveyAnalysisState(
    course_name=config.COURSE_NAME,
    organizer=config.ORGANIZER
)
orchestrator = SurveyOrchestrator()

if config.RESPONSES_CSV_PATH.exists():
    try:
        current_state.df = pd.read_csv(config.RESPONSES_CSV_PATH)
        current_state = orchestrator.run_pipeline(current_state)
    except Exception as e:
        print(f"[Init Warning] 初次載入資料異常: {e}", flush=True)

class SurveyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query_params = parse_qs(parsed.query)

        # 1. 根目錄：學員手機端問卷
        if path in ("/", "/index.html"):
            index_path = config.STATIC_DIR / "index.html"
            self.serve_file(index_path, "text/html; charset=utf-8")
            return

        # 2. 管理後台：視覺化多代理人儀表板 (/admin 或 /dashboard)
        if path in ("/admin", "/dashboard", "/dashboard.html"):
            dashboard_path = config.STATIC_DIR / "dashboard.html"
            self.serve_file(dashboard_path, "text/html; charset=utf-8")
            return

        # 3. 班級設定 API (/api/class-info?class_id=...)
        if path == "/api/class-info":
            cid = query_params.get("class_id", ["dawei_studio_01"])[0]
            class_info = config.get_class_info(cid)
            self.send_json(200, class_info)
            return

        # 4. 靜態檔案 (/static/...)
        if path.startswith("/static/"):
            rel_path = path[len("/static/"):]
            file_path = config.STATIC_DIR / rel_path
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if not mime_type:
                if file_path.suffix == ".css":
                    mime_type = "text/css"
                elif file_path.suffix == ".js":
                    mime_type = "application/javascript"
                else:
                    mime_type = "application/octet-stream"
            self.serve_file(file_path, mime_type)
            return

        # 5. 報告預覽與列印 (/report/html)
        if path == "/report/html":
            global current_state
            if not current_state.final_report_md:
                current_state = orchestrator.run_pipeline(current_state)
            html_content = export_html(
                current_state.final_report_md, 
                title=f"{config.COURSE_NAME} 結業問卷綜合審查報告"
            )
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html_content.encode("utf-8"))))
            self.end_headers()
            self.wfile.write(html_content.encode("utf-8"))
            return

        # 6. 報告 Markdown 下載 (/report/markdown)
        if path == "/report/markdown":
            if not current_state.final_report_md:
                current_state = orchestrator.run_pipeline(current_state)
            md_bytes = current_state.final_report_md.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/markdown; charset=utf-8")
            self.send_header("Content-Disposition", 'attachment; filename="survey_audit_report.md"')
            self.send_header("Content-Length", str(len(md_bytes)))
            self.end_headers()
            self.wfile.write(md_bytes)
            return

        # 7. API: 統計資訊 (/api/stats)
        if path == "/api/stats":
            stats = self.get_survey_stats()
            self.send_json(200, stats)
            return

        # 8. API: 所有回應資料 (/api/responses)
        if path == "/api/responses":
            responses = self.get_all_responses()
            self.send_json(200, {"count": len(responses), "data": responses})
            return

        self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        global current_state

        # 學員提交問卷
        if parsed.path == "/api/submit":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                data = json.loads(body)
            except Exception as e:
                self.send_json(400, {"status": "error", "message": f"無效的 JSON 格式: {str(e)}"})
                return

            data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.append_to_csv(data)

            try:
                current_state.df = pd.read_csv(config.RESPONSES_CSV_PATH)
            except:
                pass

            self.send_json(200, {
                "status": "success",
                "message": "感謝您的回饋！單元課兌換申請已受理。",
                "selected_reward_course": data.get("selected_reward_course", "")
            })
            return

        # 更新班級與問卷文案設定 (/api/update-class)
        if parsed.path == "/api/update-class":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                payload = json.loads(body)
                cid = payload.get("class_id", "dawei_studio_01")
                cfg = config.load_classes_config()
                if "classes" not in cfg:
                    cfg["classes"] = {}
                cfg["classes"][cid] = payload
                cfg["active_class_id"] = cid

                with open(config.CLASSES_JSON_PATH, "w", encoding="utf-8") as f:
                    json.dump(cfg, f, ensure_ascii=False, indent=2)

                self.send_json(200, {"status": "success", "message": "班級與問卷文案已成功儲存更新！"})
            except Exception as e:
                self.send_json(400, {"status": "error", "message": str(e)})
            return

        # 觸發多代理協同分析 (/api/analyze)
        if parsed.path == "/api/analyze":
            if config.RESPONSES_CSV_PATH.exists():
                current_state.df = pd.read_csv(config.RESPONSES_CSV_PATH)
            current_state = orchestrator.run_pipeline(current_state)
            self.send_json(200, {
                "status": "success",
                "message": "多代理協同分析完成",
                "executive_summary": current_state.executive_summary,
                "nps": current_state.quant_metrics.get("nps", 0),
                "avg_instructor": current_state.quant_metrics.get("avg_instructor", 5.0)
            })
            return

        # AI 顧問問答 (/api/ask)
        if parsed.path == "/api/ask":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                payload = json.loads(body)
                question = payload.get("question", "")
            except Exception as e:
                self.send_json(400, {"status": "error", "message": str(e)})
                return

            answer = orchestrator.ask_advisor(question, current_state)
            self.send_json(200, {"status": "success", "answer": answer})
            return

        self.send_error(404, "Endpoint Not Found")

    def serve_file(self, file_path: Path, content_type: str):
        if not file_path.exists():
            self.send_error(404, f"File {file_path.name} not found")
            return
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error reading file: {e}")

    def send_json(self, status_code: int, data: dict):
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def append_to_csv(self, row_dict: dict):
        file_path = config.RESPONSES_CSV_PATH
        fieldnames = [
            "timestamp", "class_id", "student_name", "phone", "line_id", "email",
            "prior_experience", "key_progress", "struggle_point", "instructor_rating", 
            "instructor_comment", "course_rating", "ta_rating", "ta_comment", 
            "platform_experience", "nps_score", "selected_reward_course"
        ]
        file_exists = file_path.exists()
        
        with open(file_path, mode="a", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            if not file_exists or file_path.stat().st_size == 0:
                writer.writeheader()
            writer.writerow(row_dict)

    def get_all_responses(self):
        file_path = config.RESPONSES_CSV_PATH
        if not file_path.exists():
            return []
        rows = []
        with open(file_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)
        return rows

    def get_survey_stats(self):
        responses = self.get_all_responses()
        count = len(responses)
        if count == 0:
            return {"total_count": 0, "nps": 0, "avg_instructor": 0, "avg_course": 0, "avg_ta": 0}

        inst_scores = []
        course_scores = []
        ta_scores = []
        nps_scores = []

        for r in responses:
            try:
                inst_scores.append(float(r.get("instructor_rating", 5)))
                course_scores.append(float(r.get("course_rating", 5)))
                ta_scores.append(float(r.get("ta_rating", 5)))
                nps_scores.append(float(r.get("nps_score", 10)))
            except:
                pass

        promoters = sum(1 for s in nps_scores if s >= 9)
        detractors = sum(1 for s in nps_scores if s <= 6)
        nps = round(((promoters - detractors) / len(nps_scores) * 100), 1) if nps_scores else 0

        return {
            "total_count": count,
            "nps": nps,
            "avg_instructor": round(sum(inst_scores) / len(inst_scores), 2) if inst_scores else 0,
            "avg_course": round(sum(course_scores) / len(course_scores), 2) if course_scores else 0,
            "avg_ta": round(sum(ta_scores) / len(ta_scores), 2) if ta_scores else 0,
            "last_submission": responses[-1].get("timestamp", "") if responses else ""
        }

def run_server(port=config.SURVEY_SERVER_PORT):
    server_address = ("", port)
    httpd = HTTPServer(server_address, SurveyHandler)
    print(f"============================================================", flush=True)
    print(f"🎨 結業問卷多代理 AI 分析師 ✕ 單元課兌換系統伺服器已啟動！", flush=True)
    print(f"📱 學員填答端點 (LINE 分享連結): http://localhost:{port}/", flush=True)
    print(f"📊 管理後台與兌換名冊:           http://localhost:{port}/admin", flush=True)
    print(f"📑 結業診斷報告 (可列印 HTML):    http://localhost:{port}/report/html", flush=True)
    print(f"============================================================", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n伺服器已停止。", flush=True)
        httpd.server_close()

if __name__ == "__main__":
    run_server()
