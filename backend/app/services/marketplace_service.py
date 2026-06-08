"""Module 23: SellerVision Marketplace — asset purchase, install, and monetization."""
import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.core.config import settings
stripe.api_key = settings.STRIPE_SECRET_KEY


class MarketplaceService:
    def __init__(self, db: AsyncSession, tenant_slug: str):
        self.db = db
        self.tenant_slug = tenant_slug

    async def purchase_asset(self, asset_id: str, user_id: str) -> dict:
        from app.models.remaining_models import MarketplaceAsset
        result = await self.db.execute(
            select(MarketplaceAsset).where(MarketplaceAsset.id == asset_id)
        )
        asset = result.scalar_one_or_none()
        if not asset:
            raise ValueError("Asset not found")

        if float(asset.price or 0) == 0:
            # Free asset — install directly
            return await self._install_asset(asset, user_id)

        # Paid asset — create Stripe checkout
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": asset.name, "description": asset.description or ""},
                    "unit_amount": int(float(asset.price) * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{settings.CORS_ORIGINS[0]}/marketplace?purchased={asset_id}",
            cancel_url=f"{settings.CORS_ORIGINS[0]}/marketplace",
            metadata={"asset_id": asset_id, "user_id": user_id},
        )
        return {"checkout_url": session.url, "asset_id": asset_id}

    async def _install_asset(self, asset: any, user_id: str) -> dict:
        """Install a purchased/free asset into the user's workspace."""
        from app.models.remaining_models import MarketplaceAsset
        # Increment download count
        await self.db.execute(
            update(MarketplaceAsset).where(MarketplaceAsset.id == asset.id)
            .values(downloads=MarketplaceAsset.downloads + 1)
        )
        await self.db.commit()

        asset_type = asset.type
        asset_data = asset.asset_data

        if asset_type == "dashboard":
            return {"installed": True, "type": "dashboard", "config": asset_data, "message": f"Dashboard '{asset.name}' added to your workspace"}
        elif asset_type == "automation":
            # Create workflow from template
            from app.models.remaining_models import Workflow
            wf = Workflow(
                name=asset.name,
                description=asset.description,
                trigger_type=asset_data.get("trigger"),
                steps=asset_data.get("steps", []),
                is_active=False,  # User must activate
            )
            self.db.add(wf)
            await self.db.commit()
            return {"installed": True, "type": "automation", "workflow_id": str(wf.id), "message": f"Automation '{asset.name}' added (disabled by default)"}
        elif asset_type == "prompt":
            return {"installed": True, "type": "prompt", "prompts": asset_data.get("prompts", []), "message": f"Prompt pack '{asset.name}' added"}
        elif asset_type == "agent":
            return {"installed": True, "type": "agent", "config": asset_data, "message": f"Agent config '{asset.name}' installed"}
        else:
            return {"installed": True, "type": asset_type, "data": asset_data}

    async def rate_asset(self, asset_id: str, user_id: str, rating: float, review: str = None) -> dict:
        from app.models.remaining_models import MarketplaceAsset
        result = await self.db.execute(select(MarketplaceAsset).where(MarketplaceAsset.id == asset_id))
        asset = result.scalar_one_or_none()
        if not asset:
            raise ValueError("Asset not found")
        # Update rolling average
        current_count = asset.rating_count or 0
        current_rating = float(asset.rating or 0)
        new_count = current_count + 1
        new_rating = (current_rating * current_count + rating) / new_count
        await self.db.execute(
            update(MarketplaceAsset).where(MarketplaceAsset.id == asset_id)
            .values(rating=round(new_rating, 2), rating_count=new_count)
        )
        await self.db.commit()
        return {"rated": True, "new_rating": round(new_rating, 2), "review_count": new_count}

    async def get_creator_earnings(self, creator_id: str) -> dict:
        """Calculate creator revenue from asset sales."""
        from app.models.remaining_models import MarketplaceAsset
        result = await self.db.execute(
            select(MarketplaceAsset).where(MarketplaceAsset.creator_id == creator_id)
        )
        assets = result.scalars().all()
        total_downloads = sum(a.downloads or 0 for a in assets)
        total_revenue = sum(float(a.price or 0) * (a.downloads or 0) for a in assets)
        platform_cut = total_revenue * 0.30
        creator_earnings = total_revenue * 0.70
        return {
            "total_assets": len(assets),
            "total_downloads": total_downloads,
            "gross_revenue": round(total_revenue, 2),
            "platform_fee": round(platform_cut, 2),
            "net_earnings": round(creator_earnings, 2),
            "assets": [{"name": a.name, "downloads": a.downloads, "revenue": float(a.price or 0) * (a.downloads or 0)} for a in assets],
        }
