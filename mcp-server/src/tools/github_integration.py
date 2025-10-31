"""
GitHub Integration Tool
Integrates with GitHub for repository management and code operations
"""
from typing import Dict, Any, Optional
from datetime import datetime
import httpx

from .base import BaseTool, ToolParameter, ToolParameterType, ToolResult


class GitHubIntegrationTool(BaseTool):
    """Integrates with GitHub API for repository operations"""
    
    name = "github_integration"
    description = "Interact with GitHub - manage repos, PRs, issues, and code"
    category = "integration"
    version = "1.0.0"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.github_token = config.get("github_token") if config else None
        self.github_api = config.get("github_api_url", "https://api.github.com")
    
    def get_parameters(self) -> Dict[str, ToolParameter]:
        return {
            "action": ToolParameter(
                type=ToolParameterType.STRING,
                description="Action to perform",
                required=True,
                enum=[
                    "list_repos",
                    "get_repo",
                    "create_issue",
                    "list_issues",
                    "get_issue",
                    "create_pr",
                    "list_prs",
                    "get_pr",
                    "list_commits",
                    "get_file"
                ]
            ),
            "owner": ToolParameter(
                type=ToolParameterType.STRING,
                description="Repository owner/organization",
                required=False
            ),
            "repo": ToolParameter(
                type=ToolParameterType.STRING,
                description="Repository name",
                required=False
            ),
            "title": ToolParameter(
                type=ToolParameterType.STRING,
                description="Title for issue/PR",
                required=False
            ),
            "body": ToolParameter(
                type=ToolParameterType.STRING,
                description="Body/description for issue/PR",
                required=False
            ),
            "issue_number": ToolParameter(
                type=ToolParameterType.INTEGER,
                description="Issue number",
                required=False
            ),
            "pr_number": ToolParameter(
                type=ToolParameterType.INTEGER,
                description="Pull request number",
                required=False
            ),
            "branch": ToolParameter(
                type=ToolParameterType.STRING,
                description="Branch name",
                required=False
            ),
            "base_branch": ToolParameter(
                type=ToolParameterType.STRING,
                description="Base branch for PR",
                required=False
            ),
            "head_branch": ToolParameter(
                type=ToolParameterType.STRING,
                description="Head branch for PR",
                required=False
            ),
            "file_path": ToolParameter(
                type=ToolParameterType.STRING,
                description="Path to file in repository",
                required=False
            ),
            "state": ToolParameter(
                type=ToolParameterType.STRING,
                description="State filter (open, closed, all)",
                required=False,
                default="open"
            )
        }
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """
        Execute GitHub integration action
        
        Args:
            parameters: Tool parameters including action and relevant fields
            
        Returns:
            ToolResult with action results
        """
        try:
            action = parameters["action"]
            
            if not self.github_token:
                return self._mock_response(action, parameters)
            
            # Route to appropriate action
            if action == "list_repos":
                result = await self._list_repos(parameters)
            elif action == "get_repo":
                result = await self._get_repo(parameters)
            elif action == "create_issue":
                result = await self._create_issue(parameters)
            elif action == "list_issues":
                result = await self._list_issues(parameters)
            elif action == "get_issue":
                result = await self._get_issue(parameters)
            elif action == "create_pr":
                result = await self._create_pr(parameters)
            elif action == "list_prs":
                result = await self._list_prs(parameters)
            elif action == "get_pr":
                result = await self._get_pr(parameters)
            elif action == "list_commits":
                result = await self._list_commits(parameters)
            elif action == "get_file":
                result = await self._get_file(parameters)
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
                error=f"GitHub integration failed: {str(e)}"
            )
    
    def _get_headers(self) -> Dict[str, str]:
        """Get GitHub API headers"""
        return {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    async def _list_repos(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List repositories"""
        owner = params.get("owner")
        
        async with httpx.AsyncClient() as client:
            if owner:
                # List repos for specific owner
                url = f"{self.github_api}/users/{owner}/repos"
            else:
                # List authenticated user's repos
                url = f"{self.github_api}/user/repos"
            
            response = await client.get(url, headers=self._get_headers())
            response.raise_for_status()
            return {"repositories": response.json()}
    
    async def _get_repo(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get repository details"""
        owner = params["owner"]
        repo = params["repo"]
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.github_api}/repos/{owner}/{repo}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def _create_issue(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new issue"""
        owner = params["owner"]
        repo = params["repo"]
        
        issue_data = {
            "title": params["title"],
            "body": params.get("body", "")
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.github_api}/repos/{owner}/{repo}/issues",
                json=issue_data,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def _list_issues(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List repository issues"""
        owner = params["owner"]
        repo = params["repo"]
        state = params.get("state", "open")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.github_api}/repos/{owner}/{repo}/issues",
                params={"state": state, "per_page": 50},
                headers=self._get_headers()
            )
            response.raise_for_status()
            return {"issues": response.json()}
    
    async def _get_issue(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get issue details"""
        owner = params["owner"]
        repo = params["repo"]
        issue_number = params["issue_number"]
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.github_api}/repos/{owner}/{repo}/issues/{issue_number}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def _create_pr(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a pull request"""
        owner = params["owner"]
        repo = params["repo"]
        
        pr_data = {
            "title": params["title"],
            "body": params.get("body", ""),
            "head": params["head_branch"],
            "base": params.get("base_branch", "main")
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.github_api}/repos/{owner}/{repo}/pulls",
                json=pr_data,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def _list_prs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List pull requests"""
        owner = params["owner"]
        repo = params["repo"]
        state = params.get("state", "open")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.github_api}/repos/{owner}/{repo}/pulls",
                params={"state": state, "per_page": 50},
                headers=self._get_headers()
            )
            response.raise_for_status()
            return {"pull_requests": response.json()}
    
    async def _get_pr(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get pull request details"""
        owner = params["owner"]
        repo = params["repo"]
        pr_number = params["pr_number"]
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.github_api}/repos/{owner}/{repo}/pulls/{pr_number}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def _list_commits(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List repository commits"""
        owner = params["owner"]
        repo = params["repo"]
        branch = params.get("branch")
        
        query_params = {"per_page": 50}
        if branch:
            query_params["sha"] = branch
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.github_api}/repos/{owner}/{repo}/commits",
                params=query_params,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return {"commits": response.json()}
    
    async def _get_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get file contents from repository"""
        owner = params["owner"]
        repo = params["repo"]
        file_path = params["file_path"]
        branch = params.get("branch", "main")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.github_api}/repos/{owner}/{repo}/contents/{file_path}",
                params={"ref": branch},
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    def _mock_response(self, action: str, params: Dict[str, Any]) -> ToolResult:
        """Return mock data when GitHub is not configured"""
        mock_data = {
            "list_repos": {
                "repositories": [
                    {
                        "name": "example-repo",
                        "full_name": "user/example-repo",
                        "private": False,
                        "html_url": "https://github.com/user/example-repo"
                    }
                ]
            },
            "get_repo": {
                "name": params.get("repo", "example-repo"),
                "full_name": f"{params.get('owner', 'user')}/{params.get('repo', 'example-repo')}",
                "private": False,
                "stargazers_count": 42,
                "forks_count": 15
            },
            "list_issues": {
                "issues": [
                    {
                        "number": 1,
                        "title": "Example issue",
                        "state": "open",
                        "html_url": "https://github.com/user/repo/issues/1"
                    }
                ]
            },
            "create_issue": {
                "number": 42,
                "title": params.get("title", "New issue"),
                "state": "open",
                "html_url": "https://github.com/user/repo/issues/42"
            }
        }
        
        return ToolResult(
            success=True,
            data=mock_data.get(action, {"message": "Mock response", "note": "GitHub not configured"}),
            metadata={"action": action, "mock": True}
        )
