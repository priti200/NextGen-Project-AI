# NextGen Project AI - Backend

FastAPI-based backend for the AI-powered project management assistant.

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── core/                  # Core configurations
│   ├── __init__.py
│   ├── config.py         # Application settings
│   ├── auth.py           # Authentication logic
│   └── logging_config.py # Logging setup
├── routes/               # API endpoint definitions
│   ├── __init__.py
│   ├── health.py        # Health check endpoints
│   ├── dashboard.py     # Dashboard endpoints
│   ├── resources.py     # Resource allocation endpoints
│   ├── risks.py         # Risk prediction endpoints
│   ├── summarization.py # Summarization endpoints
│   └── integrations.py  # Integration management endpoints
├── schemas/             # Pydantic models for request/response
│   ├── dashboard.py
│   ├── resources.py
│   ├── risks.py
│   ├── summarization.py
│   └── integrations.py
└── services/            # Business logic layer
    ├── dashboard_service.py
    ├── resource_service.py
    ├── risk_service.py
    ├── summarization_service.py
    └── integration_service.py
```

## API Endpoints

### Health
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/detailed` - Detailed health with system metrics

### Dashboard
- `GET /api/v1/dashboard` - Get aggregated project dashboard
- `GET /api/v1/dashboard/metrics` - Get detailed project metrics
- `GET /api/v1/dashboard/velocity` - Get sprint velocity trends
- `GET /api/v1/dashboard/burndown` - Get burndown chart data
- `GET /api/v1/dashboard/github-activity` - Get GitHub activity summary
- `GET /api/v1/dashboard/ci-status` - Get CI/CD pipeline status

### Resources
- `GET /api/v1/resource-map` - Get current resource allocation map
- `GET /api/v1/resource-map/member/{email}` - Get team member details
- `GET /api/v1/resource-map/workload` - Get workload distribution
- `GET /api/v1/resource-map/capacity` - Get capacity planning info
- `POST /api/v1/resource-map/suggestions` - Get reallocation suggestions
- `GET /api/v1/resource-map/availability` - Get team availability calendar

### Risks
- `POST /api/v1/predict-risk` - Predict risks and delays
- `GET /api/v1/risks/component/{component_name}` - Get component risk
- `GET /api/v1/risks/project` - Get all project risks
- `GET /api/v1/risks/sprint` - Get sprint risk assessment
- `GET /api/v1/risks/delay-estimate` - Estimate delay
- `GET /api/v1/risks/factors` - Get risk factors breakdown
- `POST /api/v1/risks/mitigation` - Get mitigation suggestions

### Summarization
- `POST /api/v1/summarize` - Generate AI-powered summary
- `GET /api/v1/summarize/daily` - Get daily summary
- `GET /api/v1/summarize/weekly` - Get weekly summary
- `POST /api/v1/summarize/stakeholder` - Generate stakeholder report
- `GET /api/v1/summarize/sprint` - Get sprint summary
- `GET /api/v1/summarize/highlights` - Get key highlights
- `POST /api/v1/summarize/feedback` - Submit feedback for RLHF

### Integrations
- `POST /api/v1/integrations/jira/configure` - Configure Jira
- `POST /api/v1/integrations/jira/sync` - Sync Jira data
- `GET /api/v1/integrations/jira/status` - Get Jira sync status
- `POST /api/v1/integrations/github/configure` - Configure GitHub
- `POST /api/v1/integrations/github/sync` - Sync GitHub data
- `GET /api/v1/integrations/github/status` - Get GitHub sync status
- `POST /api/v1/integrations/github/webhook` - GitHub webhook receiver
- `POST /api/v1/integrations/slack/configure` - Configure Slack
- `POST /api/v1/integrations/slack/send-message` - Send Slack message
- `POST /api/v1/integrations/slack/webhook` - Slack events receiver
- `POST /api/v1/integrations/slack/schedule-summary` - Schedule automated summaries
- `GET /api/v1/integrations/status` - Get all integrations status
- `POST /api/v1/integrations/refresh-all` - Refresh all integrations

## Quick Start

### 1. Install Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

### 2. Setup Environment

```powershell
# Copy example env file
cp .env.example .env

# Edit .env and add your API tokens and configuration
```

### 3. Run Development Server

```powershell
python main.py
```

Or with uvicorn directly:

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access API Documentation

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- OpenAPI JSON: http://localhost:8000/api/openapi.json

## Development

### Running Tests

```powershell
pytest tests/ -v --cov=.
```

### Code Formatting

```powershell
black .
```

### Type Checking

```powershell
mypy .
```

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Next Steps

1. Implement service layer logic (currently stubs)
2. Set up database models and migrations
3. Integrate with ML service for risk prediction and summarization
4. Add comprehensive tests
5. Set up CI/CD pipeline
6. Add rate limiting and security hardening

## Notes

- All service implementations are currently stubs marked with `TODO`
- Integration with ML service required for risk prediction and summarization
- Database setup needed for data persistence
- RLHF feedback collection implemented but training pipeline needs setup
