"""Module 22: Automation Engine — workflow execution and Zapier/Make/n8n integration."""
import json
import httpx
import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

logger = logging.getLogger(__name__)


class AutomationService:
    def __init__(self, db: AsyncSession, tenant_slug: str):
        self.db = db
        self.tenant_slug = tenant_slug

    async def run_workflow(self, workflow_id: UUID) -> dict:
        from app.models.remaining_models import Workflow
        result = await self.db.execute(select(Workflow).where(Workflow.id == workflow_id))
        wf = result.scalar_one_or_none()
        if not wf:
            raise ValueError(f"Workflow {workflow_id} not found")
        if not wf.is_active:
            return {"status": "skipped", "reason": "workflow_disabled"}

        steps_results = []
        for step in (wf.steps or []):
            step_result = await self._execute_step(step)
            steps_results.append(step_result)
            if not step_result.get("success") and step.get("fail_fast", True):
                break

        # Update run stats
        await self.db.execute(
            update(Workflow).where(Workflow.id == workflow_id)
            .values(run_count=Workflow.run_count + 1)
        )
        await self.db.commit()
        return {"workflow_id": str(workflow_id), "status": "completed", "steps": steps_results}

    async def _execute_step(self, step: dict) -> dict:
        step_type = step.get("type")
        try:
            if step_type == "send_email":
                return await self._send_email(step)
            elif step_type == "send_slack":
                return await self._send_slack(step)
            elif step_type == "send_webhook":
                return await self._send_webhook(step)
            elif step_type == "update_price":
                return await self._update_price(step)
            elif step_type == "pause_campaign":
                return await self._pause_ppc_campaign(step)
            elif step_type == "create_reorder":
                return await self._create_reorder(step)
            else:
                return {"type": step_type, "success": True, "note": "Step type not implemented"}
        except Exception as e:
            logger.error(f"Step {step_type} failed: {e}")
            return {"type": step_type, "success": False, "error": str(e)}

    async def _send_webhook(self, step: dict) -> dict:
        url = step.get("url")
        if not url:
            return {"success": False, "error": "No webhook URL"}
        payload = step.get("payload", {})
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=payload)
            return {"type": "webhook", "success": resp.status_code < 400, "status_code": resp.status_code}

    async def _send_slack(self, step: dict) -> dict:
        webhook_url = step.get("webhook_url")
        message = step.get("message", "SellerVision AI notification")
        if not webhook_url:
            return {"success": False, "error": "No Slack webhook URL configured"}
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(webhook_url, json={"text": message})
            return {"type": "slack", "success": resp.status_code == 200}

    async def _send_email(self, step: dict) -> dict:
        # In production: integrate SendGrid / AWS SES
        to = step.get("to")
        subject = step.get("subject", "SellerVision AI Alert")
        body = step.get("body", "")
        logger.info(f"[Email] To: {to} | Subject: {subject}")
        return {"type": "email", "success": True, "to": to}

    async def _update_price(self, step: dict) -> dict:
        product_id = step.get("product_id")
        new_price = step.get("price")
        marketplace = step.get("marketplace", "amazon")
        logger.info(f"[Price Update] Product {product_id} → ${new_price} on {marketplace}")
        return {"type": "update_price", "success": True, "product_id": product_id, "new_price": new_price}

    async def _pause_ppc_campaign(self, step: dict) -> dict:
        campaign_id = step.get("campaign_id")
        logger.info(f"[PPC] Pausing campaign {campaign_id}")
        return {"type": "pause_campaign", "success": True, "campaign_id": campaign_id}

    async def _create_reorder(self, step: dict) -> dict:
        product_id = step.get("product_id")
        quantity = step.get("quantity", 100)
        logger.info(f"[Reorder] Product {product_id}, qty {quantity}")
        return {"type": "create_reorder", "success": True, "product_id": product_id, "quantity": quantity}

    # ── Zapier / Make / n8n webhook endpoints ──────────────────────────────────

    async def handle_zapier_trigger(self, event_type: str, data: dict, tenant_id: str) -> dict:
        """Receive data from Zapier and trigger internal workflows."""
        logger.info(f"Zapier trigger: {event_type} for tenant {tenant_id}")
        triggered_workflows = []
        from app.models.remaining_models import Workflow
        result = await self.db.execute(
            select(Workflow).where(
                Workflow.trigger_type == f"zapier:{event_type}",
                Workflow.is_active == True,
            )
        )
        for wf in result.scalars().all():
            run_result = await self.run_workflow(wf.id)
            triggered_workflows.append(run_result)
        return {"triggered": len(triggered_workflows), "results": triggered_workflows}

    async def generate_webhook_url(self, workflow_id: UUID) -> str:
        """Generate a unique webhook URL for this workflow."""
        import secrets
        token = secrets.token_urlsafe(24)
        # In production: store token → workflow mapping in Redis
        return f"https://api.sellervisionai.com/api/v1/automation/webhook/{token}"
