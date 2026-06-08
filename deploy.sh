#!/usr/bin/env bash
# ── SellerVision AI — Production Deploy Script ────────────────
# Usage:
#   ./deploy.sh                  — full deploy (build + migrate + restart + health check)
#   ./deploy.sh --no-migrate     — skip alembic upgrade head
#   ./deploy.sh --rollback       — roll back last migration and restart
#   ./deploy.sh --check-secrets  — only run the secrets gate, exit
set -euo pipefail

COMPOSE="docker compose"
BOLD="\033[1m"; GREEN="\033[32m"; RED="\033[31m"; YELLOW="\033[33m"; CYAN="\033[36m"; NC="\033[0m"

log()  { echo -e "${BOLD}[deploy]${NC} $*"; }
ok()   { echo -e "  ${GREEN}✓${NC} $*"; }
warn() { echo -e "  ${YELLOW}⚠${NC} $*"; }
fail() { echo -e "  ${RED}✗${NC} $*"; exit 1; }
info() { echo -e "  ${CYAN}→${NC} $*"; }

# ── Secrets gate ─────────────────────────────────────────────
# Reads backend/.env.production and validates that each required
# key is set and is NOT a placeholder value.
check_secrets() {
  log "Secrets gate — checking backend/.env.production..."

  ENV_FILE="backend/.env.production"
  [[ -f "$ENV_FILE" ]] || fail "$ENV_FILE not found. Copy backend/.env.production and fill in values."

  # Required keys and their placeholder patterns (regex)
  declare -A REQUIRED=(
    [SECRET_KEY]="CHANGE_ME"
    [CLERK_SECRET_KEY]="sk_live_\.\.\."
    [ANTHROPIC_API_KEY]="sk-ant-\.\.\."
    [STRIPE_SECRET_KEY]="sk_live_\.\.\."
    [STRIPE_WEBHOOK_SECRET]="whsec_\.\.\."
  )

  MISSING=0
  while IFS='=' read -r key value; do
    # Skip comments and blanks
    [[ "$key" =~ ^#.*$ || -z "$key" ]] && continue
    key="${key%%[[:space:]]*}"          # trim trailing whitespace
    value="${value%%[[:space:]#]*}"     # trim comments + whitespace

    if [[ -v REQUIRED["$key"] ]]; then
      placeholder="${REQUIRED[$key]}"
      if [[ -z "$value" ]]; then
        warn "EMPTY: $key — must be set before deploying to production"
        MISSING=$((MISSING+1))
      elif echo "$value" | grep -qE "$placeholder"; then
        warn "PLACEHOLDER: $key — still set to template value"
        MISSING=$((MISSING+1))
      else
        ok "$key"
      fi
      unset "REQUIRED[$key]"
    fi
  done < "$ENV_FILE"

  # Keys not found in file at all
  for key in "${!REQUIRED[@]}"; do
    warn "MISSING from file: $key"
    MISSING=$((MISSING+1))
  done

  if [[ $MISSING -gt 0 ]]; then
    echo ""
    echo -e "${RED}✗ $MISSING secret(s) need attention. Fix them before deploying.${NC}"
    exit 1
  fi

  ok "All required secrets are set"
}

# ── Parse args ────────────────────────────────────────────────
SKIP_MIGRATE=false
ROLLBACK=false
for arg in "$@"; do
  case "$arg" in
    --no-migrate)   SKIP_MIGRATE=true ;;
    --rollback)     ROLLBACK=true ;;
    --check-secrets) check_secrets; exit 0 ;;
  esac
done

# ── Preflight checks ─────────────────────────────────────────
log "Preflight checks..."
command -v docker >/dev/null 2>&1          || fail "Docker not installed"
docker info >/dev/null 2>&1               || fail "Docker daemon not running"
[[ -f backend/.env.production ]]           || fail "backend/.env.production missing"
[[ -f frontend/.env.production ]]          || fail "frontend/.env.production missing"
[[ -f nginx/ssl/fullchain.pem ]] \
  && ok "SSL cert found" \
  || warn "nginx/ssl/fullchain.pem missing — HTTPS will not work (run Certbot first)"
ok "Preflight passed"

# ── Secrets gate ─────────────────────────────────────────────
check_secrets

# ── Rollback path ────────────────────────────────────────────
if [[ "$ROLLBACK" == true ]]; then
  log "Rolling back last migration..."
  $COMPOSE run --rm backend alembic downgrade -1
  ok "Migration rolled back"
  log "Restarting services..."
  $COMPOSE up -d --remove-orphans
  ok "Done"
  exit 0
fi

# ── Pull base images ─────────────────────────────────────────
log "Pulling base images..."
$COMPOSE pull postgres redis 2>/dev/null || true

# ── Build app images ─────────────────────────────────────────
log "Building backend + celery images..."
$COMPOSE build --no-cache backend celery

log "Building frontend image..."
source frontend/.env.production 2>/dev/null || true
$COMPOSE build --no-cache \
  --build-arg NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-}" \
  --build-arg NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="${NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY:-}" \
  frontend

# ── Database migrations ──────────────────────────────────────
if [[ "$SKIP_MIGRATE" != true ]]; then
  log "Running database migrations..."
  $COMPOSE run --rm backend alembic upgrade head
  ok "Migrations applied"
fi

# ── Rolling restart ──────────────────────────────────────────
log "Starting services..."
$COMPOSE up -d --remove-orphans

# ── Health check — wait for /health to return 200 ────────────
log "Waiting for backend health check..."

# Determine health URL (direct port or through nginx)
HEALTH_URL="${HEALTH_URL:-http://localhost:8000/health}"
MAX_WAIT=60
COUNT=0

until curl -sf --max-time 3 "$HEALTH_URL" | grep -q '"status"'; do
  COUNT=$((COUNT+1))
  if [[ $COUNT -ge $MAX_WAIT ]]; then
    echo ""
    fail "Backend did not become healthy after ${MAX_WAIT}s. Check logs: docker compose logs backend"
  fi
  printf "."
  sleep 1
done

echo ""
HEALTH_JSON=$(curl -sf "$HEALTH_URL")
DB_STATUS=$(echo "$HEALTH_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['checks']['database']['status'])" 2>/dev/null || echo "unknown")
ok "Backend healthy (db=${DB_STATUS})"

# ── Summary ──────────────────────────────────────────────────
log "Deployment complete!"
echo ""
$COMPOSE ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo -e "${GREEN}${BOLD}SellerVision AI is live.${NC}"
echo -e "  ${CYAN}Frontend:${NC} https://yourdomain.com"
echo -e "  ${CYAN}API:${NC}      https://yourdomain.com/api/v1"
echo -e "  ${CYAN}Health:${NC}   $HEALTH_URL"
