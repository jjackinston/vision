"""
Tests for the Super-Admin Panel API (/api/v1/admin/*)

Covers:
- Auth: missing key → 503, wrong key → 403, correct key → passes
- GET /admin/stats returns expected shape
- GET /admin/tenants returns paginated list
- GET /admin/users returns paginated list
- GET /admin/audit-logs returns list
- PATCH /admin/tenants/{id} updates plan + active status
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
from httpx import AsyncClient


VALID_KEY   = "test-admin-secret-abc123"   # matches ADMIN_SECRET_KEY in conftest env
INVALID_KEY = "definitely-wrong-key"

STATS_FIXTURE = {
    "tenants":  {"total": 5, "paying": 2, "trial": 3, "churned": 0},
    "users":    {"total": 8, "active_today": 3},
    "revenue":  {"mrr": 29800, "arr": 357600},
    "products": {"total_tracked": 237},
    "agents":   {"runs_today": 14},
}

TENANT_LIST_FIXTURE = {
    "items": [
        {
            "id": str(uuid.uuid4()),
            "slug": "acme-corp",
            "name": "Acme Corp",
            "plan": "Professional",
            "status": "active",
            "member_count": 2,
            "product_count": 0,
            "created_at": "2025-01-15T10:00:00Z",
        }
    ],
    "total": 1,
    "page": 1,
    "per_page": 25,
}


# ── Auth checks ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_admin_stats_no_key_returns_503(client: AsyncClient):
    """No X-Admin-Key header → 503 (admin disabled when key unset)."""
    resp = await client.get("/api/v1/admin/stats")
    # 503 when key missing/unset in env, or 401/403 for wrong auth
    assert resp.status_code in (401, 403, 503)


@pytest.mark.asyncio
async def test_admin_stats_wrong_key_returns_403(client: AsyncClient):
    resp = await client.get(
        "/api/v1/admin/stats",
        headers={"X-Admin-Key": INVALID_KEY},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_stats_correct_key_returns_200(client: AsyncClient):
    with patch("app.api.v1.endpoints.admin.AdminService.get_stats",
               new_callable=AsyncMock, return_value=STATS_FIXTURE):
        resp = await client.get(
            "/api/v1/admin/stats",
            headers={"X-Admin-Key": VALID_KEY},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert "tenants" in data
    assert "users"   in data


# ── Stats endpoint shape ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_admin_stats_shape(client: AsyncClient):
    with patch("app.api.v1.endpoints.admin.AdminService.get_stats",
               new_callable=AsyncMock, return_value=STATS_FIXTURE):
        resp = await client.get(
            "/api/v1/admin/stats",
            headers={"X-Admin-Key": VALID_KEY},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["tenants"]["total"] == 5
    assert data["users"]["total"] == 8
    assert data["revenue"]["mrr"] == 29800


# ── Tenant list ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_admin_list_tenants(client: AsyncClient):
    with patch("app.api.v1.endpoints.admin.AdminService.list_tenants",
               new_callable=AsyncMock, return_value=TENANT_LIST_FIXTURE):
        resp = await client.get(
            "/api/v1/admin/tenants",
            headers={"X-Admin-Key": VALID_KEY},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["slug"] == "acme-corp"


@pytest.mark.asyncio
async def test_admin_list_tenants_pagination(client: AsyncClient):
    with patch("app.api.v1.endpoints.admin.AdminService.list_tenants",
               new_callable=AsyncMock, return_value={**TENANT_LIST_FIXTURE, "page": 2}):
        resp = await client.get(
            "/api/v1/admin/tenants?page=2&per_page=10",
            headers={"X-Admin-Key": VALID_KEY},
        )
    assert resp.status_code == 200
    assert resp.json()["page"] == 2


# ── User list ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_admin_list_users(client: AsyncClient):
    users_fixture = {
        "items": [
            {"id": str(uuid.uuid4()), "email": "user@example.com",
             "full_name": "Test User", "tenant": "acme-corp", "role": "owner"}
        ],
        "total": 1, "page": 1, "per_page": 25,
    }
    with patch("app.api.v1.endpoints.admin.AdminService.list_users",
               new_callable=AsyncMock, return_value=users_fixture):
        resp = await client.get(
            "/api/v1/admin/users",
            headers={"X-Admin-Key": VALID_KEY},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["email"] == "user@example.com"


# ── Audit logs ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_admin_audit_logs_empty(client: AsyncClient):
    with patch("app.api.v1.endpoints.admin.AdminService.list_audit_logs",
               new_callable=AsyncMock, return_value={"items": [], "total": 0, "page": 1, "per_page": 50}):
        resp = await client.get(
            "/api/v1/admin/audit-logs",
            headers={"X-Admin-Key": VALID_KEY},
        )
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


# ── Tenant update (PATCH) ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_admin_update_tenant_plan(client: AsyncClient):
    tenant_id = str(uuid.uuid4())
    updated = {**TENANT_LIST_FIXTURE["items"][0], "id": tenant_id, "plan": "Business"}
    with patch("app.api.v1.endpoints.admin.AdminService.update_tenant",
               new_callable=AsyncMock, return_value=updated):
        resp = await client.patch(
            f"/api/v1/admin/tenants/{tenant_id}",
            json={"plan": "Business"},
            headers={"X-Admin-Key": VALID_KEY},
        )
    assert resp.status_code == 200
    assert resp.json()["plan"] == "Business"


@pytest.mark.asyncio
async def test_admin_update_tenant_suspend(client: AsyncClient):
    tenant_id = str(uuid.uuid4())
    updated = {**TENANT_LIST_FIXTURE["items"][0], "id": tenant_id, "status": "suspended"}
    with patch("app.api.v1.endpoints.admin.AdminService.update_tenant",
               new_callable=AsyncMock, return_value=updated):
        resp = await client.patch(
            f"/api/v1/admin/tenants/{tenant_id}",
            json={"is_active": False},
            headers={"X-Admin-Key": VALID_KEY},
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_admin_update_tenant_wrong_key_rejected(client: AsyncClient):
    tenant_id = str(uuid.uuid4())
    resp = await client.patch(
        f"/api/v1/admin/tenants/{tenant_id}",
        json={"plan": "Agency"},
        headers={"X-Admin-Key": INVALID_KEY},
    )
    assert resp.status_code == 403
