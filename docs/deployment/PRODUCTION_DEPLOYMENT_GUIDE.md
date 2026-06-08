# SellerVision AI — Production Deployment Guide

## Prerequisites

- AWS Account with admin access
- Domain name with DNS control
- Docker & Docker Compose installed locally
- kubectl and AWS CLI configured
- Stripe account
- Clerk account
- OpenAI and Anthropic API keys

---

## Step 1: Infrastructure Setup (AWS)

### 1.1 Create EKS Cluster

```bash
eksctl create cluster \
  --name sellervision-prod \
  --region us-east-1 \
  --nodegroup-name standard \
  --node-type m5.xlarge \
  --nodes 3 \
  --nodes-min 3 \
  --nodes-max 20 \
  --managed
```

### 1.2 Install Cluster Add-ons

```bash
# AWS Load Balancer Controller
helm repo add eks https://aws.github.io/eks-charts
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=sellervision-prod

# Cert Manager (TLS)
helm repo add jetstack https://charts.jetstack.io
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager --create-namespace \
  --set installCRDs=true

# Metrics Server (for HPA)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

### 1.3 Create RDS PostgreSQL with TimescaleDB

```bash
aws rds create-db-instance \
  --db-instance-identifier sellervision-prod \
  --db-instance-class db.r6g.2xlarge \
  --engine postgres \
  --engine-version 16.3 \
  --master-username sellervision \
  --master-user-password $DB_PASSWORD \
  --allocated-storage 500 \
  --storage-type gp3 \
  --multi-az \
  --backup-retention-period 30 \
  --deletion-protection
```

### 1.4 ElastiCache Redis

```bash
aws elasticache create-replication-group \
  --replication-group-id sellervision-redis \
  --replication-group-description "SellerVision Redis" \
  --num-cache-clusters 3 \
  --cache-node-type cache.r6g.large \
  --engine redis \
  --engine-version 7.0 \
  --at-rest-encryption-enabled \
  --transit-encryption-enabled
```

---

## Step 2: Kubernetes Secrets

```bash
kubectl create namespace sellervision

kubectl create secret generic sellervision-secrets \
  --from-literal=DATABASE_URL="postgresql+asyncpg://sellervision:$DB_PASSWORD@$RDS_ENDPOINT:5432/sellervision" \
  --from-literal=REDIS_URL="rediss://:$REDIS_TOKEN@$REDIS_ENDPOINT:6380/0" \
  --from-literal=SECRET_KEY="$(openssl rand -hex 32)" \
  --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
  --from-literal=ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  --from-literal=CLERK_SECRET_KEY="$CLERK_SECRET_KEY" \
  --from-literal=STRIPE_SECRET_KEY="$STRIPE_SECRET_KEY" \
  -n sellervision
```

---

## Step 3: Database Initialization

```bash
# Run migrations
kubectl run migration --image=sellervision/api:latest \
  --restart=Never -n sellervision \
  --env-from=secret/sellervision-secrets \
  -- alembic upgrade head

# Create initial plans
kubectl run seed --image=sellervision/api:latest \
  --restart=Never -n sellervision \
  --env-from=secret/sellervision-secrets \
  -- python scripts/seed_plans.py
```

---

## Step 4: Deploy Application

```bash
# Apply all Kubernetes manifests
kubectl apply -f infrastructure/kubernetes/base/ -n sellervision
kubectl apply -f infrastructure/kubernetes/services/ -n sellervision

# Verify deployments
kubectl get pods -n sellervision
kubectl get services -n sellervision
kubectl get ingress -n sellervision
```

---

## Step 5: Configure DNS & TLS

```bash
# Get the load balancer hostname
kubectl get ingress -n sellervision -o jsonpath='{.items[0].status.loadBalancer.ingress[0].hostname}'

# Create DNS records in Route53:
# app.sellervisionai.com → ALB hostname (CNAME)
# api.sellervisionai.com → ALB hostname (CNAME)
```

---

## Step 6: Configure Monitoring

```bash
# Install Prometheus + Grafana stack
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  -f infrastructure/monitoring/prometheus-values.yaml
```

---

## Step 7: Configure Stripe

1. Create products in Stripe Dashboard:
   - Starter: $49/mo
   - Professional: $149/mo
   - Business: $299/mo
   - Agency: $499/mo
   - Enterprise: Custom

2. Add webhook endpoint: `https://api.sellervisionai.com/api/v1/webhooks/stripe`
3. Enable events: `customer.subscription.*`, `invoice.*`, `checkout.session.completed`

---

## Step 8: Configure Clerk

1. Create application in Clerk Dashboard
2. Add OAuth providers (Google, Microsoft)
3. Enable MFA
4. Set webhook: `https://api.sellervisionai.com/api/v1/webhooks/clerk`
5. Add custom claims for tenant_id

---

## Step 9: Configure Marketplace APIs

### Amazon SP-API
1. Register as Amazon Developer
2. Create SP-API application
3. Get LWA credentials (Client ID, Client Secret)
4. Request Selling Partner OAuth authorization
5. Store credentials in AWS Secrets Manager

### Walmart
1. Register at Walmart Developer Portal
2. Request API access
3. Generate Client ID and Secret

### Shopify
1. Create Shopify App in Partner Dashboard
2. Request scopes: `read_products`, `write_products`, `read_orders`, `read_inventory`

---

## Performance Benchmarks (Target)

| Metric                        | Target    |
|-------------------------------|-----------|
| API P50 latency               | < 50ms    |
| API P99 latency               | < 200ms   |
| AI response time              | < 3s      |
| Dashboard load time           | < 1.5s    |
| Uptime SLA                    | 99.9%     |
| Data freshness (metrics)      | < 1 hour  |
| Concurrent users              | 10,000+   |

---

## Scaling Thresholds

| Load Level      | API Pods | Worker Pods | DB Connections |
|-----------------|----------|-------------|----------------|
| < 1k users      | 3        | 2           | 20             |
| 1k–5k users     | 6        | 4           | 50             |
| 5k–20k users    | 12       | 8           | 100            |
| > 20k users     | 20+      | 16+         | 200+           |

---

## Rollback Procedure

```bash
# Rollback to previous version
kubectl rollout undo deployment/sellervision-api -n sellervision
kubectl rollout undo deployment/sellervision-frontend -n sellervision

# Verify rollback
kubectl rollout status deployment/sellervision-api -n sellervision
```

---

## Cost Estimate (AWS, Production)

| Service              | Monthly Cost |
|----------------------|-------------|
| EKS (3x m5.xlarge)  | $440        |
| RDS (r6g.2xlarge)   | $580        |
| ElastiCache (r6g.lg) | $210        |
| OpenAI API           | $500–$2,000 |
| Anthropic API        | $200–$800   |
| CloudFront + S3      | $50–$200    |
| ALB + networking     | $100        |
| **Total**            | **$2,080–$4,330** |

At $149/mo Professional plan: 14–29 paying customers covers infrastructure.
