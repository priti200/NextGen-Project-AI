"""
Routes module initialization
"""

from . import (
    health,
    dashboard,
    resources,
    risks,
    summarization,
    integrations
)

__all__ = [
    "health",
    "dashboard",
    "resources",
    "risks",
    "summarization",
    "integrations"
]
