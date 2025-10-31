"""
Jira Integration Tool
Integrates with Jira for issue management and project tracking
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import httpx

from .base import BaseTool, ToolParameter, ToolParameterType, ToolResult


class JiraIntegrationTool(BaseTool):
    """Integrates with Jira API for issue management"""
    
    name = "jira_integration"
    description = "Interact with Jira - create issues, update status, search, and manage sprints"
    category = "integration"
    version = "1.0.0"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.jira_url = config.get("jira_api_url") if config else None
        self.jira_token = config.get("jira_api_token") if config else None
        self.jira_email = config.get("jira_email") if config else None
    
    def get_parameters(self) -> Dict[str, ToolParameter]:
        return {
            "action": ToolParameter(
                type=ToolParameterType.STRING,
                description="Action to perform",
                required=True,
                enum=[
                    "create_issue",
                    "update_issue",
                    "search_issues",
                    "get_issue",
                    "add_comment",
                    "transition_issue",
                    "get_sprints"
                ]
            ),
            "project_key": ToolParameter(
                type=ToolParameterType.STRING,
                description="Jira project key",
                required=False
            ),
            "issue_key": ToolParameter(
                type=ToolParameterType.STRING,
                description="Issue key (e.g., PROJ-123)",
                required=False
            ),
            "issue_type": ToolParameter(
                type=ToolParameterType.STRING,
                description="Issue type (Story, Bug, Task, etc.)",
                required=False
            ),
            "summary": ToolParameter(
                type=ToolParameterType.STRING,
                description="Issue summary/title",
                required=False
            ),
            "description": ToolParameter(
                type=ToolParameterType.STRING,
                description="Issue description",
                required=False
            ),
            "jql": ToolParameter(
                type=ToolParameterType.STRING,
                description="JQL query for searching issues",
                required=False
            ),
            "status": ToolParameter(
                type=ToolParameterType.STRING,
                description="Issue status to transition to",
                required=False
            ),
            "assignee": ToolParameter(
                type=ToolParameterType.STRING,
                description="Assignee email or account ID",
                required=False
            ),
            "priority": ToolParameter(
                type=ToolParameterType.STRING,
                description="Issue priority (High, Medium, Low)",
                required=False
            )
        }
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """
        Execute Jira integration action
        
        Args:
            parameters: Tool parameters including action and relevant fields
            
        Returns:
            ToolResult with action results
        """
        try:
            action = parameters["action"]
            
            if not self.jira_url or not self.jira_token:
                return self._mock_response(action, parameters)
            
            # Route to appropriate action
            if action == "create_issue":
                result = await self._create_issue(parameters)
            elif action == "update_issue":
                result = await self._update_issue(parameters)
            elif action == "search_issues":
                result = await self._search_issues(parameters)
            elif action == "get_issue":
                result = await self._get_issue(parameters)
            elif action == "add_comment":
                result = await self._add_comment(parameters)
            elif action == "transition_issue":
                result = await self._transition_issue(parameters)
            elif action == "get_sprints":
                result = await self._get_sprints(parameters)
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown action: {action}"
                )
            
            return ToolResult(
                success=True,
                data=result,
                metadata={
                    "action": action,
                    "executed_at": datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Jira integration failed: {str(e)}"
            )
    
    async def _create_issue(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Jira issue"""
        issue_data = {
            "fields": {
                "project": {"key": params["project_key"]},
                "summary": params["summary"],
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": params.get("description", "")
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {"name": params.get("issue_type", "Task")}
            }
        }
        
        if params.get("assignee"):
            issue_data["fields"]["assignee"] = {"emailAddress": params["assignee"]}
        
        if params.get("priority"):
            issue_data["fields"]["priority"] = {"name": params["priority"]}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.jira_url}/rest/api/3/issue",
                json=issue_data,
                auth=(self.jira_email, self.jira_token)
            )
            response.raise_for_status()
            return response.json()
    
    async def _update_issue(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing Jira issue"""
        issue_key = params["issue_key"]
        update_data = {"fields": {}}
        
        if params.get("summary"):
            update_data["fields"]["summary"] = params["summary"]
        
        if params.get("description"):
            update_data["fields"]["description"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": params["description"]}]
                    }
                ]
            }
        
        if params.get("assignee"):
            update_data["fields"]["assignee"] = {"emailAddress": params["assignee"]}
        
        if params.get("priority"):
            update_data["fields"]["priority"] = {"name": params["priority"]}
        
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.jira_url}/rest/api/3/issue/{issue_key}",
                json=update_data,
                auth=(self.jira_email, self.jira_token)
            )
            response.raise_for_status()
            return {"success": True, "issue_key": issue_key, "updated": True}
    
    async def _search_issues(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for Jira issues using JQL"""
        jql = params.get("jql", f"project = {params.get('project_key', '')}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.jira_url}/rest/api/3/search",
                params={
                    "jql": jql,
                    "maxResults": 50,
                    "fields": "summary,status,assignee,priority,created,updated"
                },
                auth=(self.jira_email, self.jira_token)
            )
            response.raise_for_status()
            return response.json()
    
    async def _get_issue(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get details of a specific issue"""
        issue_key = params["issue_key"]
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.jira_url}/rest/api/3/issue/{issue_key}",
                auth=(self.jira_email, self.jira_token)
            )
            response.raise_for_status()
            return response.json()
    
    async def _add_comment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a comment to an issue"""
        issue_key = params["issue_key"]
        comment_text = params.get("description", params.get("summary", ""))
        
        comment_data = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": comment_text}]
                    }
                ]
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.jira_url}/rest/api/3/issue/{issue_key}/comment",
                json=comment_data,
                auth=(self.jira_email, self.jira_token)
            )
            response.raise_for_status()
            return response.json()
    
    async def _transition_issue(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Transition an issue to a new status"""
        issue_key = params["issue_key"]
        target_status = params["status"]
        
        # Get available transitions
        async with httpx.AsyncClient() as client:
            transitions_response = await client.get(
                f"{self.jira_url}/rest/api/3/issue/{issue_key}/transitions",
                auth=(self.jira_email, self.jira_token)
            )
            transitions_response.raise_for_status()
            transitions = transitions_response.json()["transitions"]
            
            # Find matching transition
            transition_id = None
            for transition in transitions:
                if transition["to"]["name"].lower() == target_status.lower():
                    transition_id = transition["id"]
                    break
            
            if not transition_id:
                return {
                    "success": False,
                    "error": f"No transition found to status: {target_status}",
                    "available_transitions": [t["to"]["name"] for t in transitions]
                }
            
            # Perform transition
            transition_data = {"transition": {"id": transition_id}}
            response = await client.post(
                f"{self.jira_url}/rest/api/3/issue/{issue_key}/transitions",
                json=transition_data,
                auth=(self.jira_email, self.jira_token)
            )
            response.raise_for_status()
            return {"success": True, "issue_key": issue_key, "new_status": target_status}
    
    async def _get_sprints(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get sprints for a project/board"""
        project_key = params["project_key"]
        
        async with httpx.AsyncClient() as client:
            # First get the board ID
            boards_response = await client.get(
                f"{self.jira_url}/rest/agile/1.0/board",
                params={"projectKeyOrId": project_key},
                auth=(self.jira_email, self.jira_token)
            )
            boards_response.raise_for_status()
            boards = boards_response.json()["values"]
            
            if not boards:
                return {"sprints": [], "message": "No boards found for project"}
            
            board_id = boards[0]["id"]
            
            # Get sprints for the board
            sprints_response = await client.get(
                f"{self.jira_url}/rest/agile/1.0/board/{board_id}/sprint",
                auth=(self.jira_email, self.jira_token)
            )
            sprints_response.raise_for_status()
            return sprints_response.json()
    
    def _mock_response(self, action: str, params: Dict[str, Any]) -> ToolResult:
        """Return mock data when Jira is not configured"""
        mock_data = {
            "create_issue": {
                "id": "10001",
                "key": f"{params.get('project_key', 'PROJ')}-123",
                "self": f"https://jira.example.com/rest/api/3/issue/10001"
            },
            "search_issues": {
                "total": 5,
                "issues": [
                    {
                        "key": "PROJ-121",
                        "fields": {
                            "summary": "Implement new feature",
                            "status": {"name": "In Progress"}
                        }
                    },
                    {
                        "key": "PROJ-122",
                        "fields": {
                            "summary": "Fix bug in authentication",
                            "status": {"name": "Done"}
                        }
                    }
                ]
            },
            "get_issue": {
                "key": params.get("issue_key", "PROJ-123"),
                "fields": {
                    "summary": "Example issue",
                    "status": {"name": "In Progress"},
                    "assignee": {"displayName": "John Doe"}
                }
            }
        }
        
        return ToolResult(
            success=True,
            data=mock_data.get(action, {"message": "Mock response", "note": "Jira not configured"}),
            metadata={"action": action, "mock": True}
        )
