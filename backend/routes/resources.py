"""
Resource allocation endpoints - Team workload and capacity management
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional, List
from datetime import datetime

from schemas.resources import (
    ResourceMap,
    TeamMember,
    WorkloadDistribution,
    CapacityPlan,
    ReallocationSuggestion
)
from core.auth import get_current_user
from services.resource_service import ResourceService

router = APIRouter()


@router.get("/resource-map", response_model=ResourceMap)
async def get_resource_map(
    project_key: str = Query(..., description="Project identifier"),
    include_teams: Optional[List[str]] = Query(None, description="Filter by team names"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get current resource allocation map
    
    Returns:
    - Workload per team member
    - Current assignments (Jira issues, GitHub PRs)
    - Capacity utilization percentage
    - Availability status
    """
    service = ResourceService()
    resource_map = await service.get_resource_map(
        project_key=project_key,
        include_teams=include_teams
    )
    return resource_map


@router.get("/resource-map/member/{email}", response_model=TeamMember)
async def get_member_details(
    email: str,
    project_key: str = Query(..., description="Project identifier"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed information about a specific team member
    
    Returns:
    - Current assignments
    - Workload metrics
    - Recent activity
    - Skills and roles
    """
    service = ResourceService()
    member = await service.get_member_details(email=email, project_key=project_key)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team member {email} not found"
        )
    return member


@router.get("/resource-map/workload", response_model=WorkloadDistribution)
async def get_workload_distribution(
    project_key: str = Query(..., description="Project identifier"),
    team_name: Optional[str] = Query(None, description="Filter by team"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get workload distribution across the team
    
    Returns:
    - Overloaded members (>80% capacity)
    - Underutilized members (<50% capacity)
    - Average workload
    - Distribution visualization data
    """
    service = ResourceService()
    distribution = await service.get_workload_distribution(
        project_key=project_key,
        team_name=team_name
    )
    return distribution


@router.get("/resource-map/capacity", response_model=CapacityPlan)
async def get_capacity_plan(
    project_key: str = Query(..., description="Project identifier"),
    sprint_id: Optional[str] = Query(None, description="Sprint ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get capacity planning information for sprint
    
    Returns:
    - Total team capacity
    - Committed story points
    - Remaining capacity
    - Predicted capacity vs actual
    """
    service = ResourceService()
    capacity = await service.get_capacity_plan(
        project_key=project_key,
        sprint_id=sprint_id
    )
    return capacity


@router.post("/resource-map/suggestions", response_model=List[ReallocationSuggestion])
async def get_reallocation_suggestions(
    project_key: str = Query(..., description="Project identifier"),
    threshold: float = Query(0.8, description="Overload threshold (0-1)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get AI-powered reallocation suggestions
    
    Analyzes current workload and suggests task reassignments
    to balance the load across team members
    """
    service = ResourceService()
    suggestions = await service.get_reallocation_suggestions(
        project_key=project_key,
        threshold=threshold
    )
    return suggestions


@router.get("/resource-map/availability")
async def get_team_availability(
    project_key: str = Query(..., description="Project identifier"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Get team availability calendar
    
    Returns:
    - Vacation schedules
    - Public holidays
    - Meetings and commitments
    - Available hours per member
    """
    service = ResourceService()
    availability = await service.get_availability(
        project_key=project_key,
        start_date=start_date,
        end_date=end_date
    )
    return availability
