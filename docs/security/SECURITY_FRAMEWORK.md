# SellerVision AI — Security Framework

## Authentication & Authorization

### Multi-Layer Auth
1. **Clerk JWT** — Primary user auth with RS256 signing
2. **API Keys** — SHA-256 hashed, prefix-based identification
3. **Service-to-service** — mTLS within Kubernetes cluster

### RBAC Matrix

| Permission          | Owner | Admin | Manager | Analyst | Viewer |
|--------------------|:-----:|:-----:|:-------:|:-------:|:------:|
| View all data      | ✅    | ✅    | ✅      | ✅      | ✅     |
| Create/edit        | ✅    | ✅    | ✅      | ✅      | ❌     |
| Delete             | ✅    | ✅    | ✅      | ❌      | ❌     |
| Manage team        | ✅    | ✅    | ❌      | ❌      | ❌     |
| Billing            | ✅    | ❌    | ❌      | ❌      | ❌     |
| API keys           | ✅    | ✅    | ❌      | ❌      | ❌     |
| Agent control      | ✅    | ✅    | ✅      | ❌      | ❌     |

### MFA
- TOTP (Google Authenticator, Authy)
- SMS via Twilio (backup)
- Required for Owner and Admin roles in Enterprise plan

---

## Data Security

### Encryption
- **At rest**: AES-256 (RDS, S3, EBS)
- **In transit**: TLS 1.3 minimum
- **Marketplace credentials**: AWS KMS-encrypted, stored in Secrets Manager
- **API keys**: One-way SHA-256 hash, full key shown only once at creation

### Database Security
- **Row-Level Security (RLS)**: Enforced at PostgreSQL level per tenant schema
- **Connection pooling**: PgBouncer with auth_user isolation
- **Read replicas**: Analytics queries routed to replicas
- **Automated backups**: 30-day retention, point-in-time recovery

### Secrets Management
```
AWS Secrets Manager
├── sellervision/prod/database
├── sellervision/prod/redis
├── sellervision/prod/openai
├── sellervision/prod/anthropic
├── sellervision/prod/stripe
├── sellervision/prod/clerk
└── sellervision/prod/marketplaces/{tenant_id}/{marketplace}
```

---

## Network Security

### AWS Architecture
- VPC with private subnets for databases
- Public subnets only for ALB
- Security groups with principle of least privilege
- NACLs as secondary layer
- VPC Flow Logs enabled

### WAF Rules (AWS WAF)
- OWASP Core Rule Set
- Rate-based rules (500 req/5min per IP)
- IP reputation list
- SQL injection protection
- XSS protection
- Bot management

### DDoS Protection
- AWS Shield Standard (included)
- AWS Shield Advanced for Enterprise customers
- CloudFront absorbs volumetric attacks

---

## Application Security

### OWASP Top 10 Mitigations

| Threat                    | Mitigation                                           |
|---------------------------|------------------------------------------------------|
| Injection (SQL, NoSQL)    | SQLAlchemy ORM, parameterized queries always         |
| Broken Auth               | Clerk JWT, short-lived tokens, secure cookies        |
| Sensitive Data Exposure   | Encryption at rest/transit, no PII logging          |
| XXE                       | XML parsing disabled; JSON-only APIs                |
| Broken Access Control     | RBAC + RLS at DB level + API middleware              |
| Security Misconfiguration | Hardened Docker images, no default credentials       |
| XSS                       | React (auto-escaping), CSP headers, sanitize inputs  |
| Insecure Deserialization  | Pydantic validation on all inputs                    |
| Known Vulnerabilities     | Dependabot + Trivy weekly scans                      |
| Insufficient Logging      | Structured audit logs for all mutations              |

### Input Validation
- All API inputs validated with Pydantic v2 schemas
- File uploads: type validation, size limits, virus scan (ClamAV)
- Rate limiting per endpoint per tenant

### Security Headers
```
Content-Security-Policy: default-src 'self'; ...
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(self), geolocation=()
```

---

## Audit & Compliance

### Audit Log Schema
Every state change logs:
- timestamp
- tenant_id
- user_id
- IP address
- user_agent
- action (CREATE/UPDATE/DELETE)
- resource_type + resource_id
- before/after state (for sensitive changes)
- request_id (for tracing)

### Compliance
- **GDPR**: Data export, data deletion, DPA available
- **CCPA**: Right to know, opt-out, deletion
- **SOC2 Type II**: Controls documented, audit trail complete (Year 1 target)
- **PCI DSS**: Stripe handles all card data; we are Level 4 merchant
- **Data Residency**: EU data stored in AWS eu-west-1

### Incident Response
1. Detection (Grafana alerts / AWS GuardDuty)
2. Contain (isolate tenant, revoke tokens)
3. Investigate (audit logs, CloudTrail)
4. Remediate
5. Notify (72-hour GDPR window)
6. Post-mortem

---

## Penetration Testing
- External pentest every 6 months
- Bug bounty program via HackerOne ($100–$5,000 per severity)
- Internal security review on every major feature
