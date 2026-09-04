import argparse
import sys
from pathlib import Path
import pandas as pd

import config
from core.state import SurveyAnalysisState
from core.orchestrator import SurveyOrchestrator
from utils.exporter import export_markdown, export_html
from data.sample_generator import generate_responses, save_csv

def run_analysis_cli():
    print("============================================================")
    print("🤖 啟動【班級結業問卷分析師 多代理協同 AI Agent】")
    print(f"📚 標的課程：{config.COURSE_NAME}")
    print(f"🏢 主辦單位：{config.ORGANIZER}")
    print("============================================================\n")

    csv_path = config.RESPONSES_CSV_PATH
    if not csv_path.exists():
        print(f"⚠️ 找不到問卷資料，正在自動生成 45 筆擬真範例資料...")
        data = generate_responses(45)
        save_csv(csv_path, data)

    df = pd.read_csv(csv_path)
    state = SurveyAnalysisState(
        course_name=config.COURSE_NAME,
        organizer=config.ORGANIZER,
        df=df
    )

    orchestrator = SurveyOrchestrator()

    def progress_callback(agent_name, percent, msg):
        bar = "█" * (percent // 5) + "░" * (20 - (percent // 5))
        print(f"[{percent:3d}%] [{bar}] {agent_name} -> {msg}")

    analyzed_state = orchestrator.run_pipeline(state, progress_callback=progress_callback)

    print("\n============================================================")
    print("✨ 多代理協同分析完畢！分析關鍵指標摘要：")
    print("============================================================")
    qm = analyzed_state.quant_metrics
    print(f"📊 大維老師授課均分：{qm.get('avg_instructor')} ★ (標準差 {qm.get('std_instructor')})")
    print(f"🤝 助教支援滿意均分：{qm.get('avg_ta')} ★ (標準差 {qm.get('std_ta')})")
    print(f"🚀 淨推薦值 (NPS)：  +{qm.get('nps')} (推薦者比例: {qm.get('promoters_pct')}%)")
    print(f"💬 質化正向情緒比：  {analyzed_state.text_insights.get('sentiment_ratio', {}).get('positive')}%")
    print(f"\n【執行摘要】\n{analyzed_state.executive_summary}\n")

    # 匯出報告
    report_md_path = config.DATA_DIR / "final_report.md"
    report_html_path = config.DATA_DIR / "final_report.html"
    export_markdown(analyzed_state.final_report_md, report_md_path)
    export_html(analyzed_state.final_report_md, f"{config.COURSE_NAME} 結業審查報告", report_html_path)

    print(f"📄 Markdown 報告已匯出至: {report_md_path}")
    print(f"🌐 可列印 HTML 報告已匯出至: {report_html_path}")
    print("============================================================")

def main():
    parser = argparse.ArgumentParser(description="班級結業問卷分析師 多代理協同 AI Agent")
    parser.add_argument("--serve", action="store_true", help="啟動問卷收集與管理後台伺服器")
    parser.add_argument("--port", type=int, default=config.SURVEY_SERVER_PORT, help="伺服器連接埠 (預設 8080)")
    parser.add_argument("--analyze", action="store_true", help="執行 CLI 多代理人問卷分析並產出報告")
    parser.add_argument("--reset-sample", action="store_true", help="重設為 45 筆擬真問卷資料")

    args = parser.parse_args()

    if args.reset_sample:
        print("正在重設問卷範例資料庫...")
        data = generate_responses(45)
        save_csv(config.RESPONSES_CSV_PATH, data)
        print("重設完成！")
        return

    if args.analyze:
        run_analysis_cli()
        return

    if args.serve or len(sys.argv) == 1:
        from survey_server import run_server
        run_server(port=args.port)

if __name__ == "__main__":
    main()
