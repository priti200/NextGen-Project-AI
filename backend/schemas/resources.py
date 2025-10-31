"""
Resource allocation schemas
"""

from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class WorkloadLevel(str, Enum):
    UNDERUTILIZED = "underutilized"  # < 50%
    OPTIMAL = "optimal"  # 50-80%
    OVERLOADED = "overloaded"  # > 80%
    CRITICAL = "critical"  # > 100%


class Assignment(BaseModel):
    id: str
    type: str = Field(..., description="jira_issue, github_pr, review")
    title: str
    url: str
    estimated_hours: float
    priority: str


class TeamMember(BaseModel):
    email: EmailStr
    name: str
    role: str
    team: Optional[str]
    
    current_assignments: List[Assignment]
    total_workload_hours: float
    capacity_hours: float
    utilization_percent: float
    workload_level: WorkloadLevel
    
    skills: List[str] = []
    availability_status: str = Field(..., description="available, limited, on_leave")


class WorkloadDistribution(BaseModel):
    project_key: str
    timestamp: datetime
    
    overloaded_members: List[TeamMember]
    underutilized_members: List[TeamMember]
    optimal_members: List[TeamMember]
    
    avg_utilization: float
    max_utilization: float
    min_utilization: float
    
    total_capacity_hours: float
    total_workload_hours: float


class CapacityPlan(BaseModel):
    project_key: str
    sprint_id: Optional[str]
    
    total_capacity_points: int
    committed_points: int
    remaining_capacity_points: int
    
    team_members_count: int
    available_hours: float
    
    predicted_completion_rate: float = Field(..., description="Probability of completing committed work")


class ReallocationSuggestion(BaseModel):
    from_member: EmailStr
    to_member: EmailStr
    assignment: Assignment
    reason: str
    impact_score: float = Field(..., description="Positive impact of reallocation")


class ResourceMap(BaseModel):
    project_key: str
    last_updated: datetime
    
    team_members: List[TeamMember]
    workload_distribution: WorkloadDistribution
    capacity_summary: CapacityPlan
