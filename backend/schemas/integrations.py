"""
Integration schemas
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class IntegrationType(str, Enum):
    JIRA = "jira"
    GITHUB = "github"
    SLACK = "slack"


class SyncState(str, Enum):
    IDLE = "idle"
    SYNCING = "syncing"
    SUCCESS = "success"
    FAILED = "failed"


class JiraConfig(BaseModel):
    base_url: HttpUrl
    email: str
    api_token: str
    project_keys: List[str]


class GitHubConfig(BaseModel):
    token: str
    organization: str
    repositories: List[str]


class SlackConfig(BaseModel):
    bot_token: str
    signing_secret: str
    default_channel: str
    notification_channels: Dict[str, str] = Field(
        default_factory=dict,
        description="Mapping of notification types to channel IDs"
    )


class SyncStatus(BaseModel):
    integration_type: IntegrationType
    state: SyncState
    last_sync: Optional[datetime]
    last_success: Optional[datetime]
    error_message: Optional[str] = None
    records_synced: int = 0


class WebhookPayload(BaseModel):
    event_type: str
    source: str
    payload: Dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SlackMessageRequest(BaseModel):
    channel_id: str
    text: str
    blocks: Optional[List[Dict]] = None
    thread_ts: Optional[str] = None
    
    # For rich formatting
    attachments: Optional[List[Dict]] = None
