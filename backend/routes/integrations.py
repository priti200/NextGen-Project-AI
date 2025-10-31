"""
Integration endpoints - Jira, GitHub, Slack integration management
"""

from fastapi import APIRouter, Depends, Query, Body, HTTPException, status, BackgroundTasks
from typing import Optional, List

from schemas.integrations import (
    JiraConfig,
    GitHubConfig,
    SlackConfig,
    SyncStatus,
    WebhookPayload,
    SlackMessageRequest
)
from core.auth import get_current_user
from services.integration_service import IntegrationService

router = APIRouter()


# Jira Integration
@router.post("/integrations/jira/configure")
async def configure_jira(
    config: JiraConfig = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Configure Jira integration
    
    Sets up connection to Jira instance and validates credentials
    """
    service = IntegrationService()
    result = await service.configure_jira(config)
    return result


@router.post("/integrations/jira/sync")
async def sync_jira_data(
    project_key: str = Query(..., description="Jira project key"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: dict = Depends(get_current_user)
):
    """
    Trigger manual sync of Jira data
    
    Fetches latest issues, sprints, and activities
    """
    service = IntegrationService()
    background_tasks.add_task(service.sync_jira, project_key)
    return {"status": "sync_started", "project_key": project_key}


@router.get("/integrations/jira/status", response_model=SyncStatus)
async def get_jira_sync_status(
    project_key: str = Query(..., description="Jira project key"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get Jira sync status
    """
    service = IntegrationService()
    status = await service.get_jira_sync_status(project_key)
    return status


# GitHub Integration
@router.post("/integrations/github/configure")
async def configure_github(
    config: GitHubConfig = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Configure GitHub integration
    
    Sets up connection to GitHub organization/repos and validates token
    """
    service = IntegrationService()
    result = await service.configure_github(config)
    return result


@router.post("/integrations/github/sync")
async def sync_github_data(
    repo_name: str = Query(..., description="GitHub repository name"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: dict = Depends(get_current_user)
):
    """
    Trigger manual sync of GitHub data
    
    Fetches latest PRs, commits, issues, and CI/CD status
    """
    service = IntegrationService()
    background_tasks.add_task(service.sync_github, repo_name)
    return {"status": "sync_started", "repo_name": repo_name}


@router.get("/integrations/github/status", response_model=SyncStatus)
async def get_github_sync_status(
    repo_name: str = Query(..., description="GitHub repository name"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get GitHub sync status
    """
    service = IntegrationService()
    status = await service.get_github_sync_status(repo_name)
    return status


@router.post("/integrations/github/webhook")
async def github_webhook(
    payload: WebhookPayload = Body(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    GitHub webhook endpoint
    
    Receives real-time events from GitHub (PRs, commits, CI/CD)
    No authentication required - uses webhook secret validation
    """
    service = IntegrationService()
    background_tasks.add_task(service.process_github_webhook, payload)
    return {"status": "accepted"}


# Slack Integration
@router.post("/integrations/slack/configure")
async def configure_slack(
    config: SlackConfig = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Configure Slack integration
    
    Sets up Slack bot and validates tokens
    """
    service = IntegrationService()
    result = await service.configure_slack(config)
    return result


@router.post("/integrations/slack/send-message")
async def send_slack_message(
    message_request: SlackMessageRequest = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Send message to Slack channel
    
    Used for delivering summaries and notifications
    """
    service = IntegrationService()
    result = await service.send_slack_message(message_request)
    return result


@router.post("/integrations/slack/webhook")
async def slack_webhook(
    payload: dict = Body(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Slack events webhook endpoint
    
    Receives events from Slack (mentions, commands, messages)
    """
    # Handle Slack URL verification challenge
    if payload.get("type") == "url_verification":
        return {"challenge": payload.get("challenge")}
    
    service = IntegrationService()
    background_tasks.add_task(service.process_slack_event, payload)
    return {"status": "accepted"}


@router.post("/integrations/slack/schedule-summary")
async def schedule_slack_summary(
    channel_id: str = Query(..., description="Slack channel ID"),
    frequency: str = Query(..., description="daily or weekly"),
    time: str = Query(..., description="Time in HH:MM format (UTC)"),
    project_key: str = Query(..., description="Project identifier"),
    current_user: dict = Depends(get_current_user)
):
    """
    Schedule automated summary delivery to Slack
    """
    service = IntegrationService()
    result = await service.schedule_slack_summary(
        channel_id=channel_id,
        frequency=frequency,
        time=time,
        project_key=project_key
    )
    return result


# General Integration Management
@router.get("/integrations/status")
async def get_all_integrations_status(
    current_user: dict = Depends(get_current_user)
):
    """
    Get status of all configured integrations
    """
    service = IntegrationService()
    status = await service.get_all_status()
    return status


@router.post("/integrations/refresh-all")
async def refresh_all_integrations(
    project_key: str = Query(..., description="Project identifier"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: dict = Depends(get_current_user)
):
    """
    Refresh data from all configured integrations
    """
    service = IntegrationService()
    background_tasks.add_task(service.refresh_all, project_key)
    return {"status": "refresh_started", "project_key": project_key}
