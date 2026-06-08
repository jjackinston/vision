# SellerVision AI — API Specification v1

Base URL: `https://api.sellervisionai.com/api/v1`
Auth: `Authorization: Bearer <clerk_jwt>` or `X-API-Key: sv_<key>`

---

## Authentication

### POST /auth/token
Exchange Clerk session for API token.
```json
Request: { "clerk_session_token": "string" }
Response: { "access_token": "string", "expires_in": 3600 }
```

### POST /auth/api-keys
Create an API key.
```json
Request: { "name": "My Integration", "scopes": ["products:read", "keywords:read"] }
Response: { "key": "sv_...", "prefix": "sv_abc123", "id": "uuid" }
```

---

## Products

### GET /products
List tracked products.
**Query:** `page`, `per_page`, `marketplace`, `is_tracked`, `min_opportunity`, `sort_by`
```json
Response: {
  "items": [{ "id": "uuid", "title": "...", "asin": "...", "opportunity_score": 84.2, ... }],
  "total": 156, "page": 1, "per_page": 20
}
```

### POST /products/search
Search & analyze products.
```json
Request: {
  "query": "yoga mat",
  "marketplace": "amazon",
  "category": "Sports",
  "min_price": 10, "max_price": 100,
  "min_monthly_revenue": 5000
}
Response: [{ "asin": "...", "title": "...", "estimated_monthly_revenue": 45000, ... }]
```

### POST /products/predict-success
Predict product launch success.
```json
Request: {
  "concept": "Bamboo travel coffee mug with built-in strainer",
  "category": "Kitchen",
  "cost": 4.50,
  "selling_price": 28.99,
  "marketplace": "amazon"
}
Response: {
  "success_probability": 78,
  "estimated_revenue_monthly": 12400,
  "estimated_profit_monthly": 3200,
  "break_even_months": 3,
  "risk_factors": ["High competition in coffee category"],
  "recommendation": "launch",
  "explainable_reasoning": "..."
}
```

### POST /products/launch-simulator
```json
Request: {
  "product_cost": 5.00,
  "inventory_quantity": 500,
  "ppc_budget_daily": 50,
  "selling_price": 29.99,
  "marketplace": "amazon",
  "target_bsr": 5000
}
Response: {
  "scenarios": {
    "conservative": { "month_1_revenue": 2400, "roi_percent": 180, ... },
    "realistic": { "month_1_revenue": 4800, "roi_percent": 340, ... },
    "optimistic": { "month_1_revenue": 8200, "roi_percent": 580, ... }
  },
  "recommended_scenario": "realistic",
  "cash_flow_chart": [...]
}
```

---

## Keywords

### GET /keywords/research
```
Query: q=yoga+mat&marketplace=amazon&include_related=true
Response: {
  "keyword": "yoga mat",
  "monthly_searches": 450000,
  "cpc": 1.24,
  "difficulty_score": 72,
  "opportunity_score": 61,
  "related": [{ "keyword": "yoga mat non slip", "monthly_searches": 180000 }]
}
```

### POST /keywords/cluster
Cluster keywords by topic.
```json
Request: { "keywords": ["yoga mat", "exercise mat", "fitness mat", ...] }
Response: { "clusters": [{ "topic": "yoga", "keywords": [...], "total_volume": 750000 }] }
```

### GET /keywords/reverse-asin/{asin}
Get all keywords an ASIN ranks for.

---

## Competitors

### POST /competitors/weakness-scan
```json
Request: { "asin": "B08XYZ123", "marketplace": "amazon" }
Response: {
  "weaknesses": [
    { "type": "quality", "issue": "Cap leaks after 2 months", "frequency": 0.28, "sentiment": -0.82 }
  ],
  "opportunities": [
    { "improvement": "Double-wall seal with leak-proof guarantee", "impact_score": 84 }
  ],
  "competitive_advantage_score": 76
}
```

---

## AI Agents

### GET /agents
List all agents and their status.
```json
Response: [
  { "name": "product_research", "status": "running", "last_run": "2025-06-04T10:00:00Z", "findings": 12 }
]
```

### POST /agents/{agent_name}/run
Trigger a one-time agent run.
```json
Request: { "task": "Scan yoga accessories category for opportunities", "priority": "high" }
Response: { "run_id": "uuid", "status": "queued", "estimated_time_seconds": 45 }
```

### GET /agents/runs/{run_id}
Get agent run results.

---

## CEO Dashboard

### GET /analytics/ceo-recommendations
Get today's AI action plan.
```json
Response: {
  "date": "2025-06-04",
  "business_score": 72,
  "recommendations": {
    "actions": [
      { "action": "Reorder 500 units of Widget Pro", "urgency": "critical", "expected_impact": "+$8,400" }
    ]
  }
}
```

### POST /analytics/simulate
Digital twin simulation.
```json
Request: {
  "scenario_type": "price_change",
  "parameters": { "product_id": "uuid", "change_percent": 10 },
  "forecast_months": 6
}
Response: { "simulation": { "months": [...], "total_6m_profit": 42000, "recommendation": "go" } }
```

---

## Billing

### GET /billing/plans
List all plans.

### POST /billing/subscribe
Create subscription.
```json
Request: { "plan_id": "uuid", "payment_method": "pm_..." }
Response: { "subscription_id": "...", "status": "active", "trial_end": null }
```

### GET /billing/usage
Current usage vs plan limits.

---

## Rate Limits

| Plan         | Requests/min | Requests/hour | AI calls/day |
|--------------|-------------|---------------|--------------|
| Starter      | 30          | 500           | 100          |
| Professional | 60          | 2,000         | 500          |
| Business     | 120         | 5,000         | 2,000        |
| Agency       | 300         | 15,000        | 10,000       |
| Enterprise   | Unlimited   | Unlimited     | Unlimited    |

Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
