"""
Risk prediction schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class RiskSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskFactor(BaseModel):
    factor_name: str
    contribution_score: float = Field(..., ge=0, le=1)
    description: str
    evidence: List[str] = Field(default_factory=list)


class DelayEstimate(BaseModel):
    component_name: Optional[str]
    issue_key: Optional[str]
    
    expected_completion_date: datetime
    original_due_date: Optional[datetime]
    estimated_delay_days: int
    
    probability_on_time: float = Field(..., ge=0, le=1)
    confidence_interval_days: int


class ComponentRisk(BaseModel):
    component_name: str
    project_key: str
    
    risk_score: float = Field(..., ge=0, le=1)
    severity: RiskSeverity
    
    open_blockers: int
    dependency_issues: int
    test_coverage_percent: Optional[float]
    pr_age_avg_days: float
    
    risk_factors: List[RiskFactor]
    last_assessed: datetime


class RiskRequest(BaseModel):
    project_key: str
    component_name: Optional[str] = None
    sprint_id: Optional[str] = None
    issue_keys: Optional[List[str]] = None


class RiskPrediction(BaseModel):
    project_key: str
    component_name: Optional[str]
    sprint_id: Optional[str]
    
    risk_score: float = Field(..., ge=0, le=1, description="Overall risk score")
    severity: RiskSeverity
    
    delay_probability: float = Field(..., ge=0, le=1)
    estimated_delay_days: int
    
    top_risk_factors: List[RiskFactor]
    
    explanation: str = Field(..., description="Human-readable explanation")
    confidence: float = Field(..., ge=0, le=1)
    
    assessed_at: datetime = Field(default_factory=datetime.utcnow)


class MitigationSuggestion(BaseModel):
    risk_id: str
    suggestion: str
    action_items: List[str]
    estimated_impact: str = Field(..., description="low, medium, high")
    effort_required: str = Field(..., description="low, medium, high")
