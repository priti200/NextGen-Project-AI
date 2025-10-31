"""
Summarization schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class SummaryType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    SPRINT = "sprint"
    CUSTOM = "custom"


class SummaryFormat(str, Enum):
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    PLAIN_TEXT = "plain_text"


class TargetAudience(str, Enum):
    TEAM = "team"
    MANAGER = "manager"
    STAKEHOLDER = "stakeholder"
    EXECUTIVE = "executive"


class SummaryRequest(BaseModel):
    project_key: str
    start_date: datetime
    end_date: datetime
    summary_type: SummaryType = SummaryType.CUSTOM
    target_audience: TargetAudience = TargetAudience.MANAGER
    
    include_progress: bool = True
    include_risks: bool = True
    include_blockers: bool = True
    include_achievements: bool = True
    include_metrics: bool = True
    
    format: SummaryFormat = SummaryFormat.MARKDOWN


class Highlight(BaseModel):
    title: str
    description: str
    category: str = Field(..., description="achievement, risk, blocker, metric")
    importance: float = Field(..., ge=0, le=1)
    timestamp: datetime


class ActionItem(BaseModel):
    description: str
    priority: str = Field(..., description="low, medium, high, critical")
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None


class SummaryResponse(BaseModel):
    summary_id: str
    project_key: str
    generated_at: datetime
    
    summary_text: str = Field(..., description="Natural language summary")
    highlights: List[Highlight]
    action_items: List[ActionItem]
    
    metrics_snapshot: Dict[str, float] = Field(default_factory=dict)
    format: SummaryFormat


class DailySummary(BaseModel):
    project_key: str
    date: datetime
    
    summary_text: str
    completed_yesterday: List[str]
    planned_today: List[str]
    blockers: List[str]
    team_updates: List[str]
    
    format: SummaryFormat


class WeeklySummary(BaseModel):
    project_key: str
    week_start: datetime
    week_end: datetime
    
    summary_text: str
    
    sprint_progress_percent: float
    velocity_comparison: str
    major_achievements: List[str]
    risks_and_blockers: List[str]
    next_week_plan: List[str]
    
    format: SummaryFormat


class StakeholderReport(BaseModel):
    project_key: str
    report_period_start: datetime
    report_period_end: datetime
    generated_at: datetime
    
    executive_summary: str
    project_status: str = Field(..., description="on_track, at_risk, delayed")
    
    key_achievements: List[str]
    critical_risks: List[str]
    resource_utilization_percent: float
    
    upcoming_deliverables: List[Dict[str, str]]
    recommendations: List[str]
    
    format: SummaryFormat
    document_url: Optional[str] = Field(None, description="URL for PDF/HTML report")
