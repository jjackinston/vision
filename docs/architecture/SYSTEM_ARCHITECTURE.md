# SellerVision AI — Complete System Architecture

## Overview

SellerVision AI is an enterprise-grade, AI-powered multi-platform e-commerce intelligence platform. It is architected as a cloud-native SaaS with event-driven microservices, multi-agent AI systems, and real-time analytics pipelines.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER                                       │
│  Next.js 14 (App Router) │ React 18 │ TypeScript │ TailwindCSS │ ShadCN UI  │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │ HTTPS / WebSocket
┌───────────────────────────────────▼─────────────────────────────────────────┐
│                           CDN / EDGE LAYER                                   │
│               AWS CloudFront │ Edge Caching │ DDoS Protection                │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────────────┐
│                         API GATEWAY LAYER                                    │
│         AWS API Gateway │ Rate Limiting │ Auth Middleware │ Load Balancer     │
└──────┬──────────────────┬──────────────────┬──────────────────┬─────────────┘
       │                  │                  │                  │
┌──────▼──────┐  ┌────────▼───────┐  ┌──────▼──────┐  ┌───────▼──────┐
│  FastAPI    │  │  WebSocket     │  │  AI Agent   │  │  MCP Agent   │
│  REST API   │  │  Server        │  │  Gateway    │  │  Orchestrator│
│  Service    │  │  (Real-time)   │  │  (LangChain)│  │  (MCP SDK)   │
└──────┬──────┘  └────────┬───────┘  └──────┬──────┘  └───────┬──────┘
       │                  │                  │                  │
┌──────▼──────────────────▼──────────────────▼──────────────────▼─────────────┐
│                         SERVICE MESH (Kubernetes)                             │
│                                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Product     │  │  Analytics   │  │  Inventory   │  │  Listing     │    │
│  │  Research    │  │  Service     │  │  Service     │  │  Service     │    │
│  │  Service     │  │              │  │              │  │              │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                  │                  │            │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐   │
│  │  Competitor  │  │  Keyword     │  │  Supplier    │  │  Billing     │   │
│  │  Service     │  │  Service     │  │  Service     │  │  Service     │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
└─────────┼─────────────────┼──────────────────┼──────────────────┼───────────┘
          │                 │                  │                  │
┌─────────▼─────────────────▼──────────────────▼──────────────────▼───────────┐
│                         DATA LAYER                                            │
│                                                                               │
│  PostgreSQL (Primary)  │  TimescaleDB (Time-series)  │  Redis (Cache/Queue)  │
│  Elasticsearch (Search)│  Pinecone/pgvector (Vector) │  S3 (Object Storage)  │
└───────────────────────────────────────────────────────────────────────────────┘
          │
┌─────────▼───────────────────────────────────────────────────────────────────┐
│                    INTEGRATION LAYER                                          │
│                                                                               │
│  Amazon SP-API │ Walmart API │ Shopify API │ eBay API │ TikTok Shop API      │
│  Etsy API      │ Google Trends │ OpenAI API │ Anthropic API │ Stripe API     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### 1. Frontend Architecture (Next.js 14)

```
frontend/
├── app/                          # App Router
│   ├── (auth)/                   # Auth group (no layout)
│   │   ├── login/
│   │   └── register/
│   ├── (dashboard)/              # Protected dashboard group
│   │   ├── layout.tsx            # Dashboard shell
│   │   ├── dashboard/            # AI CEO Dashboard
│   │   ├── products/             # Product Research
│   │   ├── keywords/             # Keyword Intelligence
│   │   ├── competitors/          # Competitor Analysis
│   │   ├── inventory/            # Inventory Command Center
│   │   ├── listings/             # Multi-Platform Listings
│   │   ├── analytics/            # Business Analytics
│   │   ├── agents/               # AI Agent Control Panel
│   │   ├── automation/           # Workflow Automation
│   │   ├── marketplace/          # SellerVision Marketplace
│   │   └── settings/             # Settings & Billing
│   └── api/                      # Next.js API Routes
├── components/
│   ├── ui/                       # ShadCN primitives
│   ├── charts/                   # Recharts wrappers
│   ├── modules/                  # Feature-specific components
│   ├── agents/                   # AI Agent UI components
│   └── layout/                   # Shell, Nav, Sidebar
├── lib/
│   ├── api.ts                    # API client
│   ├── auth.ts                   # Auth helpers
│   └── utils.ts
├── hooks/                        # Custom React hooks
├── stores/                       # Zustand state stores
└── types/                        # TypeScript definitions
```

### 2. Backend Architecture (FastAPI)

```
backend/
├── app/
│   ├── api/v1/endpoints/         # REST endpoints per module
│   ├── core/                     # Config, security, db
│   ├── models/                   # SQLAlchemy ORM models
│   ├── schemas/                  # Pydantic schemas
│   ├── services/                 # Business logic layer
│   ├── agents/                   # LangChain AI agents
│   ├── mcp/                      # MCP agent definitions
│   ├── ml/                       # ML models & inference
│   ├── integrations/             # Marketplace connectors
│   └── workers/                  # Celery background tasks
```

### 3. AI Architecture

```
AI Layer
├── LLM Gateway
│   ├── OpenAI GPT-4o             # Primary reasoning
│   ├── Anthropic Claude 3.5      # Analysis & writing
│   └── Cost optimizer            # Route by task type
├── RAG System
│   ├── Document ingestion        # Marketplace docs, reports
│   ├── Embedding pipeline        # text-embedding-3-large
│   ├── Vector store              # pgvector / Pinecone
│   └── Retrieval chain           # LangChain LCEL
├── Agent System (LangChain)
│   ├── Product Research Agent
│   ├── Trend Detection Agent
│   ├── Competitor Analysis Agent
│   ├── Inventory Planning Agent
│   ├── PPC Optimization Agent
│   ├── Supplier Intelligence Agent
│   └── Listing Optimization Agent
└── MCP Architecture
    ├── MCP Server (custom tools)
    ├── Tool definitions per module
    └── Agent-to-agent communication
```

---

## Multi-Tenant Architecture

```
Tenant Isolation Strategy: Schema-per-tenant (PostgreSQL)

┌─────────────────────────────────────────────────────┐
│  Public Schema                                       │
│  - tenants, plans, billing, global_config           │
└───────────────────────┬─────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌──────▼──────┐ ┌─────▼───────┐
│ tenant_abc   │ │ tenant_xyz  │ │ tenant_123  │
│ - products   │ │ - products  │ │ - products  │
│ - keywords   │ │ - keywords  │ │ - keywords  │
│ - analytics  │ │ - analytics │ │ - analytics │
│ - users      │ │ - users     │ │ - users     │
└──────────────┘ └─────────────┘ └─────────────┘

Row-Level Security (RLS) enforced at PostgreSQL level.
Tenant context injected via JWT claim.
```

---

## Security Architecture

- **Authentication**: Clerk (primary) with Auth0 fallback
- **Authorization**: RBAC with 5 roles: Owner, Admin, Manager, Analyst, Viewer
- **API Security**: JWT + API Keys with scopes
- **Data Encryption**: AES-256 at rest, TLS 1.3 in transit
- **Secret Management**: AWS Secrets Manager
- **Audit Logging**: Every mutation logged with user, timestamp, IP, action
- **Rate Limiting**: Per-plan, per-endpoint via Redis sliding window
- **MFA**: TOTP + SMS via Clerk
- **SOC2 Controls**: Full audit trail, data retention policies, access reviews

---

## Scalability Strategy

| Component       | Scaling Method                          | Target Capacity     |
|-----------------|----------------------------------------|---------------------|
| API Services    | Horizontal pod autoscaling (HPA)       | 10k req/s           |
| WebSocket       | Sticky sessions + Redis pub/sub        | 50k concurrent      |
| AI Agents       | Worker pool + Celery                   | 1000 concurrent     |
| Database        | Read replicas + connection pooling     | 100k queries/min    |
| Cache           | Redis Cluster                          | 1M ops/sec          |
| Search          | Elasticsearch cluster                  | Sub-100ms           |
| File Storage    | S3 + CloudFront                        | Unlimited           |
