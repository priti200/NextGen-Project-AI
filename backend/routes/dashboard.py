"""
Dashboard endpoints - Aggregated project metrics and KPIs
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional, List
from datetime import datetime, timedelta

from schemas.dashboard import (
    DashboardResponse,
    ProjectMetrics,
    SprintVelocity,
    BurndownChart
)
from core.auth import get_current_user
from services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse)
async def get_project_dashboard(
    project_key: str = Query(..., description="Jira project key"),
    sprint_id: Optional[str] = Query(None, description="Sprint ID (optional, defaults to active sprint)"),
    start_date: Optional[datetime] = Query(None, description="Start date for metrics"),
    end_date: Optional[datetime] = Query(None, description="End date for metrics"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get aggregated project dashboard with KPIs
    
    Returns:
    - Backlog status (open, in progress, done)
    - Sprint velocity
    - Burndown chart data
    - Open PRs and issues count
    - CI/CD status
    - Team velocity trends
    """
    try:
        service = DashboardService()
        dashboard_data = await service.get_dashboard(
            project_key=project_key,
            sprint_id=sprint_id,
            start_date=start_date,
            end_date=end_date
        )
        return dashboard_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard: {str(e)}"
        )


@router.get("/dashboard/metrics", response_model=ProjectMetrics)
async def get_project_metrics(
    project_key: str = Query(..., description="Jira project key"),
    days: int = Query(30, description="Number of days for historical metrics"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed project metrics over time
    
    Returns metrics including:
    - Issue creation/closure rates
    - PR merge rates
    - Test pass rates
    - Deployment frequency
    """
    service = DashboardService()
    metrics = await service.get_metrics(project_key=project_key, days=days)
    return metrics


@router.get("/dashboard/velocity", response_model=List[SprintVelocity])
async def get_sprint_velocity(
    project_key: str = Query(..., description="Jira project key"),
    num_sprints: int = Query(6, description="Number of past sprints to include"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get sprint velocity trends
    
    Returns velocity data for the last N sprints
    """
    service = DashboardService()
    velocity = await service.get_velocity(project_key=project_key, num_sprints=num_sprints)
    return velocity


@router.get("/dashboard/burndown", response_model=BurndownChart)
async def get_burndown_chart(
    project_key: str = Query(..., description="Jira project key"),
    sprint_id: Optional[str] = Query(None, description="Sprint ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get burndown chart data for current or specified sprint
    """
    service = DashboardService()
    burndown = await service.get_burndown(project_key=project_key, sprint_id=sprint_id)
    return burndown


@router.get("/dashboard/github-activity")
async def get_github_activity(
    repo_name: str = Query(..., description="GitHub repository name"),
    days: int = Query(7, description="Number of days for activity"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get GitHub activity summary
    
    Returns:
    - Open PRs count
    - PRs merged in period
    - Open issues count
    - Recent commits
    - CI/CD status
    """
    service = DashboardService()
    activity = await service.get_github_activity(repo_name=repo_name, days=days)
    return activity


@router.get("/dashboard/ci-status")
async def get_ci_status(
    project_key: str = Query(..., description="Project identifier"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get CI/CD pipeline status across repositories
    """
    service = DashboardService()
    ci_status = await service.get_ci_status(project_key=project_key)
    return ci_status
