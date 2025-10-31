"""
Code Analyzer Tool - GitHub repository analysis and quality metrics
"""
from typing import Dict, Any, Optional
import httpx
import base64

from .base import BaseTool, ToolParameter, ToolParameterType, ToolResult


class CodeAnalyzerTool(BaseTool):
    """
    Analyzes GitHub repositories for code quality and health metrics.
    Provides insights on structure, documentation, testing, and CI/CD setup.
    """
    
    name = "analyze_code"
    description = "Analyzes code quality, complexity, and patterns from GitHub repositories"
    category = "analysis"
    version = "1.0.0"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.github_token = config.get("github_token") if config else None
        self.github_api = config.get("github_api_url", "https://api.github.com")
    
    def get_parameters(self) -> Dict[str, ToolParameter]:
        return {
            "repository": ToolParameter(
                type=ToolParameterType.STRING,
                description="Repository in format 'owner/repo'",
                required=True
            ),
            "path": ToolParameter(
                type=ToolParameterType.STRING,
                description="Path within repository to analyze (default: root)",
                required=False,
                default=""
            ),
            "branch": ToolParameter(
                type=ToolParameterType.STRING,
                description="Branch to analyze (default: main)",
                required=False,
                default="main"
            ),
            "analysis_depth": ToolParameter(
                type=ToolParameterType.STRING,
                description="Depth of analysis",
                required=False,
                enum=["quick", "standard", "deep"],
                default="standard"
            )
        }
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Executes repository analysis and returns quality metrics."""
        try:
            repository = parameters["repository"]
            path = parameters.get("path", "")
            branch = parameters.get("branch", "main")
            depth = parameters.get("analysis_depth", "standard")
            
            if not self.github_token:
                return self._mock_analysis(repository, path)
            
            analysis = await self._analyze_repository(
                repository, path, branch, depth
            )
            
            return ToolResult(
                success=True,
                data=analysis,
                metadata={
                    "repository": repository,
                    "path": path,
                    "branch": branch,
                    "analysis_depth": depth
                }
            )
            
        except Exception as error:
            return ToolResult(
                success=False,
                error=f"Code analysis failed: {str(error)}"
            )
    
    async def _analyze_repository(
        self, 
        repository: str, 
        path: str, 
        branch: str,
        depth: str
    ) -> Dict[str, Any]:
        """Perform actual GitHub repository analysis"""
        
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with httpx.AsyncClient() as client:
            # Get repository info
            repo_response = await client.get(
                f"{self.github_api}/repos/{repository}",
                headers=headers
            )
            repo_response.raise_for_status()
            repo_data = repo_response.json()
            
            # Get contents
            contents_url = f"{self.github_api}/repos/{repository}/contents/{path}"
            if branch != "main":
                contents_url += f"?ref={branch}"
            
            contents_response = await client.get(contents_url, headers=headers)
            contents_response.raise_for_status()
            contents = contents_response.json()
            
            # Analyze contents
            analysis = {
                "repository_info": {
                    "name": repo_data["name"],
                    "language": repo_data.get("language"),
                    "stars": repo_data["stargazers_count"],
                    "forks": repo_data["forks_count"],
                    "open_issues": repo_data["open_issues_count"]
                },
                "code_metrics": await self._calculate_metrics(
                    client, repository, contents, headers, depth
                ),
                "quality_score": 0,
                "recommendations": []
            }
            
            # Calculate quality score
            analysis["quality_score"] = self._calculate_quality_score(
                analysis["code_metrics"]
            )
            
            # Generate recommendations
            analysis["recommendations"] = self._generate_code_recommendations(
                analysis["code_metrics"]
            )
            
            return analysis
    
    async def _calculate_metrics(
        self, 
        client: httpx.AsyncClient, 
        repository: str,
        contents: list,
        headers: dict,
        depth: str
    ) -> Dict[str, Any]:
        """Calculates code metrics from repository contents."""
        
        metrics = {
            "total_files": 0,
            "total_lines": 0,
            "file_types": {},
            "average_file_size": 0,
            "has_readme": False,
            "has_tests": False,
            "has_ci": False
        }
        
        if isinstance(contents, list):
            for item in contents:
                if item["type"] == "file":
                    metrics["total_files"] += 1
                    
                    filename = item["name"]
                    file_extension = filename.split(".")[-1] if "." in filename else "none"
                    metrics["file_types"][file_extension] = metrics["file_types"].get(file_extension, 0) + 1
                    
                    filename_lower = filename.lower()
                    if filename_lower == "readme.md":
                        metrics["has_readme"] = True
                    if "test" in filename_lower:
                        metrics["has_tests"] = True
                    if filename in [".github", ".gitlab-ci.yml", ".travis.yml"]:
                        metrics["has_ci"] = True
                    
                    # Count lines for standard and deep analysis
                    if depth != "quick" and item.get("size", 0) < 100000:
                        try:
                            file_response = await client.get(
                                item["download_url"],
                                headers=headers,
                                timeout=5.0
                            )
                            if file_response.status_code == 200:
                                file_content = file_response.text
                                line_count = file_content.count("\n") + 1
                                metrics["total_lines"] += line_count
                        except:
                            pass
        
        if metrics["total_files"] > 0:
            metrics["average_file_size"] = metrics["total_lines"] // metrics["total_files"]
        
        return metrics
    
    def _calculate_quality_score(self, metrics: Dict[str, Any]) -> float:
        """Calculates quality score based on best practices and project health."""
        score = 50.0
        
        if metrics["has_readme"]:
            score += 10
        if metrics["has_tests"]:
            score += 20
        if metrics["has_ci"]:
            score += 15
        if metrics["total_files"] < 50:
            score += 5
        
        return min(100, score)
    
    def _generate_code_recommendations(self, metrics: Dict[str, Any]) -> list:
        """Generates improvement suggestions based on analysis metrics."""
        recommendations = []
        
        if not metrics["has_readme"]:
            recommendations.append({
                "category": "documentation",
                "priority": "high",
                "suggestion": "Add README.md with project overview and setup instructions",
                "impact": "Improves project understandability and onboarding"
            })
        
        if not metrics["has_tests"]:
            recommendations.append({
                "category": "quality",
                "priority": "critical",
                "suggestion": "Implement test suite with unit and integration tests",
                "impact": "Improves code reliability and maintainability"
            })
        
        if not metrics["has_ci"]:
            recommendations.append({
                "category": "automation",
                "priority": "medium",
                "suggestion": "Configure CI/CD pipeline (GitHub Actions, GitLab CI, etc.)",
                "impact": "Automates testing and deployment process"
            })
        
        if metrics["total_files"] > 100:
            recommendations.append({
                "category": "organization",
                "priority": "low",
                "suggestion": "Reorganize codebase into logical subdirectories",
                "impact": "Improves code navigation and maintenance"
            })
        
        return recommendations
    
    def _mock_analysis(self, repository: str, path: str) -> ToolResult:
        """Return mock data when GitHub is not configured"""
        mock_data = {
            "repository_info": {
                "name": repository.split("/")[-1],
                "language": "Python",
                "stars": 42,
                "forks": 15,
                "open_issues": 8
            },
            "code_metrics": {
                "total_files": 45,
                "total_lines": 5234,
                "file_types": {
                    "py": 30,
                    "js": 10,
                    "md": 3,
                    "json": 2
                },
                "average_file_size": 116,
                "has_readme": True,
                "has_tests": True,
                "has_ci": False
            },
            "quality_score": 75,
            "recommendations": [
                {
                    "category": "automation",
                    "priority": "medium",
                    "suggestion": "Set up CI/CD pipeline",
                    "impact": "Automates testing and deployment"
                }
            ],
            "note": "Mock data - GitHub not configured"
        }
        
        return ToolResult(
            success=True,
            data=mock_data,
            metadata={
                "repository": repository,
                "path": path,
                "mock": True
            }
        )
