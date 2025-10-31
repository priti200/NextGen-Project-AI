"""
API Endpoints Registry - Complete list of all API endpoints
"""

API_ENDPOINTS = {
    "health": {
        "base_path": "/api/v1",
        "endpoints": [
            {
                "method": "GET",
                "path": "/health",
                "description": "Basic health check endpoint",
                "auth_required": False
            },
            {
                "method": "GET",
                "path": "/health/detailed",
                "description": "Detailed health check with system metrics",
                "auth_required": False
            }
        ]
    },
    
    "dashboard": {
        "base_path": "/api/v1",
        "endpoints": [
            {
                "method": "GET",
                "path": "/dashboard",
                "description": "Get aggregated project dashboard with KPIs",
                "auth_required": True,
                "query_params": ["project_key", "sprint_id?", "start_date?", "end_date?"]
            },
            {
                "method": "GET",
                "path": "/dashboard/metrics",
                "description": "Get detailed project metrics over time",
                "auth_required": True,
                "query_params": ["project_key", "days?"]
            },
            {
                "method": "GET",
                "path": "/dashboard/velocity",
                "description": "Get sprint velocity trends",
                "auth_required": True,
                "query_params": ["project_key", "num_sprints?"]
            },
            {
                "method": "GET",
                "path": "/dashboard/burndown",
                "description": "Get burndown chart data for sprint",
                "auth_required": True,
                "query_params": ["project_key", "sprint_id?"]
            },
            {
                "method": "GET",
                "path": "/dashboard/github-activity",
                "description": "Get GitHub activity summary",
                "auth_required": True,
                "query_params": ["repo_name", "days?"]
            },
            {
                "method": "GET",
                "path": "/dashboard/ci-status",
                "description": "Get CI/CD pipeline status",
                "auth_required": True,
                "query_params": ["project_key"]
            }
        ]
    },
    
    "resources": {
        "base_path": "/api/v1",
        "endpoints": [
            {
                "method": "GET",
                "path": "/resource-map",
                "description": "Get current resource allocation map",
                "auth_required": True,
                "query_params": ["project_key", "include_teams?"]
            },
            {
                "method": "GET",
                "path": "/resource-map/member/{email}",
                "description": "Get detailed information about a team member",
                "auth_required": True,
                "query_params": ["project_key"]
            },
            {
                "method": "GET",
                "path": "/resource-map/workload",
                "description": "Get workload distribution across team",
                "auth_required": True,
                "query_params": ["project_key", "team_name?"]
            },
            {
                "method": "GET",
                "path": "/resource-map/capacity",
                "description": "Get capacity planning information",
                "auth_required": True,
                "query_params": ["project_key", "sprint_id?"]
            },
            {
                "method": "POST",
                "path": "/resource-map/suggestions",
                "description": "Get AI-powered reallocation suggestions",
                "auth_required": True,
                "query_params": ["project_key", "threshold?"]
            },
            {
                "method": "GET",
                "path": "/resource-map/availability",
                "description": "Get team availability calendar",
                "auth_required": True,
                "query_params": ["project_key", "start_date?", "end_date?"]
            }
        ]
    },
    
    "risks": {
        "base_path": "/api/v1",
        "endpoints": [
            {
                "method": "POST",
                "path": "/predict-risk",
                "description": "Predict risks and delays using ML",
                "auth_required": True,
                "body": "RiskRequest"
            },
            {
                "method": "GET",
                "path": "/risks/component/{component_name}",
                "description": "Get risk assessment for a component",
                "auth_required": True,
                "query_params": ["project_key"]
            },
            {
                "method": "GET",
                "path": "/risks/project",
                "description": "Get all risks for a project",
                "auth_required": True,
                "query_params": ["project_key", "severity?"]
            },
            {
                "method": "GET",
                "path": "/risks/sprint",
                "description": "Get overall risk assessment for sprint",
                "auth_required": True,
                "query_params": ["project_key", "sprint_id?"]
            },
            {
                "method": "GET",
                "path": "/risks/delay-estimate",
                "description": "Estimate delay for component or issue",
                "auth_required": True,
                "query_params": ["project_key", "component_name?", "issue_key?"]
            },
            {
                "method": "GET",
                "path": "/risks/factors",
                "description": "Get detailed breakdown of risk factors",
                "auth_required": True,
                "query_params": ["project_key", "component_name?"]
            },
            {
                "method": "POST",
                "path": "/risks/mitigation",
                "description": "Get AI-generated mitigation suggestions",
                "auth_required": True,
                "query_params": ["project_key", "risk_id"]
            }
        ]
    },
    
    "summarization": {
        "base_path": "/api/v1",
        "endpoints": [
            {
                "method": "POST",
                "path": "/summarize",
                "description": "Generate AI-powered plain-language summary",
                "auth_required": True,
                "body": "SummaryRequest"
            },
            {
                "method": "GET",
                "path": "/summarize/daily",
                "description": "Get daily summary for a project",
                "auth_required": True,
                "query_params": ["project_key", "date?", "format?"]
            },
            {
                "method": "GET",
                "path": "/summarize/weekly",
                "description": "Get weekly summary for a project",
                "auth_required": True,
                "query_params": ["project_key", "week_start?", "format?"]
            },
            {
                "method": "POST",
                "path": "/summarize/stakeholder",
                "description": "Generate executive-level stakeholder report",
                "auth_required": True,
                "query_params": ["project_key", "start_date", "end_date", "include_risks?", "include_metrics?", "format?"]
            },
            {
                "method": "GET",
                "path": "/summarize/sprint",
                "description": "Get sprint summary with AI insights",
                "auth_required": True,
                "query_params": ["project_key", "sprint_id?"]
            },
            {
                "method": "GET",
                "path": "/summarize/highlights",
                "description": "Get key highlights and achievements",
                "auth_required": True,
                "query_params": ["project_key", "days?", "limit?"]
            },
            {
                "method": "POST",
                "path": "/summarize/feedback",
                "description": "Submit feedback on generated summary for RLHF",
                "auth_required": True,
                "query_params": ["summary_id"],
                "body": {"rating": "int", "feedback?": "str", "corrections?": "dict"}
            }
        ]
    },
    
    "integrations": {
        "base_path": "/api/v1",
        "endpoints": [
            # Jira
            {
                "method": "POST",
                "path": "/integrations/jira/configure",
                "description": "Configure Jira integration",
                "auth_required": True,
                "body": "JiraConfig"
            },
            {
                "method": "POST",
                "path": "/integrations/jira/sync",
                "description": "Trigger manual sync of Jira data",
                "auth_required": True,
                "query_params": ["project_key"]
            },
            {
                "method": "GET",
                "path": "/integrations/jira/status",
                "description": "Get Jira sync status",
                "auth_required": True,
                "query_params": ["project_key"]
            },
            
            # GitHub
            {
                "method": "POST",
                "path": "/integrations/github/configure",
                "description": "Configure GitHub integration",
                "auth_required": True,
                "body": "GitHubConfig"
            },
            {
                "method": "POST",
                "path": "/integrations/github/sync",
                "description": "Trigger manual sync of GitHub data",
                "auth_required": True,
                "query_params": ["repo_name"]
            },
            {
                "method": "GET",
                "path": "/integrations/github/status",
                "description": "Get GitHub sync status",
                "auth_required": True,
                "query_params": ["repo_name"]
            },
            {
                "method": "POST",
                "path": "/integrations/github/webhook",
                "description": "GitHub webhook endpoint for real-time events",
                "auth_required": False,
                "body": "WebhookPayload"
            },
            
            # Slack
            {
                "method": "POST",
                "path": "/integrations/slack/configure",
                "description": "Configure Slack integration",
                "auth_required": True,
                "body": "SlackConfig"
            },
            {
                "method": "POST",
                "path": "/integrations/slack/send-message",
                "description": "Send message to Slack channel",
                "auth_required": True,
                "body": "SlackMessageRequest"
            },
            {
                "method": "POST",
                "path": "/integrations/slack/webhook",
                "description": "Slack events webhook endpoint",
                "auth_required": False,
                "body": "dict"
            },
            {
                "method": "POST",
                "path": "/integrations/slack/schedule-summary",
                "description": "Schedule automated summary delivery",
                "auth_required": True,
                "query_params": ["channel_id", "frequency", "time", "project_key"]
            },
            
            # General
            {
                "method": "GET",
                "path": "/integrations/status",
                "description": "Get status of all configured integrations",
                "auth_required": True
            },
            {
                "method": "POST",
                "path": "/integrations/refresh-all",
                "description": "Refresh data from all integrations",
                "auth_required": True,
                "query_params": ["project_key"]
            }
        ]
    }
}


def print_endpoints_summary():
    """Print a formatted summary of all endpoints"""
    print("\n=== NextGen Project AI - API Endpoints ===\n")
    
    for category, info in API_ENDPOINTS.items():
        print(f"\n{category.upper()}")
        print("=" * 50)
        for endpoint in info["endpoints"]:
            auth = "🔒" if endpoint["auth_required"] else "🔓"
            print(f"{auth} {endpoint['method']:6} {info['base_path']}{endpoint['path']}")
            print(f"   {endpoint['description']}")
            if endpoint.get("query_params"):
                print(f"   Query: {', '.join(endpoint['query_params'])}")
            if endpoint.get("body"):
                print(f"   Body: {endpoint['body']}")
            print()


if __name__ == "__main__":
    print_endpoints_summary()
