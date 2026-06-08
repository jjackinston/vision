from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user, CurrentUser, generate_api_key

router = APIRouter()


@router.get("/me")
async def get_me(user: CurrentUser = Depends(get_current_user)):
    return {"user_id": user.user_id, "tenant_id": user.tenant_id, "role": user.role}


@router.post("/api-keys")
async def create_api_key(
    name: str,
    scopes: list[str] = [],
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    user.require("admin")
    raw, prefix, hashed = generate_api_key()
    from app.models.tenant import APIKey
    key = APIKey(
        tenant_id=user.tenant_id,
        user_id=user.user_id,
        name=name,
        key_hash=hashed,
        key_prefix=prefix,
        scopes=scopes,
    )
    db.add(key)
    await db.commit()
    return {"key": raw, "prefix": prefix, "name": name, "warning": "Store this key — it won't be shown again."}


@router.get("/api-keys")
async def list_api_keys(
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    from sqlalchemy import select
    from app.models.tenant import APIKey
    result = await db.execute(
        select(APIKey.id, APIKey.name, APIKey.key_prefix, APIKey.scopes, APIKey.last_used_at, APIKey.created_at)
        .where(APIKey.tenant_id == user.tenant_id, APIKey.is_active == True)
    )
    return result.fetchall()


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    user.require("admin")
    from sqlalchemy import update
    from app.models.tenant import APIKey
    await db.execute(
        update(APIKey).where(APIKey.id == key_id, APIKey.tenant_id == user.tenant_id)
        .values(is_active=False)
    )
    await db.commit()
    return {"revoked": key_id}
