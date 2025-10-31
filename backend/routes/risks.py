"""
Risk prediction endpoints - Delay and risk assessment
"""

from fastapi import APIRouter, Depends, Query, Body, HTTPException, status
from typing import Optional, List
from datetime import datetime

from schemas.risks import (
    RiskPrediction,
    RiskRequest,
    ComponentRisk,
    DelayEstimate,
    RiskFactor,
    MitigationSuggestion
)
from core.auth import get_current_user
from services.risk_service import RiskService

router = APIRouter()


@router.post("/predict-risk", response_model=RiskPrediction)
async def predict_risk(
    risk_request: RiskRequest = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Predict risks and delays for a component or sprint
    
    Input:
    - Project key
    - Component/module name
    - Sprint ID (optional)
    - Historical context
    
    Returns:
    - Risk score (0-1)
    - Probability of delay
    - Estimated delay (in days)
    - Contributing risk factors
    - Explainability data
    """
    service = RiskService()
    prediction = await service.predict_risk(risk_request)
    return prediction


@router.get("/risks/component/{component_name}", response_model=ComponentRisk)
async def get_component_risk(
    component_name: str,
    project_key: str = Query(..., description="Project identifier"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get risk assessment for a specific component
    
    Returns:
    - Current risk level
    - Open blockers
    - Dependency issues
    - Test coverage gaps
    - Historical risk trends
    """
    service = RiskService()
    risk = await service.get_component_risk(
        component_name=component_name,
        project_key=project_key
    )
    return risk


@router.get("/risks/project", response_model=List[ComponentRisk])
async def get_project_risks(
    project_key: str = Query(..., description="Project identifier"),
    severity: Optional[str] = Query(None, description="Filter by severity (low, medium, high, critical)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all risks for a project, sorted by severity
    """
    service = RiskService()
    risks = await service.get_project_risks(
        project_key=project_key,
        severity=severity
    )
    return risks


@router.get("/risks/sprint", response_model=RiskPrediction)
async def get_sprint_risk(
    project_key: str = Query(..., description="Project identifier"),
    sprint_id: Optional[str] = Query(None, description="Sprint ID (defaults to active)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get overall risk assessment for a sprint
    
    Returns:
    - Sprint completion probability
    - Estimated delay
    - At-risk stories/tasks
    - Blocker analysis
    """
    service = RiskService()
    risk = await service.get_sprint_risk(
        project_key=project_key,
        sprint_id=sprint_id
    )
    return risk


@router.get("/risks/delay-estimate", response_model=DelayEstimate)
async def estimate_delay(
    project_key: str = Query(..., description="Project identifier"),
    component_name: Optional[str] = Query(None, description="Component name"),
    issue_key: Optional[str] = Query(None, description="Jira issue key"),
    current_user: dict = Depends(get_current_user)
):
    """
    Estimate delay for a specific component or issue
    
    Uses historical data and current signals to predict:
    - Expected completion date
    - Probability of meeting deadline
    - Confidence interval
    """
    if not component_name and not issue_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either component_name or issue_key must be provided"
        )
    
    service = RiskService()
    estimate = await service.estimate_delay(
        project_key=project_key,
        component_name=component_name,
        issue_key=issue_key
    )
    return estimate


@router.get("/risks/factors", response_model=List[RiskFactor])
async def get_risk_factors(
    project_key: str = Query(..., description="Project identifier"),
    component_name: Optional[str] = Query(None, description="Component name"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed breakdown of risk factors
    
    Returns ranked list of contributing factors:
    - Blocker count
    - PR age
    - Test failure rate
    - Dependency issues
    - Team capacity
    - Historical patterns
    """
    service = RiskService()
    factors = await service.get_risk_factors(
        project_key=project_key,
        component_name=component_name
    )
    return factors


@router.post("/risks/mitigation", response_model=List[MitigationSuggestion])
async def get_mitigation_suggestions(
    project_key: str = Query(..., description="Project identifier"),
    risk_id: str = Query(..., description="Risk identifier"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get AI-generated mitigation suggestions for a specific risk
    
    Returns actionable recommendations to reduce risk
    """
    service = RiskService()
    suggestions = await service.get_mitigation_suggestions(
        project_key=project_key,
        risk_id=risk_id
    )
    return suggestions
