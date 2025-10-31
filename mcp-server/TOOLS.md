# MCP Tools Documentation

This document describes all available tools in the MCP Server for project management, code analysis, and integrations.

## Available Tools

### 1. Project Analyzer (`analyze_project`)

Analyzes project health, velocity, and key metrics from Jira.

**Category:** Analysis  
**Version:** 1.0.0

**Parameters:**
- `project_key` (string, required): Jira project key (e.g., "PROJ", "TEAM")
- `analysis_type` (string, optional): Type of analysis
  - `comprehensive` - Full project analysis (default)
  - `velocity` - Sprint velocity analysis
  - `health` - Project health score
  - `risks` - Risk identification
- `time_period_days` (integer, optional): Days to analyze (default: 30)

**Returns:**
```json
{
  "summary": {
    "total_issues": 45,
    "completed": 30,
    "in_progress": 10,
    "blocked": 5,
    "completion_rate": 66.67,
    "velocity_per_week": 7.5
  },
  "breakdown": {
    "by_status": { "Done": 30, "In Progress": 10, "Blocked": 5 },
    "by_priority": { "High": 15, "Medium": 20, "Low": 10 },
    "by_type": { "Story": 25, "Bug": 15, "Task": 5 }
  },
  "health_score": 75.5
}
```

**Example Usage:**
```python
result = await tool_registry.execute_tool("analyze_project", {
    "project_key": "NEXTGEN",
    "analysis_type": "comprehensive",
    "time_period_days": 30
})
```

---

### 2. Risk Predictor (`predict_risk`)

Predicts project risks using ML models and historical data patterns.

**Category:** Prediction  
**Version:** 1.0.0

**Parameters:**
- `project_key` (string, required): Project identifier
- `component_name` (string, optional): Specific component/module to analyze
- `prediction_horizon_days` (integer, optional): Days ahead to predict (default: 30)
- `include_recommendations` (boolean, optional): Include mitigation recommendations (default: true)

**Returns:**
```json
{
  "overall_risk_score": 65.5,
  "risk_level": "medium",
  "risk_breakdown": {
    "schedule_risk": {
      "score": 70,
      "level": "high",
      "factors": ["Declining velocity", "High blocker count"]
    },
    "quality_risk": {
      "score": 55,
      "level": "medium",
      "factors": ["Below target test coverage"]
    },
    "resource_risk": {
      "score": 40,
      "level": "medium",
      "factors": ["High team capacity utilization"]
    }
  },
  "predicted_issues": {
    "likely_delays_days": 5,
    "potential_quality_defects": 8,
    "resource_shortfall_percentage": 15
  },
  "recommendations": [
    {
      "category": "schedule",
      "priority": "high",
      "action": "Address blockers immediately",
      "details": "Focus on removing the top blocking issues"
    }
  ],
  "confidence": 0.75
}
```

**Example Usage:**
```python
result = await tool_registry.execute_tool("predict_risk", {
    "project_key": "NEXTGEN",
    "prediction_horizon_days": 30,
    "include_recommendations": True
})
```

---

### 3. Code Analyzer (`analyze_code`)

Analyzes code quality, complexity, and patterns from GitHub repositories.

**Category:** Analysis  
**Version:** 1.0.0

**Parameters:**
- `repository` (string, required): Repository in format "owner/repo"
- `path` (string, optional): Path within repository (default: root)
- `branch` (string, optional): Branch to analyze (default: "main")
- `analysis_depth` (string, optional): Analysis depth
  - `quick` - Basic file structure only
  - `standard` - File structure + metrics (default)
  - `deep` - Full analysis with code complexity

**Returns:**
```json
{
  "repository_info": {
    "name": "NextGen-Project-AI",
    "language": "Python",
    "stars": 42,
    "forks": 15,
    "open_issues": 8
  },
  "code_metrics": {
    "total_files": 45,
    "total_lines": 5234,
    "file_types": { "py": 30, "js": 10, "md": 3, "json": 2 },
    "average_file_size": 116,
    "has_readme": true,
    "has_tests": true,
    "has_ci": false
  },
  "quality_score": 75,
  "recommendations": [
    {
      "category": "automation",
      "priority": "medium",
      "suggestion": "Set up CI/CD pipeline",
      "impact": "Automates testing and deployment"
    }
  ]
}
```

**Example Usage:**
```python
result = await tool_registry.execute_tool("analyze_code", {
    "repository": "priti200/NextGen-Project-AI",
    "branch": "main",
    "analysis_depth": "standard"
})
```

---

### 4. Jira Integration (`jira_integration`)

Integrates with Jira for issue management and project tracking.

**Category:** Integration  
**Version:** 1.0.0

**Parameters:**
- `action` (string, required): Action to perform
  - `create_issue` - Create new issue
  - `update_issue` - Update existing issue
  - `search_issues` - Search using JQL
  - `get_issue` - Get issue details
  - `add_comment` - Add comment to issue
  - `transition_issue` - Change issue status
  - `get_sprints` - List project sprints
- Additional parameters based on action (see examples below)

**Actions:**

#### Create Issue
```python
result = await tool_registry.execute_tool("jira_integration", {
    "action": "create_issue",
    "project_key": "NEXTGEN",
    "issue_type": "Story",
    "summary": "Implement user authentication",
    "description": "Add OAuth 2.0 authentication flow",
    "priority": "High",
    "assignee": "user@example.com"
})
```

#### Search Issues
```python
result = await tool_registry.execute_tool("jira_integration", {
    "action": "search_issues",
    "project_key": "NEXTGEN",
    "jql": "status = 'In Progress' AND assignee = currentUser()"
})
```

#### Transition Issue
```python
result = await tool_registry.execute_tool("jira_integration", {
    "action": "transition_issue",
    "issue_key": "NEXTGEN-123",
    "status": "Done"
})
```

---

### 5. GitHub Integration (`github_integration`)

Integrates with GitHub for repository management and code operations.

**Category:** Integration  
**Version:** 1.0.0

**Parameters:**
- `action` (string, required): Action to perform
  - `list_repos` - List repositories
  - `get_repo` - Get repository details
  - `create_issue` - Create GitHub issue
  - `list_issues` - List issues
  - `get_issue` - Get issue details
  - `create_pr` - Create pull request
  - `list_prs` - List pull requests
  - `get_pr` - Get PR details
  - `list_commits` - List commits
  - `get_file` - Get file contents
- Additional parameters based on action

**Actions:**

#### List Repositories
```python
result = await tool_registry.execute_tool("github_integration", {
    "action": "list_repos",
    "owner": "priti200"
})
```

#### Create Issue
```python
result = await tool_registry.execute_tool("github_integration", {
    "action": "create_issue",
    "owner": "priti200",
    "repo": "NextGen-Project-AI",
    "title": "Add documentation for MCP tools",
    "body": "Need comprehensive tool documentation"
})
```

#### Create Pull Request
```python
result = await tool_registry.execute_tool("github_integration", {
    "action": "create_pr",
    "owner": "priti200",
    "repo": "NextGen-Project-AI",
    "title": "Feature: MCP Tools Implementation",
    "body": "Implements all MCP tools including project analyzer and risk predictor",
    "head_branch": "feature/mcp-tools",
    "base_branch": "main"
})
```

#### Get File Contents
```python
result = await tool_registry.execute_tool("github_integration", {
    "action": "get_file",
    "owner": "priti200",
    "repo": "NextGen-Project-AI",
    "file_path": "backend/main.py",
    "branch": "main"
})
```

---

## Configuration

All tools require proper configuration in `.env`:

```bash
# Jira Configuration
JIRA_API_URL=https://your-domain.atlassian.net
JIRA_API_TOKEN=your_jira_api_token
JIRA_EMAIL=your_email@example.com

# GitHub Configuration
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_API_URL=https://api.github.com

# ML Service (for risk prediction)
ML_SERVICE_URL=http://localhost:8000
```

## Mock Mode

When integration credentials are not configured, tools return mock data for testing:
- All tools work without configuration
- Returns realistic sample data
- Marked with `"mock": true` in metadata
- Perfect for development and testing

## Error Handling

All tools return standardized `ToolResult` objects:

```python
class ToolResult:
    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[str]
    metadata: Optional[Dict[str, Any]]
```

**Success Response:**
```json
{
  "success": true,
  "data": { ... },
  "metadata": {
    "action": "analyze_project",
    "executed_at": "2025-10-31T12:00:00Z"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Project analysis failed: Connection timeout",
  "data": null
}
```

## Usage in MCP Server

Tools are automatically registered and available through the MCP protocol:

### List Available Tools
```bash
curl http://localhost:8080/mcp/tools/list
```

### Call a Tool
```bash
curl -X POST http://localhost:8080/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-123",
    "name": "analyze_project",
    "parameters": {
      "project_key": "NEXTGEN",
      "analysis_type": "comprehensive"
    }
  }'
```

## Tool Development

To add a new tool:

1. Create a new file in `src/tools/` (e.g., `my_tool.py`)
2. Extend `BaseTool` class
3. Implement required methods:
   - `get_parameters()` - Define tool parameters
   - `execute()` - Implement tool logic
4. Register in `src/tools/factory.py`

**Example:**
```python
from .base import BaseTool, ToolParameter, ToolParameterType, ToolResult

class MyCustomTool(BaseTool):
    name = "my_custom_tool"
    description = "Does something amazing"
    category = "custom"
    version = "1.0.0"
    
    def get_parameters(self) -> Dict[str, ToolParameter]:
        return {
            "input": ToolParameter(
                type=ToolParameterType.STRING,
                description="Input data",
                required=True
            )
        }
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        try:
            result = do_something(parameters["input"])
            return ToolResult(success=True, data=result)
        except Exception as e:
            return ToolResult(success=False, error=str(e))
```

## Integration with LLM Models

Tools can be used with LLM models for agentic workflows:

```python
# LLM can call tools during completion
response = await model.generate(
    messages=[{"role": "user", "content": "Analyze project NEXTGEN"}],
    tools=[tool_registry.get_tool_definition("analyze_project")]
)

# If LLM wants to use a tool
if response.tool_calls:
    for tool_call in response.tool_calls:
        result = await tool_registry.execute_tool(
            tool_call.name,
            tool_call.parameters
        )
```

## Best Practices

1. **Always validate parameters** - Use Pydantic models for validation
2. **Handle errors gracefully** - Return ToolResult with error messages
3. **Provide mock data** - Enable testing without external dependencies
4. **Log operations** - Use structured logging for debugging
5. **Document thoroughly** - Clear descriptions and examples
6. **Version your tools** - Use semantic versioning
7. **Test extensively** - Unit tests for all tool operations

## Support

For issues or questions:
- Check logs: `logs/mcp-server.log`
- Enable debug logging: `LOG_LEVEL=DEBUG`
- Review tool source code in `src/tools/`
