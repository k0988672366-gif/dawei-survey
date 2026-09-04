from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import pandas as pd

@dataclass
class SurveyAnalysisState:
    """多代理人協同分析共享狀態上下文"""
    course_name: str = "劉大維畫室直播課程"
    organizer: str = "赫綵設計學院"
    class_id: str = ""
    teacher_name: str = "授課講師"
    syllabus_topics: List[str] = field(default_factory=list)
    raw_responses: List[Dict[str, Any]] = field(default_factory=list)
    df: Optional[pd.DataFrame] = None
    
    # Agent 1: 檢驗與資料畫像
    inspection_summary: Dict[str, Any] = field(default_factory=dict)
    
    # Agent 2: 量化統計與 NPS
    quant_metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Agent 3: 質化語意與情緒主題
    text_insights: Dict[str, Any] = field(default_factory=dict)
    
    # Agent 4: 交叉因果與根因診斷
    cross_correlations: Dict[str, Any] = field(default_factory=dict)
    
    # Agent 5: 教學行動與覆盤策略
    pedagogical_strategies: Dict[str, Any] = field(default_factory=dict)
    
    # Agent 6: 總協調綜合審查報告
    final_report_md: str = ""
    executive_summary: str = ""
    
    # 執行軌跡與代理人日誌 (供前端動態監控)
    agent_logs: List[Dict[str, Any]] = field(default_factory=list)
    
    def log(self, agent_name: str, step: str, message: str, status: str = "success"):
        self.agent_logs.append({
            "agent": agent_name,
            "step": step,
            "message": message,
            "status": status
        })
