from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    products,
    keywords,
    competitors,
    inventory,
    suppliers,
    listings,
    analytics,
    agents,
    trends,
    ppc,
    automation,
    marketplace,
    billing,
    tenants,
    users,
    integrations,
    webhooks,
    notifications,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["Tenants"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(keywords.router, prefix="/keywords", tags=["Keywords"])
api_router.include_router(competitors.router, prefix="/competitors", tags=["Competitors"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
api_router.include_router(suppliers.router, prefix="/suppliers", tags=["Suppliers"])
api_router.include_router(listings.router, prefix="/listings", tags=["Listings"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(agents.router, prefix="/agents", tags=["AI Agents"])
api_router.include_router(trends.router, prefix="/trends", tags=["Trends"])
api_router.include_router(ppc.router, prefix="/ppc", tags=["PPC"])
api_router.include_router(automation.router, prefix="/automation", tags=["Automation"])
api_router.include_router(marketplace.router, prefix="/marketplace", tags=["Marketplace"])
api_router.include_router(billing.router, prefix="/billing", tags=["Billing"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["Integrations"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
