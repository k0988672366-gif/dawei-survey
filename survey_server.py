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
from core.agents.syllabus_agent import SyllabusSurveyAgent
from utils.exporter import export_html

# 全域共用分析狀態實例
current_state = SurveyAnalysisState(
    course_name=config.COURSE_NAME,
    organizer=config.ORGANIZER
)
orchestrator = SurveyOrchestrator()
syllabus_agent = SyllabusSurveyAgent()

if config.RESPONSES_CSV_PATH.exists():
    try:
        current_state.df = pd.read_csv(config.RESPONSES_CSV_PATH)
        current_state = orchestrator.run_pipeline(current_state)
    except Exception as e:
        print(f"[Init Warning] 初次載入資料異常: {e}", flush=True)

import base64

class SurveyHandler(BaseHTTPRequestHandler):
    def check_auth(self) -> bool:
        """檢查是否具備管理員權限"""
        auth_header = self.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Basic "):
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="Admin Access Required"')
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<h1>401 Unauthorized: \xe8\xab\x8b\xe8\xbc\x98\xe5\x85\xa5\xe7\xae\xa1\xe7\x90\x86\xe5\x93\xa1\xe5\xb8\xb3\xe8\x99\x9f\xe8\x88\x87\xe5\xaf\x86\xe7\xa2\xbc</h1>")
            return False

        try:
            encoded_credentials = auth_header.split(" ", 1)[1]
            decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
            username, password = decoded_credentials.split(":", 1)
            if username == config.ADMIN_USERNAME and password == config.ADMIN_PASSWORD:
                return True
        except Exception:
            pass

        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="Admin Access Required"')
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"<h1>401 Unauthorized: \xe5\xb8\xb3\xe8\x99\x9f\xe6\x88\x96\xe5\xaf\x86\xe7\xa2\xbc\xe9\x8c\xaf\xe8\xaa\xa4</h1>")
        return False

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query_params = parse_qs(parsed.query)

        # 1. 根目錄：學員手機端問卷 (公開，免密碼)
        if path in ("/", "/index.html"):
            index_path = config.STATIC_DIR / "index.html"
            self.serve_file(index_path, "text/html; charset=utf-8")
            return

        # 2. 管理後台：視覺化多代理人儀表板 (需要管理員密碼保護！)
        if path in ("/admin", "/dashboard", "/dashboard.html"):
            if not self.check_auth():
                return
            dashboard_path = config.STATIC_DIR / "dashboard.html"
            self.serve_file(dashboard_path, "text/html; charset=utf-8")
            return

        # 3. 班級設定 API (/api/class-info?class_id=...) (公開)
        if path == "/api/class-info":
            cid = query_params.get("class_id", [None])[0]
            if cid == "":
                cid = None
            class_info = config.get_class_info(cid)
            self.send_json(200, class_info)
            return

        # 3.1 班級清單 API (/api/classes-list)
        if path == "/api/classes-list":
            cfg = config.load_classes_config()
            self.send_json(200, {
                "active_class_id": cfg.get("active_class_id", "dawei_studio_01"),
                "classes": cfg.get("classes", {})
            })
            return

        # 4. 靜態檔案 (/static/...) (公開)
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

        # 5. 報告預覽與列印 (/report/html) (需要管理員密碼保護！)
        if path == "/report/html":
            if not self.check_auth():
                return
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

        # 6. 報告 Markdown 下載 (/report/markdown) (需要管理員密碼保護！)
        if path == "/report/markdown":
            if not self.check_auth():
                return
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

        # 7. API: 統計資訊 (/api/stats?class_id=...) (公開)
        if path == "/api/stats":
            cid = query_params.get("class_id", [None])[0]
            if cid == "":
                cid = None
            stats = self.get_survey_stats(class_id=cid)
            self.send_json(200, stats)
            return

        # 8. API: 所有回應資料與名冊 (/api/responses?class_id=...) (嚴格保護：必須驗證管理員密碼！)
        if path == "/api/responses":
            if not self.check_auth():
                return
            cid = query_params.get("class_id", [None])[0]
            if cid == "":
                cid = None
            responses = self.get_all_responses(class_id=cid)
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
            if data.get("wants_reward") == "no":
                data["student_name"] = data.get("student_name") or "匿名學員"
                data["selected_reward_course"] = "無需兌換 (純回饋)"
                data["phone"] = ""
                data["line_id"] = ""
                data["email"] = ""

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

        # 更新班級與問卷文案設定 (/api/update-class) (需要管理員密碼保護！)
        if parsed.path == "/api/update-class":
            if not self.check_auth():
                return
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

        # 同步雲端回饋資料到本機 (/api/sync-cloud) (需要管理員密碼保護！)
        if parsed.path == "/api/sync-cloud":
            if not self.check_auth():
                return
            try:
                import urllib.request, ssl, base64
                ctx = ssl._create_unverified_context()
                cloud_url = "https://dawei-survey.onrender.com/api/responses"
                req = urllib.request.Request(cloud_url)
                auth = base64.b64encode(f"{config.ADMIN_USERNAME}:{config.ADMIN_PASSWORD}".encode()).decode("ascii")
                req.add_header("Authorization", f"Basic {auth}")
                with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))
                    rows = resp_data.get("data", [])

                fieldnames = [
                    "timestamp", "class_id", "student_name", "phone", "line_id", "email",
                    "prior_experience", "key_progress", "struggle_point", "instructor_rating",
                    "instructor_comment", "course_rating", "ta_rating", "ta_comment",
                    "platform_experience", "nps_score", "selected_reward_course", "wants_reward"
                ]
                with open(config.RESPONSES_CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                    writer.writeheader()
                    for r in rows:
                        writer.writerow(r)

                if config.RESPONSES_CSV_PATH.exists():
                    current_state.df = pd.read_csv(config.RESPONSES_CSV_PATH)

                self.send_json(200, {"status": "success", "message": f"🎉 成功從雲端同步 {len(rows)} 筆最新填答！", "count": len(rows)})
            except Exception as e:
                self.send_json(500, {"status": "error", "message": f"同步失敗: {str(e)}"})
            return

        # 觸發多代理協同分析 (/api/analyze) (需要管理員密碼保護！)
        if parsed.path == "/api/analyze":
            if not self.check_auth():
                return
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

        # AI 課綱解析與問卷生成 (/api/generate-from-syllabus) (需要管理員密碼保護！)
        if parsed.path == "/api/generate-from-syllabus":
            if not self.check_auth():
                return
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                payload = json.loads(body)
                pdf_base64 = payload.get("pdf_base64", "")
                syllabus_text = payload.get("syllabus_text", "")
                hints = {
                    "course_name": payload.get("course_name", ""),
                    "teacher_name": payload.get("teacher_name", ""),
                    "organizer": payload.get("organizer", "")
                }

                if pdf_base64:
                    raw_pdf_bytes = base64.b64decode(pdf_base64)
                    extracted = syllabus_agent.extract_text_from_pdf(raw_pdf_bytes)
                    if extracted:
                        syllabus_text = extracted + ("\n\n" + syllabus_text if syllabus_text else "")

                if not syllabus_text.strip():
                    self.send_json(400, {"status": "error", "message": "未能由上傳檔案或輸入中讀取到課綱文字，請確認 PDF 是否含文字或直接貼上大綱"})
                    return

                generated_config = syllabus_agent.generate_survey_config(syllabus_text, hints)
                self.send_json(200, {
                    "status": "success",
                    "preview": generated_config,
                    "extracted_text_preview": syllabus_text[:300] + ("..." if len(syllabus_text) > 300 else "")
                })
            except Exception as e:
                self.send_json(500, {"status": "error", "message": f"AI 課綱分析處理異常: {str(e)}"})
            return

        # 套用課綱生成問卷 (/api/apply-syllabus-survey) (需要管理員密碼保護！)
        if parsed.path == "/api/apply-syllabus-survey":
            if not self.check_auth():
                return
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                new_class_data = json.loads(body)
                cid = new_class_data.get("class_id") or f"class_{int(datetime.now().timestamp())}"
                new_class_data["class_id"] = cid

                cfg = config.load_classes_config()
                if "classes" not in cfg:
                    cfg["classes"] = {}
                cfg["classes"][cid] = new_class_data
                cfg["active_class_id"] = cid

                with open(config.CLASSES_JSON_PATH, "w", encoding="utf-8") as f:
                    json.dump(cfg, f, ensure_ascii=False, indent=2)

                # 更新全域狀態之課程與機構名稱
                current_state.course_name = new_class_data.get("course_name", current_state.course_name)
                current_state.organizer = new_class_data.get("organizer", current_state.organizer)

                self.send_json(200, {
                    "status": "success",
                    "message": f"🎉 課綱問卷「{new_class_data.get('course_name')}」已成功發布！",
                    "class_id": cid,
                    "survey_url": f"/?class={cid}"
                })
            except Exception as e:
                self.send_json(400, {"status": "error", "message": str(e)})
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
            "platform_experience", "nps_score", "selected_reward_course", "wants_reward"
        ]
        file_exists = file_path.exists()
        
        with open(file_path, mode="a", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            if not file_exists or file_path.stat().st_size == 0:
                writer.writeheader()
            writer.writerow(row_dict)

    def get_all_responses(self, class_id=None):
        file_path = config.RESPONSES_CSV_PATH
        if not file_path.exists():
            return []
        rows = []
        with open(file_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for r in reader:
                if class_id and r.get("class_id") and r.get("class_id") != class_id:
                    continue
                rows.append(r)
        return rows

    def get_survey_stats(self, class_id=None):
        responses = self.get_all_responses(class_id=class_id)
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
