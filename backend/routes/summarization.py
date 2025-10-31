"""
Summarization endpoints - AI-generated status reports and summaries
"""

from fastapi import APIRouter, Depends, Query, Body, HTTPException, status
from typing import Optional, List
from datetime import datetime, timedelta

from schemas.summarization import (
    SummaryRequest,
    SummaryResponse,
    DailySummary,
    WeeklySummary,
    StakeholderReport,
    SummaryFormat
)
from core.auth import get_current_user
from services.summarization_service import SummarizationService

router = APIRouter()


@router.post("/summarize", response_model=SummaryResponse)
async def generate_summary(
    summary_request: SummaryRequest = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate AI-powered plain-language summary
    
    Input:
    - Project key
    - Time range (start_date, end_date)
    - Summary type (daily, weekly, custom)
    - Target audience (manager, stakeholder, team)
    - Include sections (progress, risks, blockers, achievements)
    
    Returns:
    - Natural language summary
    - Key highlights
    - Action items
    - Metrics snapshot
    """
    service = SummarizationService()
    summary = await service.generate_summary(summary_request)
    return summary


@router.get("/summarize/daily", response_model=DailySummary)
async def get_daily_summary(
    project_key: str = Query(..., description="Project identifier"),
    date: Optional[datetime] = Query(None, description="Date for summary (defaults to today)"),
    format: SummaryFormat = Query(SummaryFormat.MARKDOWN, description="Output format"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get daily summary for a project
    
    Returns:
    - Work completed yesterday
    - Today's focus areas
    - Blockers and risks
    - Team updates
    """
    service = SummarizationService()
    summary = await service.get_daily_summary(
        project_key=project_key,
        date=date or datetime.utcnow(),
        format=format
    )
    return summary


@router.get("/summarize/weekly", response_model=WeeklySummary)
async def get_weekly_summary(
    project_key: str = Query(..., description="Project identifier"),
    week_start: Optional[datetime] = Query(None, description="Week start date"),
    format: SummaryFormat = Query(SummaryFormat.MARKDOWN, description="Output format"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get weekly summary for a project
    
    Returns:
    - Sprint progress
    - Velocity trends
    - Major achievements
    - Risks and blockers
    - Next week's plan
    """
    service = SummarizationService()
    summary = await service.get_weekly_summary(
        project_key=project_key,
        week_start=week_start,
        format=format
    )
    return summary


@router.post("/summarize/stakeholder", response_model=StakeholderReport)
async def generate_stakeholder_report(
    project_key: str = Query(..., description="Project identifier"),
    start_date: datetime = Query(..., description="Report start date"),
    end_date: datetime = Query(..., description="Report end date"),
    include_risks: bool = Query(True, description="Include risk section"),
    include_metrics: bool = Query(True, description="Include metrics"),
    format: SummaryFormat = Query(SummaryFormat.PDF, description="Output format"),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate executive-level stakeholder report
    
    Returns:
    - High-level project status
    - Key achievements and milestones
    - Critical risks
    - Resource utilization
    - Upcoming deliverables
    - Recommendations
    """
    service = SummarizationService()
    report = await service.generate_stakeholder_report(
        project_key=project_key,
        start_date=start_date,
        end_date=end_date,
        include_risks=include_risks,
        include_metrics=include_metrics,
        format=format
    )
    return report


@router.get("/summarize/sprint")
async def get_sprint_summary(
    project_key: str = Query(..., description="Project identifier"),
    sprint_id: Optional[str] = Query(None, description="Sprint ID (defaults to active)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get sprint summary with AI-generated insights
    
    Returns:
    - Sprint goals vs achievements
    - Completed vs planned story points
    - Carry-over items
    - Team performance
    - Key learnings
    """
    service = SummarizationService()
    summary = await service.get_sprint_summary(
        project_key=project_key,
        sprint_id=sprint_id
    )
    return summary


@router.get("/summarize/highlights")
async def get_highlights(
    project_key: str = Query(..., description="Project identifier"),
    days: int = Query(7, description="Number of days to look back"),
    limit: int = Query(5, description="Maximum number of highlights"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get key highlights and achievements
    
    Returns AI-curated list of most important updates
    """
    service = SummarizationService()
    highlights = await service.get_highlights(
        project_key=project_key,
        days=days,
        limit=limit
    )
    return highlights


@router.post("/summarize/feedback")
async def submit_feedback(
    summary_id: str = Query(..., description="Summary identifier"),
    rating: int = Body(..., ge=1, le=5, description="Rating 1-5"),
    feedback: Optional[str] = Body(None, description="Optional feedback text"),
    corrections: Optional[dict] = Body(None, description="Corrections for RLHF"),
    current_user: dict = Depends(get_current_user)
):
    """
    Submit feedback on generated summary for RLHF
    
    This endpoint collects human feedback to improve future summaries
    """
    service = SummarizationService()
    result = await service.submit_feedback(
        summary_id=summary_id,
        rating=rating,
        feedback=feedback,
        corrections=corrections,
        user=current_user
    )
    return result
