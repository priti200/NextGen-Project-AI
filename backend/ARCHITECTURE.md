# NextGen Project AI - Backend Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT APPLICATIONS                          │
│              (Frontend, Mobile, CLI, External Systems)               │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               │ HTTP/HTTPS + JWT
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                         API GATEWAY (FastAPI)                        │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  Middleware Layer                                              │ │
│  │  • CORS • Auth • Rate Limiting • Request Timing • Logging    │ │
│  └────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   ROUTES      │   │   ROUTES      │   │   ROUTES      │
│               │   │               │   │               │
│ • Health      │   │ • Dashboard   │   │ • Risks       │
│               │   │ • Resources   │   │ • Summarize   │
│               │   │               │   │ • Integrations│
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
               ┌────────────────────────┐
               │   PYDANTIC SCHEMAS     │
               │ Request/Response Models│
               └────────────┬───────────┘
                            │
                            ▼
               ┌────────────────────────┐
               │   SERVICE LAYER        │
               │ Business Logic         │
               │                        │
               │ • DashboardService     │
               │ • ResourceService      │
               │ • RiskService          │
               │ • SummarizationService │
               │ • IntegrationService   │
               └────────────┬───────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  DATABASE    │  │  REDIS       │  │  ML SERVICE  │
│              │  │              │  │              │
│ • Issues     │  │ • Cache      │  │ • Risk Model │
│ • PRs        │  │ • Sessions   │  │ • LLM        │
│ • Users      │  │ • Rate Limit │  │ • RLHF       │
│ • History    │  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘

        ▲                                   ▲
        │                                   │
        └───────────────┬───────────────────┘
                        │
            ┌───────────┴───────────┐
            │                       │
            ▼                       ▼
    ┌──────────────┐       ┌──────────────┐
    │ INTEGRATIONS │       │  WEBHOOKS    │
    │              │       │              │
    │ • Jira API   │       │ • GitHub     │
    │ • GitHub API │       │ • Slack      │
    │ • Slack API  │       │              │
    └──────────────┘       └──────────────┘
```

## Data Flow Examples

### 1. Dashboard Request Flow
```
Client Request
    ↓
JWT Auth Middleware → Verify Token
    ↓
Dashboard Router → /api/v1/dashboard
    ↓
Validate Query Params (Pydantic)
    ↓
DashboardService.get_dashboard()
    ↓
Fetch Data: Database + Cache
    ↓
Aggregate & Transform
    ↓
Return DashboardResponse (Pydantic)
    ↓
JSON Response to Client
```

### 2. Risk Prediction Flow
```
Client POST /api/v1/predict-risk
    ↓
JWT Auth Middleware
    ↓
Risk Router → Validate RiskRequest
    ↓
RiskService.predict_risk()
    ↓
Fetch Historical Data (Database)
    ↓
Call ML Service API → Risk Model
    ↓
Calculate Risk Factors & Explainability
    ↓
Return RiskPrediction Response
    ↓
Client receives prediction + factors
```

### 3. Summarization with RLHF Flow
```
Client POST /api/v1/summarize
    ↓
JWT Auth Middleware
    ↓
Summarization Router → Validate Request
    ↓
SummarizationService.generate_summary()
    ↓
Gather Data (Jira, GitHub, Database)
    ↓
Call ML Service → LLM Endpoint
    ↓
Generate Natural Language Summary
    ↓
Store Summary with ID
    ↓
Return SummaryResponse
    ↓
User Reviews Summary
    ↓
POST /api/v1/summarize/feedback
    ↓
Store Feedback for RLHF Training
```

### 4. Integration Sync Flow
```
POST /api/v1/integrations/jira/sync
    ↓
JWT Auth Middleware
    ↓
Integration Router → BackgroundTask
    ↓
IntegrationService.sync_jira()
    ↓
Call Jira API → Fetch Issues/Sprints
    ↓
Transform Data → Normalize Events
    ↓
Store in Database
    ↓
Update Sync Status
    ↓
Return "sync_started" Response
```

### 5. Real-time Webhook Flow
```
GitHub Event (PR opened)
    ↓
POST /api/v1/integrations/github/webhook
    ↓
Validate Webhook Signature
    ↓
BackgroundTask → Process Event
    ↓
IntegrationService.process_github_webhook()
    ↓
Parse Event Payload
    ↓
Update Database (Real-time)
    ↓
Trigger Risk Recalculation (if needed)
    ↓
Send Slack Notification (if configured)
```

## Key Design Patterns

### 1. **Layered Architecture**
- Routes (API Layer)
- Schemas (Validation Layer)
- Services (Business Logic Layer)
- External Services (Integration Layer)

### 2. **Dependency Injection**
- FastAPI's `Depends()` for auth, db sessions
- Service instances created per request

### 3. **Async/Await**
- All endpoints are async-ready
- Background tasks for long-running operations

### 4. **Type Safety**
- Pydantic models for all requests/responses
- Type hints throughout codebase

### 5. **Separation of Concerns**
- Each route file handles one domain
- Services contain business logic
- Schemas define data contracts

## Security Layers

```
Request → CORS Check → JWT Verification → Rate Limiting → Route Handler
                ↓              ↓              ↓
             Block         Block          Block
           Invalid       Invalid       Excessive
           Origins       Token         Requests
```

## Integration Architecture

```
┌─────────────────────────────────────────────────┐
│           Integration Service                    │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌────────────┐  ┌────────────┐  ┌───────────┐│
│  │ Jira       │  │ GitHub     │  │ Slack     ││
│  │ Client     │  │ Client     │  │ Client    ││
│  └─────┬──────┘  └─────┬──────┘  └─────┬─────┘│
│        │               │               │       │
│        ▼               ▼               ▼       │
│  ┌──────────────────────────────────────────┐ │
│  │      Unified Event Store                 │ │
│  │  • Normalized event schema               │ │
│  │  • Source tracking                       │ │
│  │  • Timestamp indexing                    │ │
│  └──────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

## Error Handling Strategy

```
Exception Occurs
    ↓
Specific Exception Handler? → Yes → Custom Error Response
    ↓ No
Global Exception Handler
    ↓
Log Error (with context)
    ↓
Return Generic 500 Response
    ↓
(Production: Send to Sentry)
```

## Performance Considerations

1. **Caching Strategy**
   - Dashboard data: 5 min TTL
   - User permissions: 15 min TTL
   - Risk predictions: 1 hour TTL

2. **Database Optimization**
   - Indexes on frequently queried fields
   - Connection pooling
   - Query optimization

3. **Background Processing**
   - Heavy computations in background tasks
   - Celery for scheduled jobs
   - Rate limiting on external APIs

4. **Response Optimization**
   - Pagination for list endpoints
   - Field selection/filtering
   - Gzip compression

## Monitoring Points

```
┌────────────────────────────────────┐
│  Metrics to Track                  │
├────────────────────────────────────┤
│ • Request latency (p50, p95, p99) │
│ • Error rates by endpoint          │
│ • Auth failures                    │
│ • External API call duration       │
│ • Database query time              │
│ • Cache hit rate                   │
│ • Background task queue length     │
│ • ML model prediction latency      │
└────────────────────────────────────┘
```
