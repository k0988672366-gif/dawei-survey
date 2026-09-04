import os
import sys
from pathlib import Path
import pandas as pd

# 引入設定與核心庫
import config
from core.state import SurveyAnalysisState
from core.orchestrator import SurveyOrchestrator
from utils.exporter import export_html, export_markdown

try:
    import streamlit as st
except ImportError:
    print("【提示】目前系統尚未安裝 Streamlit。")
    print("您可以隨時透過以下指令啟動內建的零依賴視覺化伺服器：")
    print("   python3 main.py --serve")
    print("或安裝 Streamlit 後再次執行：")
    print("   pip install streamlit plotly")
    sys.exit(0)

# Streamlit 頁面設定
st.set_page_config(
    page_title=f"{config.COURSE_NAME} 結業問卷多代理 AI 分析師",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 側邊欄：環境設定與控制
with st.sidebar:
    st.title("🎨 結業分析師 AI Agent")
    st.caption("劉大維畫室直播課程 ✕ 赫綵設計學院")
    
    st.markdown("---")
    st.subheader("⚙️ 引擎配置")
    api_key_input = st.text_input("Gemini API Key (選填)", value=config.GEMINI_API_KEY, type="password")
    if api_key_input:
        st.success("✨ 已啟用 Gemini 2.5 雲端大模型引擎")
    else:
        st.info("💡 運行於本機智慧啟發式推論引擎 (免 Key 開箱即用)")

    st.markdown("---")
    st.subheader("📱 學員手機端問卷入口")
    st.markdown(f"**本機網址**：`http://localhost:{config.SURVEY_SERVER_PORT}/`")
    st.caption("可在 LINE 群分享此連結，填完直接領取筆刷包！")
    
    if st.button("🔄 重新載入問卷資料庫"):
        st.rerun()

# 載入資料
csv_path = config.RESPONSES_CSV_PATH
if not csv_path.exists():
    from data.sample_generator import generate_responses, save_csv
    data = generate_responses(45)
    save_csv(csv_path, data)

df = pd.read_csv(csv_path)

# 初始化狀態與 Orchestrator
if "analysis_state" not in st.session_state:
    orchestrator = SurveyOrchestrator(api_key=api_key_input)
    init_state = SurveyAnalysisState(
        course_name=config.COURSE_NAME,
        organizer=config.ORGANIZER,
        df=df
    )
    st.session_state.analysis_state = orchestrator.run_pipeline(init_state)

state: SurveyAnalysisState = st.session_state.analysis_state
qm = state.quant_metrics
insp = state.inspection_summary
ti = state.text_insights
ps = state.pedagogical_strategies

# 主標題區
st.title("🎨 劉大維畫室直播課程 結業問卷多代理 AI 診斷系統")
st.markdown(f"**分析標的**：{state.course_name} ｜ **評鑑主辦**：{state.organizer} ｜ **有效問卷**：`{insp.get('total_responses', 0)}` 份")

# 頂部 KPI 卡片列
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("有效填答數", f"{insp.get('total_responses', 0)} 份", "完整度 100%")
with kpi2:
    st.metric("淨推薦值 (NPS)", f"+{qm.get('nps', 0)}", f"推薦者 {qm.get('promoters_pct', 0)}%")
with kpi3:
    st.metric("大維老師教學均分", f"{qm.get('avg_instructor', 5.0)} ★", f"標差 {qm.get('std_instructor', 0.0)}")
with kpi4:
    st.metric("助教輔導支援均分", f"{qm.get('avg_ta', 5.0)} ★", f"標差 {qm.get('std_ta', 0.0)}")

st.markdown("---")

# 分頁標籤
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🤖 多代理協同流程", 
    "📊 量化評分與 NPS", 
    "💬 質化語意與金句牆", 
    "🎯 教學迭代行動矩陣", 
    "📑 綜合診斷報告匯出", 
    "💡 AI 問卷即席諮詢"
])

# Tab 1: 多代理協同流程
with tab1:
    st.subheader("🤖 6+1 專業代理人協同推論日誌與狀態")
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.info("""
        **協同代理人陣容：**
        1. 🔍 **Inspector Agent** (資料檢驗與完整性分析)
        2. 📊 **Quant Agent** (量化指標、離散度與 NPS)
        3. 💬 **Text Miner Agent** (質化情感、主題與金句挖掘)
        4. 🧬 **Correlation Agent** (起點 vs 痛點深層歸因)
        5. 🎯 **Strategist Agent** (教學優化行動矩陣)
        6. 📑 **Chief Synthesizer** (總協調綜合審查報告)
        7. 💡 **Chat Advisor** (互動式即席問答顧問)
        """)
        if st.button("🚀 重新執行 6 大代理人協同分析"):
            with st.spinner("代理人團隊正在協同分析最新資料..."):
                orch = SurveyOrchestrator(api_key=api_key_input)
                new_state = SurveyAnalysisState(
                    course_name=config.COURSE_NAME,
                    organizer=config.ORGANIZER,
                    df=pd.read_csv(config.RESPONSES_CSV_PATH)
                )
                st.session_state.analysis_state = orch.run_pipeline(new_state)
            st.success("協同分析完成！")
            st.rerun()

    with col_b:
        st.markdown("#### 協同執行日誌 (Agent Execution Traces)")
        for log in state.agent_logs:
            st.markdown(f"**[{log['agent']}]** `{log['step']}` : {log['message']}")

# Tab 2: 量化與 NPS
with tab2:
    st.subheader("📊 教學維度與學員滿意度分佈")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 核心教學維度滿意度")
        st.dataframe(pd.DataFrame([
            {"評鑑維度": "大維老師授課與示範", "平均滿意度": f"{qm.get('avg_instructor')} ★", "標準差": qm.get('std_instructor')},
            {"評鑑維度": "課綱規劃與講義素材", "平均滿意度": f"{qm.get('avg_course')} ★", "標準差": qm.get('std_course')},
            {"評鑑維度": "助教課堂解惑與課後陪伴", "平均滿意度": f"{qm.get('avg_ta')} ★", "標準差": qm.get('std_ta')}
        ]), use_container_width=True, hide_index=True)

    with c2:
        st.markdown("#### NPS 淨推薦值指標")
        st.write(f"- **推薦者 (9-10分)**：{qm.get('promoters_count')} 人 ({qm.get('promoters_pct')}%)")
        st.write(f"- **被動者 (7-8分)**：{qm.get('passives_count')} 人 ({qm.get('passives_pct')}%)")
        st.write(f"- **批評者 (0-6分)**：{qm.get('detractors_count')} 人 ({qm.get('detractors_pct')}%)")
        st.progress(qm.get("promoters_pct", 0) / 100.0, text=f"口碑推薦強度：{qm.get('promoters_pct')}%")

# Tab 3: 質化與金句牆
with tab3:
    st.subheader("💬 學員原聲金句牆與情緒洞察")
    q_col1, q_col2 = st.columns(2)
    with q_col1:
        st.markdown("#### 🎨 大維老師教學魅力口碑金句")
        for g in ti.get("gold_quotes", []):
            st.success(f"「{g.get('quote')}」\n\n— **{g.get('student_name')}** ({g.get('experience')}, {g.get('rating')}★)")

    with q_col2:
        st.markdown("#### ⚠️ 教學警訊與示範節奏微調反饋")
        for a in ti.get("alert_quotes", []):
            st.warning(f"「{a.get('quote')}」\n\n— **{a.get('student_name')}** ({a.get('experience')})")

# Tab 4: 行動矩陣
with tab4:
    st.subheader("🎯 大維老師教學迭代行動矩陣")
    st.markdown("### 1. Eisenhower 優化行動矩陣")
    for qw in ps.get("action_matrix", {}).get("quick_wins", []):
        st.info(f"**【即刻速贏】{qw.get('title')}**\n\n{qw.get('detail')} (投入成本: {qw.get('effort')}, 預期成效: {qw.get('impact')})")
    for nc in ps.get("action_matrix", {}).get("next_cohort", []):
        st.info(f"**【次期優化】{nc.get('title')}**\n\n{nc.get('detail')} (投入成本: {nc.get('effort')}, 預期成效: {nc.get('impact')})")

    st.markdown("### 2. 大維老師個人教學覆盤指引")
    for tr in ps.get("teacher_reflection", []):
        st.markdown(f"- **{tr}**")

# Tab 5: 綜合報告匯出
with tab5:
    st.subheader("📑 高階結業診斷審查報告")
    st.download_button(
        label="📥 下載 Markdown 診斷報告",
        data=state.final_report_md,
        file_name="DaWei_Studio_Survey_Audit_Report.md",
        mime="text/markdown"
    )
    st.markdown("---")
    st.markdown(state.final_report_md)

# Tab 6: 即席問答顧問
with tab6:
    st.subheader("💡 Agent 7: 問卷即席諮詢顧問")
    st.caption("針對問卷數據，您可以向 AI 顧問提問任何管理或教學細節：")
    user_q = st.text_input("輸入您的問題：", placeholder="例如：零基礎學員在第幾週覺得最吃力？助教批改如何改進？")
    if st.button("向顧問提問"):
        if user_q:
            with st.spinner("AI 顧問正在調閱問卷數據思考中..."):
                orch = SurveyOrchestrator(api_key=api_key_input)
                ans = orch.ask_advisor(user_q, state)
            st.markdown("#### 🤖 顧問回覆：")
            st.write(ans)
