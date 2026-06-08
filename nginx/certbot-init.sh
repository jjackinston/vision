#!/usr/bin/env bash
# ── SellerVision AI — First-time SSL Certificate (Let's Encrypt) ──
#
# Run this ONCE on your server BEFORE running ./deploy.sh
#
# Prerequisites:
#   1. Your domain's A record points to this server's IP
#   2. Port 80 is open (for ACME challenge)
#   3. docker + docker compose are installed
#
# Usage:
#   chmod +x nginx/certbot-init.sh
#   ./nginx/certbot-init.sh yourdomain.com admin@yourdomain.com
#
set -euo pipefail

DOMAIN="${1:-}"
EMAIL="${2:-}"

if [[ -z "$DOMAIN" || -z "$EMAIL" ]]; then
    echo "Usage: $0 <domain> <email>"
    echo "  e.g. $0 sellervision.ai admin@sellervision.ai"
    exit 1
fi

BOLD="\033[1m"; GREEN="\033[32m"; CYAN="\033[36m"; NC="\033[0m"
log() { echo -e "${BOLD}[certbot]${NC} $*"; }
ok()  { echo -e "  ${GREEN}✓${NC} $*"; }

log "Issuing SSL certificate for ${DOMAIN} via Let's Encrypt..."

# Step 1: Start nginx on port 80 only (no SSL yet — certs don't exist)
#   We temporarily swap in a plain HTTP-only config so Certbot can
#   complete the ACME challenge, then bring real nginx up after.
log "Step 1/3 — Starting HTTP-only nginx for ACME challenge..."
docker run -d --rm --name certbot-nginx \
    -p 80:80 \
    -v "$(pwd)/nginx/certbot-webroot:/var/www/certbot:ro" \
    nginx:alpine \
    nginx -g "daemon off;" &

# Give nginx a moment to start
sleep 2

# Step 2: Run Certbot in standalone mode using webroot
log "Step 2/3 — Running Certbot..."
docker run --rm \
    -v "$(pwd)/nginx/ssl:/etc/letsencrypt/live/${DOMAIN}" \
    -v "$(pwd)/nginx/certbot-webroot:/var/www/certbot" \
    certbot/certbot certonly \
    --webroot \
    --webroot-path /var/www/certbot \
    --email "${EMAIL}" \
    --agree-tos \
    --no-eff-email \
    -d "${DOMAIN}" \
    -d "www.${DOMAIN}"

# Stop the temporary nginx
docker stop certbot-nginx 2>/dev/null || true

# Step 3: Copy certs to nginx/ssl/ where docker-compose mounts them
log "Step 3/3 — Placing certificates..."
CERT_PATH="$(pwd)/nginx/ssl"
LETSENCRYPT_PATH="/etc/letsencrypt/live/${DOMAIN}"

# If running on the host (not in Docker), certs are at the real path:
if [[ -d "/etc/letsencrypt/live/${DOMAIN}" ]]; then
    cp "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" "${CERT_PATH}/fullchain.pem"
    cp "/etc/letsencrypt/live/${DOMAIN}/privkey.pem"   "${CERT_PATH}/privkey.pem"
    ok "Certificates copied to nginx/ssl/"
else
    ok "Certificates written to nginx/ssl/ via Docker volume mount"
fi

# Update nginx.conf with the real domain (replace placeholder)
sed -i "s/yourdomain.com www.yourdomain.com/${DOMAIN} www.${DOMAIN}/g" \
    "$(pwd)/nginx/nginx.conf"
ok "Updated nginx.conf server_name → ${DOMAIN}"

echo ""
echo -e "${GREEN}${BOLD}SSL certificate issued successfully!${NC}"
echo -e "  Certificate:  ${CERT_PATH}/fullchain.pem"
echo -e "  Private key:  ${CERT_PATH}/privkey.pem"
echo -e "  Domain:       https://${DOMAIN}"
echo ""
echo "Next: run ./deploy.sh to start all services with HTTPS."
echo ""
echo "Auto-renewal: add this cron job on your server:"
echo "  0 3 * * * docker run --rm -v /etc/letsencrypt:/etc/letsencrypt certbot/certbot renew --quiet && docker compose -f $(pwd)/docker-compose.yml exec nginx nginx -s reload"
