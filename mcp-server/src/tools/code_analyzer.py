"""
Code Analyzer Tool
Analyzes code quality, complexity, and patterns from GitHub repositories
"""
from typing import Dict, Any, Optional
import httpx
import base64

from .base import BaseTool, ToolParameter, ToolParameterType, ToolResult


class CodeAnalyzerTool(BaseTool):
    """Analyzes code quality and patterns from repositories"""
    
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
        """
        Execute code analysis
        
        Args:
            parameters: Tool parameters including repository and path
            
        Returns:
            ToolResult with code analysis
        """
        try:
            repository = parameters["repository"]
            path = parameters.get("path", "")
            branch = parameters.get("branch", "main")
            depth = parameters.get("analysis_depth", "standard")
            
            if not self.github_token:
                return self._mock_analysis(repository, path)
            
            # Perform real analysis
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
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Code analysis failed: {str(e)}"
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
        """Calculate code metrics"""
        
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
                    
                    # Check file type
                    ext = item["name"].split(".")[-1] if "." in item["name"] else "none"
                    metrics["file_types"][ext] = metrics["file_types"].get(ext, 0) + 1
                    
                    # Check for special files
                    if item["name"].lower() == "readme.md":
                        metrics["has_readme"] = True
                    if "test" in item["name"].lower():
                        metrics["has_tests"] = True
                    if item["name"] in [".github", ".gitlab-ci.yml", ".travis.yml"]:
                        metrics["has_ci"] = True
                    
                    # Get file size
                    if depth != "quick" and item.get("size", 0) < 100000:  # < 100KB
                        try:
                            file_response = await client.get(
                                item["download_url"],
                                headers=headers,
                                timeout=5.0
                            )
                            if file_response.status_code == 200:
                                content = file_response.text
                                lines = content.count("\n") + 1
                                metrics["total_lines"] += lines
                        except:
                            pass  # Skip files that fail to download
        
        if metrics["total_files"] > 0:
            metrics["average_file_size"] = metrics["total_lines"] // metrics["total_files"]
        
        return metrics
    
    def _calculate_quality_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate code quality score (0-100)"""
        score = 50.0  # Base score
        
        # Has README
        if metrics["has_readme"]:
            score += 10
        
        # Has tests
        if metrics["has_tests"]:
            score += 20
        
        # Has CI/CD
        if metrics["has_ci"]:
            score += 15
        
        # File organization (not too many files in root)
        if metrics["total_files"] < 50:
            score += 5
        
        return min(100, score)
    
    def _generate_code_recommendations(self, metrics: Dict[str, Any]) -> list:
        """Generate code quality recommendations"""
        recommendations = []
        
        if not metrics["has_readme"]:
            recommendations.append({
                "category": "documentation",
                "priority": "high",
                "suggestion": "Add README.md",
                "impact": "Improves project understandability"
            })
        
        if not metrics["has_tests"]:
            recommendations.append({
                "category": "quality",
                "priority": "critical",
                "suggestion": "Add test suite",
                "impact": "Improves code reliability and maintainability"
            })
        
        if not metrics["has_ci"]:
            recommendations.append({
                "category": "automation",
                "priority": "medium",
                "suggestion": "Set up CI/CD pipeline",
                "impact": "Automates testing and deployment"
            })
        
        if metrics["total_files"] > 100:
            recommendations.append({
                "category": "organization",
                "priority": "low",
                "suggestion": "Consider organizing files into subdirectories",
                "impact": "Improves code navigation"
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
