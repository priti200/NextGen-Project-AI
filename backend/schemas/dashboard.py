"""
Dashboard schemas - Request/Response models
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class IssueStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    BLOCKED = "blocked"


class BacklogStatus(BaseModel):
    todo: int = Field(..., description="Number of issues in backlog")
    in_progress: int = Field(..., description="Number of issues in progress")
    in_review: int = Field(..., description="Number of issues in review")
    done: int = Field(..., description="Number of completed issues")
    blocked: int = Field(..., description="Number of blocked issues")


class SprintVelocity(BaseModel):
    sprint_id: str
    sprint_name: str
    planned_points: int
    completed_points: int
    carry_over_points: int
    velocity: float
    start_date: datetime
    end_date: datetime


class BurndownPoint(BaseModel):
    date: datetime
    remaining_points: int
    ideal_points: int


class BurndownChart(BaseModel):
    sprint_id: str
    sprint_name: str
    data_points: List[BurndownPoint]
    total_points: int
    completed_points: int


class PRStatus(BaseModel):
    open_count: int
    merged_count: int
    avg_age_days: float
    oldest_pr_days: int


class CIStatus(BaseModel):
    total_runs: int
    success_rate: float
    failed_runs: int
    last_run_status: str
    last_run_time: datetime


class ProjectMetrics(BaseModel):
    project_key: str
    period_start: datetime
    period_end: datetime
    
    issues_created: int
    issues_closed: int
    issue_closure_rate: float
    
    prs_opened: int
    prs_merged: int
    pr_merge_rate: float
    avg_pr_review_time_hours: float
    
    test_pass_rate: float
    deployment_frequency: int
    
    active_contributors: int


class DashboardResponse(BaseModel):
    project_key: str
    project_name: str
    last_updated: datetime
    
    backlog_status: BacklogStatus
    current_sprint: Optional[SprintVelocity]
    burndown: Optional[BurndownChart]
    
    github_prs: PRStatus
    open_issues_count: int
    
    ci_status: CIStatus
    
    velocity_trend: List[float] = Field(..., description="Last 6 sprints velocity")
    risk_score: float = Field(..., ge=0, le=1, description="Overall project risk score")
