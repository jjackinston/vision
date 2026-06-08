"""
Tests for /api/v1/tenants/* endpoints

Covers:
- GET  /tenants/current          → returns tenant info
- GET  /tenants/current/members  → returns members with name + email from User JOIN
- POST /tenants/current/invite   → sends invite (JSON body, not query params)
- POST /tenants/current/invite   → rejects when at user limit
- DELETE /tenants/current/members/{id} → removes a non-owner member
- DELETE /tenants/current/members/{id} → cannot remove the workspace owner
- DELETE /tenants/current/members/{id} → unknown id returns 404
- PUT /tenants/current/members/{id}/role → updates role
- PUT /tenants/current/members/{id}/role → rejects invalid role
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from tests.conftest import (
    OWNER_TENANT_ID,
    OWNER_USER_ID,
    TENANT_SLUG,
    make_mock_user,
    seed_tenant,
)


# ── GET /current ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_current_tenant(authed_client: AsyncClient, db_session):
    await seed_tenant(db_session)
    resp = await authed_client.get("/api/v1/tenants/current")
    assert resp.status_code == 200
    data = resp.json()
    assert data["slug"] == TENANT_SLUG


# ── GET /current/members ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_members_returns_owner(authed_client: AsyncClient, db_session):
    """After seed, the owner is the only member and appears in the list."""
    await seed_tenant(db_session)
    resp = await authed_client.get("/api/v1/tenants/current/members")
    assert resp.status_code == 200
    members = resp.json()
    assert len(members) >= 1
    owner = next((m for m in members if m["role"] == "owner"), None)
    assert owner is not None, "Owner should be in member list"


@pytest.mark.asyncio
async def test_list_members_includes_name_and_email(authed_client: AsyncClient, db_session):
    """Each member entry must have name and email populated from the User JOIN."""
    await seed_tenant(db_session)
    resp = await authed_client.get("/api/v1/tenants/current/members")
    assert resp.status_code == 200
    members = resp.json()
    for m in members:
        assert "name" in m, "name field missing"
        assert "email" in m, "email field missing"
        assert "role" in m
        assert "id" in m
        assert "user_id" in m
        assert "joined_at" in m


@pytest.mark.asyncio
async def test_list_members_owner_email(authed_client: AsyncClient, db_session):
    """The seeded owner's email should appear in the member list."""
    await seed_tenant(db_session)
    resp = await authed_client.get("/api/v1/tenants/current/members")
    assert resp.status_code == 200
    emails = [m["email"] for m in resp.json()]
    assert "owner@test.com" in emails


# ── POST /current/invite ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_invite_member_json_body(authed_client: AsyncClient, db_session):
    """Invite via JSON body (not query params) → 200 with status."""
    await seed_tenant(db_session)
    resp = await authed_client.post(
        "/api/v1/tenants/current/invite",
        json={"email": "alice@example.com", "role": "analyst"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "alice@example.com" in data.get("message", "")
    assert data["status"] == "invitation_sent"


@pytest.mark.asyncio
async def test_invite_member_default_role(authed_client: AsyncClient, db_session):
    """Invite without specifying role defaults to analyst."""
    await seed_tenant(db_session)
    resp = await authed_client.post(
        "/api/v1/tenants/current/invite",
        json={"email": "bob@example.com"},
    )
    assert resp.status_code == 200
    assert resp.json()["role"] == "analyst"


@pytest.mark.asyncio
async def test_invite_enforces_user_limit(authed_client: AsyncClient, db_session):
    """Inviting when already at the plan's user limit → 402."""
    from app.models.tenant import Plan, Tenant, TenantMember
    from app.models.user import User

    # Seed tenant with limit=1 user
    plan = Plan(
        id=uuid.uuid4(), name="StarterLimited", price_monthly=Decimal("49.00"),
        limits={"products": 50, "keywords": 500, "api_calls": 10000, "users": 1, "agents": 2},
        features={}, is_active=True,
    )
    db_session.add(plan)
    tenant = Tenant(
        id=uuid.UUID(OWNER_TENANT_ID), slug=TENANT_SLUG,
        name="Limited Tenant", plan_id=plan.id, is_active=True,
    )
    db_session.add(tenant)
    owner_user = User(
        id=uuid.UUID(OWNER_USER_ID), clerk_id="clerk_owner",
        email="owner@test.com", full_name="Owner", is_active=True,
    )
    db_session.add(owner_user)
    db_session.add(TenantMember(tenant_id=tenant.id, user_id=owner_user.id, role="owner"))
    await db_session.commit()

    # Already at limit (1 user = 1 member); invite should fail
    resp = await authed_client.post(
        "/api/v1/tenants/current/invite",
        json={"email": "extra@example.com", "role": "analyst"},
    )
    assert resp.status_code == 402
    assert resp.json()["detail"]["code"] == "LIMIT_REACHED"


# ── DELETE /current/members/{id} ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_remove_member(authed_client: AsyncClient, db_session):
    """Remove a non-owner member → 200, member no longer in list."""
    from app.models.tenant import TenantMember
    from app.models.user import User

    _, tenant, _ = await seed_tenant(db_session)

    # Add a second member to remove
    extra_user = User(
        id=uuid.uuid4(), clerk_id="clerk_extra",
        email="extra@test.com", full_name="Extra User", is_active=True,
    )
    db_session.add(extra_user)
    extra_member = TenantMember(
        tenant_id=tenant.id, user_id=extra_user.id, role="analyst"
    )
    db_session.add(extra_member)
    await db_session.commit()

    member_id = str(extra_member.id)
    resp = await authed_client.delete(f"/api/v1/tenants/current/members/{member_id}")
    assert resp.status_code == 200
    assert resp.json()["removed"] == member_id

    # Should no longer appear in list
    list_resp = await authed_client.get("/api/v1/tenants/current/members")
    ids = [m["id"] for m in list_resp.json()]
    assert member_id not in ids


@pytest.mark.asyncio
async def test_cannot_remove_owner(authed_client: AsyncClient, db_session):
    """Attempting to remove the owner → 403."""
    await seed_tenant(db_session)

    # Find the owner member id
    list_resp = await authed_client.get("/api/v1/tenants/current/members")
    owner = next(m for m in list_resp.json() if m["role"] == "owner")

    resp = await authed_client.delete(f"/api/v1/tenants/current/members/{owner['id']}")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_remove_unknown_member_returns_404(authed_client: AsyncClient, db_session):
    await seed_tenant(db_session)
    fake_id = str(uuid.uuid4())
    resp = await authed_client.delete(f"/api/v1/tenants/current/members/{fake_id}")
    assert resp.status_code == 404


# ── PUT /current/members/{id}/role ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_member_role(authed_client: AsyncClient, db_session):
    from app.models.tenant import TenantMember
    from app.models.user import User

    _, tenant, _ = await seed_tenant(db_session)

    # Add a second member to update
    extra_user = User(
        id=uuid.uuid4(), clerk_id="clerk_role_test",
        email="roletest@test.com", full_name="Role Test", is_active=True,
    )
    db_session.add(extra_user)
    extra_member = TenantMember(
        tenant_id=tenant.id, user_id=extra_user.id, role="analyst"
    )
    db_session.add(extra_member)
    await db_session.commit()

    resp = await authed_client.put(
        f"/api/v1/tenants/current/members/{extra_member.id}/role?role=manager"
    )
    assert resp.status_code == 200
    assert resp.json()["new_role"] == "manager"


@pytest.mark.asyncio
async def test_update_member_role_invalid(authed_client: AsyncClient, db_session):
    from app.models.tenant import TenantMember
    from app.models.user import User

    _, tenant, _ = await seed_tenant(db_session)
    extra_user = User(
        id=uuid.uuid4(), clerk_id="clerk_invalid_role",
        email="invalid@test.com", full_name="Invalid Role", is_active=True,
    )
    db_session.add(extra_user)
    extra_member = TenantMember(tenant_id=tenant.id, user_id=extra_user.id, role="analyst")
    db_session.add(extra_member)
    await db_session.commit()

    resp = await authed_client.put(
        f"/api/v1/tenants/current/members/{extra_member.id}/role?role=superuser"
    )
    assert resp.status_code == 400
