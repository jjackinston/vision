-- ============================================================
-- SellerVision AI — Complete Database Schema
-- PostgreSQL 16 + TimescaleDB extension
-- ============================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";
CREATE EXTENSION IF NOT EXISTS "timescaledb";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================
-- SCHEMA: public (multi-tenant global)
-- ============================================================

-- TENANTS (Organizations/Workspaces)
CREATE TABLE public.tenants (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug            VARCHAR(100) UNIQUE NOT NULL,
    name            VARCHAR(255) NOT NULL,
    plan_id         UUID REFERENCES public.plans(id),
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    trial_ends_at   TIMESTAMPTZ,
    is_active       BOOLEAN DEFAULT TRUE,
    white_label     BOOLEAN DEFAULT FALSE,
    white_label_config JSONB DEFAULT '{}',
    settings        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- PLANS
CREATE TABLE public.plans (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(100) NOT NULL, -- starter, professional, business, agency, enterprise
    stripe_price_id VARCHAR(255),
    stripe_product_id VARCHAR(255),
    price_monthly   DECIMAL(10,2),
    price_annual    DECIMAL(10,2),
    limits          JSONB NOT NULL DEFAULT '{}',
    -- limits example: {"products": 100, "keywords": 500, "api_calls": 10000, "users": 3, "marketplaces": 2}
    features        JSONB NOT NULL DEFAULT '{}',
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- USERS
CREATE TABLE public.users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clerk_id        VARCHAR(255) UNIQUE,
    email           VARCHAR(255) UNIQUE NOT NULL,
    full_name       VARCHAR(255),
    avatar_url      TEXT,
    is_active       BOOLEAN DEFAULT TRUE,
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- TENANT MEMBERS (RBAC)
CREATE TABLE public.tenant_members (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    role            VARCHAR(50) NOT NULL DEFAULT 'analyst',
    -- roles: owner, admin, manager, analyst, viewer
    permissions     JSONB DEFAULT '{}',
    invited_by      UUID REFERENCES public.users(id),
    joined_at       TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, user_id)
);

-- API KEYS
CREATE TABLE public.api_keys (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES public.users(id),
    name            VARCHAR(255) NOT NULL,
    key_hash        VARCHAR(255) UNIQUE NOT NULL,
    key_prefix      VARCHAR(20) NOT NULL,
    scopes          TEXT[] DEFAULT '{}',
    last_used_at    TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- AUDIT LOGS
CREATE TABLE public.audit_logs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID REFERENCES public.tenants(id),
    user_id         UUID REFERENCES public.users(id),
    action          VARCHAR(255) NOT NULL,
    resource_type   VARCHAR(100),
    resource_id     UUID,
    metadata        JSONB DEFAULT '{}',
    ip_address      INET,
    user_agent      TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_audit_logs_tenant ON public.audit_logs(tenant_id, created_at DESC);

-- MARKETPLACE CONNECTIONS
CREATE TABLE public.marketplace_connections (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
    marketplace     VARCHAR(50) NOT NULL, -- amazon, walmart, shopify, ebay, tiktok, etsy
    account_name    VARCHAR(255),
    credentials     JSONB NOT NULL DEFAULT '{}', -- encrypted
    status          VARCHAR(50) DEFAULT 'active',
    last_sync_at    TIMESTAMPTZ,
    sync_config     JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- FUNCTION: create_tenant_schema
-- Creates isolated schema per tenant
-- ============================================================
CREATE OR REPLACE FUNCTION create_tenant_schema(tenant_slug TEXT)
RETURNS VOID AS $$
BEGIN
    EXECUTE format('CREATE SCHEMA IF NOT EXISTS %I', 'tenant_' || tenant_slug);
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- SCHEMA: tenant_{slug} (per-tenant tables)
-- Below tables are created per tenant via create_tenant_schema()
-- Shown here as template in public schema for documentation
-- ============================================================

-- PRODUCTS (researched/tracked)
CREATE TABLE IF NOT EXISTS products (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asin                VARCHAR(20),
    walmart_item_id     VARCHAR(50),
    shopify_product_id  VARCHAR(100),
    ebay_item_id        VARCHAR(100),
    tiktok_product_id   VARCHAR(100),
    etsy_listing_id     VARCHAR(100),
    title               VARCHAR(1000) NOT NULL,
    brand               VARCHAR(255),
    category            VARCHAR(255),
    subcategory         VARCHAR(255),
    marketplace         VARCHAR(50) NOT NULL,
    image_urls          TEXT[],
    current_price       DECIMAL(12,2),
    buy_box_price       DECIMAL(12,2),
    cost                DECIMAL(12,2),
    weight_lbs          DECIMAL(8,3),
    dimensions          JSONB, -- {l, w, h}
    is_tracked          BOOLEAN DEFAULT FALSE,
    is_own_product      BOOLEAN DEFAULT FALSE,
    tags                TEXT[],
    notes               TEXT,
    opportunity_score   DECIMAL(5,2),
    risk_score          DECIMAL(5,2),
    profit_score        DECIMAL(5,2),
    competition_score   DECIMAL(5,2),
    market_entry_score  DECIMAL(5,2),
    ai_analysis         JSONB DEFAULT '{}',
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_products_asin ON products(asin) WHERE asin IS NOT NULL;
CREATE INDEX idx_products_marketplace ON products(marketplace);
CREATE INDEX idx_products_opportunity ON products(opportunity_score DESC);

-- PRODUCT METRICS (TimescaleDB hypertable)
CREATE TABLE IF NOT EXISTS product_metrics (
    time                TIMESTAMPTZ NOT NULL,
    product_id          UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    marketplace         VARCHAR(50) NOT NULL,
    price               DECIMAL(12,2),
    bsr_rank            INTEGER,
    bsr_category        VARCHAR(255),
    review_count        INTEGER,
    review_rating       DECIMAL(3,2),
    estimated_sales     INTEGER,
    estimated_revenue   DECIMAL(12,2),
    seller_count        INTEGER,
    buy_box_seller      VARCHAR(255),
    stock_level         VARCHAR(50),
    metadata            JSONB DEFAULT '{}'
);
SELECT create_hypertable('product_metrics', 'time');
CREATE INDEX idx_product_metrics_product ON product_metrics(product_id, time DESC);

-- KEYWORDS
CREATE TABLE IF NOT EXISTS keywords (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    keyword             VARCHAR(500) NOT NULL,
    marketplace         VARCHAR(50) NOT NULL,
    monthly_searches    INTEGER,
    search_volume_trend DECIMAL(5,2),
    cpc                 DECIMAL(8,4),
    competition_level   VARCHAR(20),
    difficulty_score    DECIMAL(5,2),
    opportunity_score   DECIMAL(5,2),
    ppc_score           DECIMAL(5,2),
    seo_score           DECIMAL(5,2),
    intent              VARCHAR(50),
    cluster_id          UUID,
    parent_keyword      VARCHAR(500),
    related_keywords    TEXT[],
    ai_analysis         JSONB DEFAULT '{}',
    last_updated        TIMESTAMPTZ DEFAULT NOW(),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(keyword, marketplace)
);
CREATE INDEX idx_keywords_keyword_trgm ON keywords USING gin(keyword gin_trgm_ops);
CREATE INDEX idx_keywords_opportunity ON keywords(opportunity_score DESC);

-- KEYWORD METRICS (TimescaleDB)
CREATE TABLE IF NOT EXISTS keyword_metrics (
    time                TIMESTAMPTZ NOT NULL,
    keyword_id          UUID NOT NULL REFERENCES keywords(id) ON DELETE CASCADE,
    search_volume       INTEGER,
    cpc                 DECIMAL(8,4),
    ranking_products    INTEGER,
    top_3_asins         TEXT[],
    sponsored_count     INTEGER
);
SELECT create_hypertable('keyword_metrics', 'time');

-- PRODUCT KEYWORDS (junction)
CREATE TABLE IF NOT EXISTS product_keywords (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id          UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    keyword_id          UUID NOT NULL REFERENCES keywords(id) ON DELETE CASCADE,
    organic_rank        INTEGER,
    sponsored_rank      INTEGER,
    indexed             BOOLEAN DEFAULT FALSE,
    relevance_score     DECIMAL(5,2),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(product_id, keyword_id)
);

-- COMPETITORS
CREATE TABLE IF NOT EXISTS competitors (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id          UUID REFERENCES products(id),
    asin                VARCHAR(20),
    marketplace         VARCHAR(50) NOT NULL,
    seller_id           VARCHAR(100),
    brand               VARCHAR(255),
    title               VARCHAR(1000),
    price               DECIMAL(12,2),
    review_count        INTEGER,
    review_rating       DECIMAL(3,2),
    monthly_sales       INTEGER,
    monthly_revenue     DECIMAL(12,2),
    weakness_analysis   JSONB DEFAULT '{}',
    threat_level        VARCHAR(20),
    tracked_since       TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- INVENTORY
CREATE TABLE IF NOT EXISTS inventory (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id          UUID NOT NULL REFERENCES products(id),
    warehouse_id        UUID REFERENCES warehouses(id),
    marketplace         VARCHAR(50),
    sku                 VARCHAR(255),
    fnsku               VARCHAR(255),
    quantity_on_hand    INTEGER DEFAULT 0,
    quantity_reserved   INTEGER DEFAULT 0,
    quantity_inbound    INTEGER DEFAULT 0,
    reorder_point       INTEGER,
    reorder_quantity    INTEGER,
    lead_time_days      INTEGER DEFAULT 30,
    unit_cost           DECIMAL(12,4),
    stockout_date       DATE,
    overstock_risk      BOOLEAN DEFAULT FALSE,
    last_order_date     DATE,
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- WAREHOUSES
CREATE TABLE IF NOT EXISTS warehouses (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name                VARCHAR(255) NOT NULL,
    type                VARCHAR(50), -- fba, fbm, 3pl, own
    address             JSONB,
    country_code        VARCHAR(5),
    marketplace_codes   TEXT[],
    active              BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- INVENTORY EVENTS (TimescaleDB)
CREATE TABLE IF NOT EXISTS inventory_events (
    time                TIMESTAMPTZ NOT NULL,
    inventory_id        UUID NOT NULL REFERENCES inventory(id),
    event_type          VARCHAR(50), -- sale, restock, adjustment, return, damage
    quantity_change     INTEGER NOT NULL,
    quantity_after      INTEGER NOT NULL,
    reference_id        VARCHAR(255),
    notes               TEXT
);
SELECT create_hypertable('inventory_events', 'time');

-- SUPPLIERS
CREATE TABLE IF NOT EXISTS suppliers (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name                VARCHAR(255) NOT NULL,
    country             VARCHAR(100),
    contact_name        VARCHAR(255),
    contact_email       VARCHAR(255),
    contact_phone       VARCHAR(50),
    website             TEXT,
    alibaba_url         TEXT,
    trust_score         DECIMAL(5,2),
    risk_score          DECIMAL(5,2),
    quality_score       DECIMAL(5,2),
    reliability_score   DECIMAL(5,2),
    avg_lead_time_days  INTEGER,
    min_order_qty       INTEGER,
    payment_terms       VARCHAR(255),
    shipping_methods    TEXT[],
    certifications      TEXT[],
    notes               TEXT,
    ai_analysis         JSONB DEFAULT '{}',
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- SUPPLIER PRODUCTS
CREATE TABLE IF NOT EXISTS supplier_products (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    supplier_id         UUID NOT NULL REFERENCES suppliers(id),
    product_id          UUID REFERENCES products(id),
    supplier_sku        VARCHAR(255),
    unit_cost           DECIMAL(12,4) NOT NULL,
    moq                 INTEGER,
    sample_cost         DECIMAL(10,2),
    lead_time_days      INTEGER,
    is_preferred        BOOLEAN DEFAULT FALSE,
    last_quoted_at      TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- LISTINGS
CREATE TABLE IF NOT EXISTS listings (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id          UUID NOT NULL REFERENCES products(id),
    marketplace         VARCHAR(50) NOT NULL,
    external_id         VARCHAR(255),
    title               VARCHAR(1000),
    bullet_points       TEXT[],
    description         TEXT,
    a_plus_content      JSONB,
    backend_keywords    TEXT[],
    images              JSONB,
    price               DECIMAL(12,2),
    sale_price          DECIMAL(12,2),
    status              VARCHAR(50) DEFAULT 'draft',
    seo_score           DECIMAL(5,2),
    completeness_score  DECIMAL(5,2),
    ai_generated        BOOLEAN DEFAULT FALSE,
    published_at        TIMESTAMPTZ,
    last_synced_at      TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- PPC CAMPAIGNS
CREATE TABLE IF NOT EXISTS ppc_campaigns (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id          UUID REFERENCES products(id),
    marketplace         VARCHAR(50) NOT NULL,
    campaign_id         VARCHAR(255),
    name                VARCHAR(500),
    type                VARCHAR(50), -- sponsored_products, sponsored_brands, sponsored_display
    status              VARCHAR(50),
    daily_budget        DECIMAL(10,2),
    spend_today         DECIMAL(10,2),
    impressions         INTEGER,
    clicks              INTEGER,
    orders              INTEGER,
    revenue             DECIMAL(12,2),
    acos                DECIMAL(5,2),
    roas                DECIMAL(5,2),
    tacos               DECIMAL(5,2),
    ai_recommendations  JSONB DEFAULT '{}',
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- TRENDS
CREATE TABLE IF NOT EXISTS trends (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    topic               VARCHAR(500) NOT NULL,
    source              VARCHAR(50), -- amazon, google, tiktok, reddit, pinterest
    category            VARCHAR(255),
    trend_score         DECIMAL(5,2),
    momentum_score      DECIMAL(5,2),
    viral_score         DECIMAL(5,2),
    lifespan_prediction VARCHAR(50),
    peak_date_estimate  DATE,
    related_products    TEXT[],
    data_points         JSONB DEFAULT '{}',
    ai_analysis         JSONB DEFAULT '{}',
    detected_at         TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- AI AGENT RUNS
CREATE TABLE IF NOT EXISTS agent_runs (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_type          VARCHAR(100) NOT NULL,
    status              VARCHAR(50) DEFAULT 'running',
    input               JSONB DEFAULT '{}',
    output              JSONB DEFAULT '{}',
    steps               JSONB DEFAULT '[]',
    tokens_used         INTEGER DEFAULT 0,
    cost_usd            DECIMAL(10,6),
    error               TEXT,
    started_at          TIMESTAMPTZ DEFAULT NOW(),
    completed_at        TIMESTAMPTZ
);

-- AUTOMATION WORKFLOWS
CREATE TABLE IF NOT EXISTS workflows (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name                VARCHAR(255) NOT NULL,
    description         TEXT,
    trigger_type        VARCHAR(100), -- schedule, event, webhook, manual
    trigger_config      JSONB DEFAULT '{}',
    steps               JSONB DEFAULT '[]',
    is_active           BOOLEAN DEFAULT TRUE,
    last_run_at         TIMESTAMPTZ,
    run_count           INTEGER DEFAULT 0,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- MARKETPLACE ASSETS (SellerVision Marketplace)
CREATE TABLE IF NOT EXISTS marketplace_assets (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    creator_id          UUID REFERENCES public.users(id),
    type                VARCHAR(50), -- dashboard, prompt, agent, automation, template
    name                VARCHAR(255) NOT NULL,
    description         TEXT,
    price               DECIMAL(10,2) DEFAULT 0,
    downloads           INTEGER DEFAULT 0,
    rating              DECIMAL(3,2),
    rating_count        INTEGER DEFAULT 0,
    asset_data          JSONB NOT NULL DEFAULT '{}',
    tags                TEXT[],
    preview_images      TEXT[],
    is_published        BOOLEAN DEFAULT FALSE,
    is_verified         BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- SALES ANALYTICS (TimescaleDB)
CREATE TABLE IF NOT EXISTS sales_analytics (
    time                TIMESTAMPTZ NOT NULL,
    product_id          UUID NOT NULL REFERENCES products(id),
    marketplace         VARCHAR(50) NOT NULL,
    orders              INTEGER DEFAULT 0,
    units_sold          INTEGER DEFAULT 0,
    gross_revenue       DECIMAL(14,2) DEFAULT 0,
    refunds             DECIMAL(14,2) DEFAULT 0,
    platform_fees       DECIMAL(14,2) DEFAULT 0,
    ad_spend            DECIMAL(14,2) DEFAULT 0,
    cogs                DECIMAL(14,2) DEFAULT 0,
    net_profit          DECIMAL(14,2) DEFAULT 0,
    roi                 DECIMAL(6,4)
);
SELECT create_hypertable('sales_analytics', 'time');
CREATE INDEX idx_sales_analytics_product ON sales_analytics(product_id, time DESC);

-- NOTIFICATIONS
CREATE TABLE IF NOT EXISTS notifications (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES public.users(id),
    type                VARCHAR(100) NOT NULL,
    title               VARCHAR(500) NOT NULL,
    body                TEXT,
    action_url          TEXT,
    metadata            JSONB DEFAULT '{}',
    is_read             BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_notifications_user ON notifications(user_id, is_read, created_at DESC);

-- VECTOR EMBEDDINGS (for RAG)
CREATE TABLE IF NOT EXISTS embeddings (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_type         VARCHAR(100), -- product, keyword, review, trend, supplier
    source_id           UUID,
    content             TEXT NOT NULL,
    embedding           VECTOR(1536),
    metadata            JSONB DEFAULT '{}',
    created_at          TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_embeddings_vector ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_embeddings_source ON embeddings(source_type, source_id);
