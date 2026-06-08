"""
Celery background task definitions.
All heavy computation runs here, not in API request handlers.
"""
from celery import Celery
from celery.schedules import crontab
import asyncio
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery(
    "sellervision",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        # Sync inventory every 30 minutes
        "sync-inventory": {
            "task": "app.workers.tasks.sync_all_inventory",
            "schedule": crontab(minute="*/30"),
        },
        # Update product metrics every hour
        "update-product-metrics": {
            "task": "app.workers.tasks.update_all_product_metrics",
            "schedule": crontab(minute=0),
        },
        # Trend detection every 2 hours
        "detect-trends": {
            "task": "app.workers.tasks.run_trend_detection",
            "schedule": crontab(minute=0, hour="*/2"),
        },
        # AI CEO daily recommendations at 6am UTC
        "ceo-daily-recommendations": {
            "task": "app.workers.tasks.generate_ceo_recommendations_all",
            "schedule": crontab(minute=0, hour=6),
        },
        # PPC optimization every 4 hours
        "optimize-ppc": {
            "task": "app.workers.tasks.run_ppc_optimization",
            "schedule": crontab(minute=0, hour="*/4"),
        },
        # Keyword rank tracking daily at 3am
        "track-keyword-ranks": {
            "task": "app.workers.tasks.track_all_keyword_ranks",
            "schedule": crontab(minute=0, hour=3),
        },
        # Competitor monitoring every 6 hours
        "monitor-competitors": {
            "task": "app.workers.tasks.monitor_all_competitors",
            "schedule": crontab(minute=0, hour="*/6"),
        },
    },
)


def run_async(coro):
    """Run async function in sync celery task."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def analyze_product_task(self, product_id: str, tenant_slug: str):
    """Deep AI analysis for a product."""
    try:
        from app.services.ai_product_service import AIProductService
        from app.services.product_service import ProductService
        from app.core.database import tenant_session
        from sqlalchemy import select
        from app.models.product import Product

        async def _run():
            async with tenant_session(tenant_slug) as db:
                service = ProductService(db, tenant_slug)
                ai_service = AIProductService()
                product = await service.get_product(product_id)
                if not product:
                    return
                scores = await ai_service.calculate_opportunity_score(product)
                await service.update_scores(product_id, scores)

        run_async(_run())
        logger.info(f"Analyzed product {product_id}")
    except Exception as exc:
        logger.error(f"Failed to analyze product {product_id}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task
def sync_all_inventory():
    """Sync inventory levels from all connected marketplaces, then push WS alerts."""
    from app.services.tenant_service import get_all_active_tenants
    from app.websocket.publisher import publish_inventory_alert
    from app.services.notification_service import send_stockout_alert

    async def _run():
        from app.core.database import AsyncSessionLocal
        from sqlalchemy import text
        from datetime import datetime, timedelta

        tenants = await get_all_active_tenants()
        for tenant in tenants:
            try:
                # Sync marketplace data
                from app.services.inventory_service import InventoryService
                svc = InventoryService()
                await svc.sync_from_marketplaces(tenant.slug)
            except Exception as e:
                logger.error(f"Inventory sync failed for {tenant.slug}: {e}")

        # After sync: query near-stockout items and push real-time alerts
        try:
            async with AsyncSessionLocal() as db:
                cutoff = datetime.utcnow() + timedelta(days=14)
                result = await db.execute(
                    text("""
                        SELECT
                            i.sku,
                            COALESCE(p.title, i.sku) AS product_name,
                            EXTRACT(DAY FROM (i.stockout_date - NOW()))::int AS days_remaining,
                            i.quantity_on_hand
                        FROM inventory i
                        LEFT JOIN products p ON p.id = i.product_id
                        WHERE i.stockout_date IS NOT NULL
                          AND i.stockout_date <= :cutoff
                          AND i.quantity_on_hand > 0
                        ORDER BY i.stockout_date ASC
                        LIMIT 50
                    """),
                    {"cutoff": cutoff},
                )
                rows = result.fetchall()

            # Publish to Redis → FastAPI WS manager → clients
            # Also persist DB notification for the notification bell
            # (inventory has no tenant_id — broadcast to all tenants for now)
            for row in rows:
                sku, product_name, days_remaining, qty = row
                days_remaining = max(int(days_remaining or 0), 0)
                for tenant in tenants:
                    await publish_inventory_alert(
                        str(tenant.id), str(sku), str(product_name), days_remaining, int(qty or 0)
                    )
                    if days_remaining <= 7:
                        await send_stockout_alert(str(tenant.id), str(product_name), days_remaining)

            if rows:
                logger.info(f"[sync-inventory] Published {len(rows)} stockout alert(s)")
        except Exception as exc:
            logger.warning(f"[sync-inventory] Alert phase failed: {exc}")

    run_async(_run())


@celery_app.task
def update_all_product_metrics():
    """Update BSR, price, review count for all tracked products."""
    from app.services.product_service import bulk_update_metrics
    run_async(bulk_update_metrics())


@celery_app.task
def run_trend_detection():
    """Run trend detection; push WS alert for high-score trends (>=80)."""
    from app.services.trend_service import TrendService
    from app.services.tenant_service import get_all_active_tenants
    from app.websocket.publisher import publish_trend_detected

    async def _run():
        from app.core.database import AsyncSessionLocal
        from sqlalchemy import select
        from app.models.remaining_models import Trend

        service = TrendService()
        await service.run_full_trend_scan()

        # Push WS events for top new trends to all tenants
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Trend).where(Trend.trend_score >= 80).order_by(Trend.trend_score.desc()).limit(10)
            )
            hot_trends = result.scalars().all()

        if hot_trends:
            tenants = await get_all_active_tenants()
            for trend in hot_trends:
                for tenant in tenants:
                    await publish_trend_detected(
                        str(tenant.id),
                        trend.keyword or trend.category or "Unknown",
                        float(trend.trend_score),
                        trend.source or "AI",
                    )
            logger.info(f"[trend-detection] Pushed {len(hot_trends)} hot trend(s)")

    run_async(_run())


@celery_app.task
def generate_ceo_recommendations_all():
    """Generate AI CEO daily recommendations for all tenants."""
    from app.services.ceo_dashboard_service import CEODashboardService
    from app.services.tenant_service import get_all_active_tenants
    from app.services.notification_service import send_notification

    async def _run():
        tenants = await get_all_active_tenants()
        service = CEODashboardService()
        for tenant in tenants:
            try:
                recs = await service.get_daily_recommendations(str(tenant.id))
                await send_notification(
                    tenant_id=str(tenant.id),
                    title="Your AI CEO Daily Briefing is ready",
                    body=f"{len(recs.get('recommendations', {}).get('actions', []))} action items identified",
                    action_url="/dashboard",
                )
            except Exception as e:
                logger.error(f"CEO recs failed for {tenant.slug}: {e}")

    run_async(_run())


@celery_app.task
def run_ppc_optimization():
    """Run PPC optimization for all tenants; push WS alert for high-ACoS campaigns."""
    from app.services.ppc_service import PPCService
    from app.services.tenant_service import get_all_active_tenants
    from app.websocket.publisher import publish_ppc_alert

    async def _run():
        from app.core.database import AsyncSessionLocal
        from sqlalchemy import select
        from app.models.remaining_models import PPCCampaign

        tenants = await get_all_active_tenants()
        for tenant in tenants:
            try:
                async with AsyncSessionLocal() as db:
                    svc = PPCService(db)
                    await svc.run_optimization_cycle(tenant.slug)
                    # Alert on high-ACoS campaigns (>35%)
                    result = await db.execute(
                        select(PPCCampaign.name, PPCCampaign.acos)
                        .where(PPCCampaign.status == "enabled", PPCCampaign.acos > 0.35)
                        .limit(5)
                    )
                    for row in result.fetchall():
                        await publish_ppc_alert(
                            str(tenant.id),
                            row.name or "Campaign",
                            float(row.acos) * 100,
                        )
            except Exception as e:
                logger.error(f"PPC optimization failed for {tenant.slug}: {e}")

    run_async(_run())


@celery_app.task
def track_all_keyword_ranks():
    """Track keyword rankings for all tenants' tracked products."""
    from app.services.keyword_service import KeywordService
    run_async(KeywordService().track_all_ranks())


@celery_app.task
def monitor_all_competitors():
    """Monitor competitor price, stock, and review changes."""
    from app.services.competitor_service import CompetitorService
    run_async(CompetitorService().monitor_all())


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def run_single_agent(self, agent_type: str, task: str, tenant_id: str, run_id: str):
    """Run a single named agent — queued by the /agents/{name}/run endpoint."""
    try:
        from app.agents.agent_system import get_orchestrator, AgentType

        async def _run():
            orchestrator = get_orchestrator(tenant_id)
            try:
                at = AgentType(agent_type)
            except ValueError:
                return {"error": f"Unknown agent type: {agent_type}"}
            return await orchestrator.run_agent(at, {"task": task})

        result = run_async(_run())

        async def _finish():
            from app.core.cache import get_redis
            import json as _json
            from app.websocket.publisher import publish_agent_completed, publish_agent_failed

            findings = result.get("findings_count", 0) if isinstance(result, dict) else 0
            summary = result.get("summary", "") if isinstance(result, dict) else ""
            status = result.get("status", "completed") if isinstance(result, dict) else "completed"
            error = result.get("error", "") if isinstance(result, dict) else str(result)

            # Persist result + status in Redis for polling
            redis = await get_redis()
            if redis:
                await redis.set(
                    f"agent_run:{run_id}",
                    _json.dumps(result, default=str),
                    ex=86400,
                )
                await redis.set(
                    f"agent_status:{tenant_id}:{agent_type}",
                    _json.dumps({
                        "status": status,
                        "last_run": result.get("completed_at") if isinstance(result, dict) else None,
                        "findings": findings,
                    }),
                    ex=3600,
                )

            # Push real-time WS event via Redis pub/sub → FastAPI process
            if "error" in (result or {}):
                await publish_agent_failed(tenant_id, agent_type, run_id, error)
            else:
                await publish_agent_completed(
                    tenant_id, agent_type, run_id,
                    findings_count=findings,
                    summary=summary,
                )

        run_async(_finish())
        logger.info(f"Agent {agent_type} run {run_id} completed: {result.get('status') if isinstance(result, dict) else 'done'}")
        return result
    except Exception as exc:
        logger.error(f"Agent {agent_type} run {run_id} failed: {exc}")
        # Publish failure event before retrying
        async def _fail():
            from app.websocket.publisher import publish_agent_failed
            await publish_agent_failed(tenant_id, agent_type, run_id, str(exc))
        run_async(_fail())
        raise self.retry(exc=exc)


@celery_app.task
def run_all_agents_task(tenant_id: str):
    """Run all 7 agents in parallel for a tenant — can be triggered on-demand."""
    from app.agents.agent_system import get_orchestrator

    async def _run():
        orchestrator = get_orchestrator(tenant_id)
        return await orchestrator.run_all_agents()

    result = run_async(_run())
    logger.info(f"All agents completed for tenant {tenant_id}: {result.get('total_findings')} findings")
    return result


@celery_app.task
def generate_ai_ceo_action_plan(tenant_id: str):
    """Generate fresh AI CEO action plan on demand."""
    from app.services.ceo_dashboard_service import CEODashboardService

    async def _run():
        service = CEODashboardService()
        return await service.get_daily_recommendations(tenant_id)

    return run_async(_run())


@celery_app.task
def process_marketplace_purchase(asset_id: str, user_id: str, tenant_id: str):
    """Process a marketplace asset purchase and provision it."""
    from app.services.marketplace_service import MarketplaceService

    async def _run():
        from app.core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            service = MarketplaceService(db, tenant_id)
            return await service.purchase_asset(asset_id, user_id)

    return run_async(_run())
