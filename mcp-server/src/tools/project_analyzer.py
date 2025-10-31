"""
Project Analyzer Tool - Jira project health and velocity analysis
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import httpx

from .base import BaseTool, ToolParameter, ToolParameterType, ToolResult


class ProjectAnalyzerTool(BaseTool):
    """Analyzes Jira projects for health metrics, velocity, and potential risks"""
    
    name = "analyze_project"
    description = "Analyzes project health, velocity, and key metrics from Jira"
    category = "analysis"
    version = "1.0.0"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.jira_url = config.get("jira_api_url") if config else None
        self.jira_token = config.get("jira_api_token") if config else None
        self.jira_email = config.get("jira_email") if config else None
    
    def get_parameters(self) -> Dict[str, ToolParameter]:
        return {
            "project_key": ToolParameter(
                type=ToolParameterType.STRING,
                description="Jira project key (e.g., PROJ, TEAM)",
                required=True
            ),
            "analysis_type": ToolParameter(
                type=ToolParameterType.STRING,
                description="Type of analysis to perform",
                required=False,
                enum=["comprehensive", "velocity", "health", "risks"],
                default="comprehensive"
            ),
            "time_period_days": ToolParameter(
                type=ToolParameterType.INTEGER,
                description="Number of days to analyze (default: 30)",
                required=False,
                default=30
            )
        }
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Executes project analysis based on specified type and time period"""
        try:
            project_key = parameters["project_key"]
            analysis_type = parameters.get("analysis_type", "comprehensive")
            time_period = parameters.get("time_period_days", 30)
            
            if not self.jira_url or not self.jira_token:
                return self._mock_analysis(project_key, analysis_type, time_period)
            
            analysis_result = await self._analyze_jira_project(
                project_key, 
                analysis_type, 
                time_period
            )
            
            return ToolResult(
                success=True,
                data=analysis_result,
                metadata={
                    "project_key": project_key,
                    "analysis_type": analysis_type,
                    "time_period_days": time_period,
                    "analyzed_at": datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Project analysis failed: {str(e)}"
            )
    
    async def _analyze_jira_project(
        self, 
        project_key: str, 
        analysis_type: str, 
        time_period: int
    ) -> Dict[str, Any]:
        """Performs Jira project analysis using REST API"""
        
        async with httpx.AsyncClient() as client:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=time_period)
            
            jql = f"project = {project_key} AND updated >= -{time_period}d"
            
            response = await client.get(
                f"{self.jira_url}/rest/api/3/search",
                params={
                    "jql": jql,
                    "maxResults": 1000,
                    "fields": "status,issuetype,created,updated,resolutiondate,priority,assignee"
                },
                auth=(self.jira_email, self.jira_token)
            )
            response.raise_for_status()
            
            issues = response.json().get("issues", [])
            
            if analysis_type == "comprehensive":
                return self._comprehensive_analysis(issues, time_period)
            elif analysis_type == "velocity":
                return self._velocity_analysis(issues, time_period)
            elif analysis_type == "health":
                return self._health_analysis(issues)
            elif analysis_type == "risks":
                return self._risk_analysis(issues)
            else:
                return self._comprehensive_analysis(issues, time_period)
    
    def _comprehensive_analysis(self, issues: list, time_period: int) -> Dict[str, Any]:
        """Generates comprehensive project analysis with all metrics"""
        total_issues = len(issues)
        
        status_counts = {}
        priority_counts = {}
        type_counts = {}
        
        completed = 0
        in_progress = 0
        blocked = 0
        
        for issue in issues:
            status = issue["fields"]["status"]["name"]
            status_counts[status] = status_counts.get(status, 0) + 1
            
            if status.lower() in ["done", "closed", "resolved"]:
                completed += 1
            elif status.lower() in ["in progress", "in review"]:
                in_progress += 1
            elif status.lower() in ["blocked", "impediment"]:
                blocked += 1
            
            # Priority
            priority = issue["fields"].get("priority", {})
            if priority:
                priority_name = priority.get("name", "None")
                priority_counts[priority_name] = priority_counts.get(priority_name, 0) + 1
            
            # Type
            issue_type = issue["fields"]["issuetype"]["name"]
            type_counts[issue_type] = type_counts.get(issue_type, 0) + 1
        
        # Calculate metrics
        completion_rate = (completed / total_issues * 100) if total_issues > 0 else 0
        velocity = completed / (time_period / 7)  # Issues per week
        
        return {
            "summary": {
                "total_issues": total_issues,
                "completed": completed,
                "in_progress": in_progress,
                "blocked": blocked,
                "completion_rate": round(completion_rate, 2),
                "velocity_per_week": round(velocity, 2)
            },
            "breakdown": {
                "by_status": status_counts,
                "by_priority": priority_counts,
                "by_type": type_counts
            },
            "health_score": self._calculate_health_score(
                completion_rate, 
                blocked, 
                total_issues
            )
        }
    
    def _velocity_analysis(self, issues: list, time_period: int) -> Dict[str, Any]:
        """Analyze project velocity"""
        completed_issues = [
            issue for issue in issues
            if issue["fields"]["status"]["name"].lower() in ["done", "closed", "resolved"]
        ]
        
        weeks = time_period / 7
        velocity = len(completed_issues) / weeks if weeks > 0 else 0
        
        return {
            "completed_issues": len(completed_issues),
            "time_period_days": time_period,
            "velocity_per_week": round(velocity, 2),
            "estimated_monthly_completion": round(velocity * 4, 2)
        }
    
    def _health_analysis(self, issues: list) -> Dict[str, Any]:
        """Analyze project health"""
        total = len(issues)
        blocked = sum(1 for i in issues if i["fields"]["status"]["name"].lower() in ["blocked", "impediment"])
        overdue = 0  # Would need due date field
        high_priority = sum(1 for i in issues if i["fields"].get("priority", {}).get("name", "").lower() in ["high", "highest", "critical"])
        
        health_score = self._calculate_health_score(
            (total - blocked) / total * 100 if total > 0 else 100,
            blocked,
            total
        )
        
        return {
            "health_score": health_score,
            "total_issues": total,
            "blocked_issues": blocked,
            "high_priority_issues": high_priority,
            "status": "healthy" if health_score >= 70 else "at_risk" if health_score >= 50 else "critical"
        }
    
    def _risk_analysis(self, issues: list) -> Dict[str, Any]:
        """Analyze project risks"""
        risks = []
        
        blocked = [i for i in issues if i["fields"]["status"]["name"].lower() in ["blocked", "impediment"]]
        if len(blocked) > len(issues) * 0.1:
            risks.append({
                "type": "high_blocked_rate",
                "severity": "high",
                "description": f"{len(blocked)} issues are blocked",
                "recommendation": "Identify and remove blockers immediately"
            })
        
        high_priority = [i for i in issues if i["fields"].get("priority", {}).get("name", "").lower() in ["high", "highest"]]
        if len(high_priority) > len(issues) * 0.3:
            risks.append({
                "type": "many_high_priority",
                "severity": "medium",
                "description": f"{len(high_priority)} high-priority issues",
                "recommendation": "Review and reprioritize if needed"
            })
        
        return {
            "risk_count": len(risks),
            "risks": risks,
            "overall_risk_level": "high" if len(risks) >= 3 else "medium" if len(risks) >= 1 else "low"
        }
    
    def _calculate_health_score(self, completion_rate: float, blocked: int, total: int) -> float:
        """Calculate overall health score (0-100)"""
        score = completion_rate * 0.5  # 50% weight on completion
        
        if total > 0:
            blocked_penalty = (blocked / total) * 30  # Up to 30 points penalty
            score -= blocked_penalty
        
        return max(0, min(100, round(score, 2)))
    
    def _mock_analysis(self, project_key: str, analysis_type: str, time_period: int) -> ToolResult:
        """Return mock data when Jira is not configured"""
        mock_data = {
            "summary": {
                "total_issues": 45,
                "completed": 30,
                "in_progress": 10,
                "blocked": 5,
                "completion_rate": 66.67,
                "velocity_per_week": 7.5
            },
            "breakdown": {
                "by_status": {
                    "Done": 30,
                    "In Progress": 10,
                    "Blocked": 5
                },
                "by_priority": {
                    "High": 15,
                    "Medium": 20,
                    "Low": 10
                },
                "by_type": {
                    "Story": 25,
                    "Bug": 15,
                    "Task": 5
                }
            },
            "health_score": 75.5,
            "note": "Mock data - Jira not configured"
        }
        
        return ToolResult(
            success=True,
            data=mock_data,
            metadata={
                "project_key": project_key,
                "analysis_type": analysis_type,
                "mock": True
            }
        )
