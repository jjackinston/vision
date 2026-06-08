"""
SellerVision AI — Transactional Email Service (Resend)
======================================================
All sends are fire-and-forget via asyncio.create_task() so they never
block request handling. Failures are logged but not raised to callers.

Emails sent:
  welcome              → new user signs up (Clerk user.created webhook)
  billing_receipt      → checkout completed (Stripe checkout.session.completed)
  subscription_cancelled → plan cancelled (Stripe customer.subscription.deleted)
  low_stock_alert      → item nearing stockout (stockout background loop)
  trial_ending         → 3 days before 14-day trial expires (Celery beat)
"""
import asyncio
import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

# ── Brand constants ────────────────────────────────────────────────────
_BRAND_COLOR  = "#7C3AED"   # violet-600
_BRAND_DARK   = "#4C1D95"   # violet-900
_LOGO_TEXT    = "SellerVision AI"
_UNSUBSCRIBE  = f"{settings.FRONTEND_URL}/settings?tab=notifications"


# ── Base HTML wrapper ──────────────────────────────────────────────────
def _wrap(title: str, body: str, preview: str = "") -> str:
    """Wrap email body HTML in a consistent branded shell."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <meta name="x-apple-disable-message-reformatting" />
  <!--[if !mso]><!--><style>
    body {{ margin:0; padding:0; background:#f4f4f7; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif; }}
    .wrapper {{ max-width:600px; margin:0 auto; padding:32px 16px; }}
    .card {{ background:#ffffff; border-radius:12px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,.08); }}
    .header {{ background:linear-gradient(135deg,{_BRAND_COLOR},{_BRAND_DARK}); padding:28px 32px; }}
    .header-logo {{ color:#ffffff; font-size:20px; font-weight:700; letter-spacing:-0.3px; text-decoration:none; }}
    .header-tag {{ color:rgba(255,255,255,.65); font-size:12px; margin-top:2px; }}
    .body {{ padding:32px; }}
    .footer {{ padding:20px 32px 28px; }}
    h1 {{ margin:0 0 8px; font-size:22px; color:#111827; font-weight:700; }}
    p  {{ margin:0 0 16px; font-size:15px; color:#374151; line-height:1.6; }}
    .btn {{ display:inline-block; padding:12px 24px; background:{_BRAND_COLOR}; color:#ffffff !important;
            border-radius:8px; font-size:15px; font-weight:600; text-decoration:none; margin:8px 0; }}
    .btn-outline {{ background:#ffffff; color:{_BRAND_COLOR} !important; border:2px solid {_BRAND_COLOR}; }}
    .divider {{ border:none; border-top:1px solid #e5e7eb; margin:24px 0; }}
    .kv-row {{ display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid #f3f4f6; font-size:14px; }}
    .kv-label {{ color:#6b7280; }}
    .kv-value {{ color:#111827; font-weight:600; }}
    .badge {{ display:inline-block; padding:3px 10px; border-radius:99px; font-size:12px; font-weight:600; }}
    .badge-green  {{ background:#d1fae5; color:#065f46; }}
    .badge-amber  {{ background:#fef3c7; color:#92400e; }}
    .badge-red    {{ background:#fee2e2; color:#991b1b; }}
    .footnote {{ font-size:12px; color:#9ca3af; line-height:1.6; }}
  </style><!--<![endif]-->
</head>
<body>
  {"<span style='display:none;max-height:0;overflow:hidden;'>" + preview + "&nbsp;" * 80 + "</span>" if preview else ""}
  <div class="wrapper">
    <div class="card">
      <div class="header">
        <div class="header-logo">{_LOGO_TEXT}</div>
        <div class="header-tag">AI-Powered E-Commerce Intelligence</div>
      </div>
      <div class="body">
        {body}
      </div>
      <div class="footer">
        <hr class="divider" />
        <p class="footnote">
          You're receiving this because you have an account at SellerVision AI.<br />
          <a href="{_UNSUBSCRIBE}" style="color:{_BRAND_COLOR};">Manage email preferences</a>
          &nbsp;·&nbsp;
          <a href="{settings.FRONTEND_URL}" style="color:{_BRAND_COLOR};">Go to Dashboard</a>
        </p>
      </div>
    </div>
  </div>
</body>
</html>"""


# ── Individual templates ───────────────────────────────────────────────
def _tpl_welcome(first_name: str) -> str:
    name = first_name or "there"
    return _wrap(
        title=f"Welcome to {_LOGO_TEXT}!",
        preview=f"Your AI-powered e-commerce intelligence platform is ready.",
        body=f"""
<h1>Welcome, {name}! 👋</h1>
<p>Your account is set up and ready to go. Here's what you can do right now:</p>
<table width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td style="padding:10px 0;vertical-align:top;width:32px;font-size:20px;">🔍</td>
    <td style="padding:10px 0 10px 8px;font-size:14px;color:#374151;">
      <strong>Discover products</strong> — Find high-opportunity items with AI scoring
    </td>
  </tr>
  <tr>
    <td style="padding:10px 0;vertical-align:top;width:32px;font-size:20px;">📊</td>
    <td style="padding:10px 0 10px 8px;font-size:14px;color:#374151;">
      <strong>Track competitors</strong> — Monitor pricing, BSR, and reviews automatically
    </td>
  </tr>
  <tr>
    <td style="padding:10px 0;vertical-align:top;width:32px;font-size:20px;">🤖</td>
    <td style="padding:10px 0 10px 8px;font-size:14px;color:#374151;">
      <strong>Deploy AI agents</strong> — Automate research, pricing, and listing optimisation
    </td>
  </tr>
  <tr>
    <td style="padding:10px 0;vertical-align:top;width:32px;font-size:20px;">📦</td>
    <td style="padding:10px 0 10px 8px;font-size:14px;color:#374151;">
      <strong>Manage inventory</strong> — Get stockout alerts before you run out
    </td>
  </tr>
</table>
<p style="margin-top:24px;">
  <a href="{settings.FRONTEND_URL}/onboarding" class="btn">Complete Your Setup →</a>
</p>
<p style="font-size:13px;color:#6b7280;">
  Your 14-day free trial is now active — no credit card needed yet.
  Need help? Reply to this email and our team will get back to you.
</p>
""",
    )


def _tpl_billing_receipt(
    first_name: str,
    plan_name: str,
    amount: str,
    period_end: str,
    invoice_url: Optional[str],
) -> str:
    name = first_name or "there"
    return _wrap(
        title=f"Your {_LOGO_TEXT} receipt",
        preview=f"Receipt for {plan_name} — {amount}",
        body=f"""
<h1>Payment confirmed ✓</h1>
<p>Thanks {name}, your <strong>{plan_name}</strong> subscription is now active.</p>

<div style="background:#f9fafb;border-radius:8px;padding:20px;margin:20px 0;">
  <div class="kv-row">
    <span class="kv-label">Plan</span>
    <span class="kv-value">{plan_name}</span>
  </div>
  <div class="kv-row">
    <span class="kv-label">Amount charged</span>
    <span class="kv-value">{amount}</span>
  </div>
  <div class="kv-row" style="border-bottom:none;">
    <span class="kv-label">Next billing date</span>
    <span class="kv-value">{period_end}</span>
  </div>
</div>

{"<p><a href='" + invoice_url + "' class='btn btn-outline'>View Invoice</a></p>" if invoice_url else ""}

<p>
  <a href="{settings.FRONTEND_URL}/dashboard" class="btn">Go to Dashboard →</a>
</p>
<p style="font-size:13px;color:#6b7280;">
  To manage your subscription, cancel, or change plans visit
  <a href="{settings.FRONTEND_URL}/settings?tab=billing" style="color:{_BRAND_COLOR};">Settings → Billing</a>.
</p>
""",
    )


def _tpl_subscription_cancelled(
    first_name: str,
    plan_name: str,
    access_until: str,
) -> str:
    name = first_name or "there"
    return _wrap(
        title=f"Your {_LOGO_TEXT} subscription has been cancelled",
        preview=f"Your {plan_name} subscription was cancelled.",
        body=f"""
<h1>Subscription cancelled</h1>
<p>Hi {name},</p>
<p>
  Your <strong>{plan_name}</strong> subscription has been cancelled.
  You'll keep full access to all features until <strong>{access_until}</strong>,
  after which your account will move to a read-only free tier.
</p>

<div style="background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;padding:16px;margin:20px 0;">
  <p style="margin:0;font-size:14px;color:#92400e;">
    <strong>Changed your mind?</strong> You can reactivate your subscription at any time
    from Settings → Billing before {access_until}.
  </p>
</div>

<p>
  <a href="{settings.FRONTEND_URL}/settings?tab=billing" class="btn">Reactivate Subscription</a>
</p>
<p style="font-size:13px;color:#6b7280;">
  We'd love to know what we could have done better.
  <a href="mailto:{settings.EMAIL_REPLY_TO}?subject=Cancellation feedback" style="color:{_BRAND_COLOR};">
    Share your feedback →
  </a>
</p>
""",
    )


def _tpl_low_stock(
    items: list[dict],
) -> str:
    """items: list of {product_name, sku, qty_on_hand, days_remaining, action_url}"""
    rows = ""
    for item in items[:5]:  # cap at 5 items per email
        severity = "badge-red" if item["days_remaining"] <= 7 else "badge-amber"
        label    = f"{item['days_remaining']}d left" if item["days_remaining"] > 0 else "OUT OF STOCK"
        rows += f"""
        <tr>
          <td style="padding:12px 8px 12px 0;font-size:14px;color:#111827;border-bottom:1px solid #f3f4f6;">
            <strong>{item['product_name'][:50]}</strong><br/>
            <span style="color:#9ca3af;font-size:12px;">SKU: {item['sku']}</span>
          </td>
          <td style="padding:12px 8px;text-align:center;font-size:14px;border-bottom:1px solid #f3f4f6;">
            {item['qty_on_hand']} units
          </td>
          <td style="padding:12px 0 12px 8px;text-align:right;border-bottom:1px solid #f3f4f6;">
            <span class="badge {severity}">{label}</span>
          </td>
        </tr>"""

    more = f"<p style='font-size:13px;color:#6b7280;'>+{len(items)-5} more items need attention.</p>" if len(items) > 5 else ""
    return _wrap(
        title="⚠️ Low stock alert — action needed",
        preview=f"{len(items)} product(s) are running low on inventory.",
        body=f"""
<h1>⚠️ Low stock alert</h1>
<p>
  The following products are running low and may stock out soon.
  Reorder now to avoid losing the buy box.
</p>

<table width="100%" cellpadding="0" cellspacing="0" style="margin:16px 0;">
  <thead>
    <tr>
      <th style="text-align:left;font-size:12px;color:#6b7280;padding-bottom:8px;border-bottom:2px solid #e5e7eb;">PRODUCT</th>
      <th style="text-align:center;font-size:12px;color:#6b7280;padding-bottom:8px;border-bottom:2px solid #e5e7eb;">QTY</th>
      <th style="text-align:right;font-size:12px;color:#6b7280;padding-bottom:8px;border-bottom:2px solid #e5e7eb;">STATUS</th>
    </tr>
  </thead>
  <tbody>{rows}</tbody>
</table>
{more}
<p style="margin-top:20px;">
  <a href="{settings.FRONTEND_URL}/inventory" class="btn">View Inventory Dashboard →</a>
</p>
""",
    )


def _tpl_trial_ending(
    first_name: str,
    days_remaining: int,
    trial_end_date: str,
) -> str:
    name = first_name or "there"
    urgency = "Your trial ends tomorrow!" if days_remaining <= 1 else f"Your trial ends in {days_remaining} days"
    return _wrap(
        title=f"{urgency} — SellerVision AI",
        preview=f"{urgency} Subscribe now to keep your data and automations.",
        body=f"""
<h1>{urgency}</h1>
<p>Hi {name},</p>
<p>
  Your free trial ends on <strong>{trial_end_date}</strong>.
  After that, your account will move to read-only mode and your AI agents will pause.
</p>

<div style="background:#f5f3ff;border:1px solid #ddd6fe;border-radius:8px;padding:16px 20px;margin:20px 0;">
  <p style="margin:0 0 8px;font-weight:600;color:#4c1d95;">What you'll keep with a paid plan:</p>
  <ul style="margin:0;padding-left:20px;color:#374151;font-size:14px;line-height:2;">
    <li>All your tracked products and keyword rankings</li>
    <li>Live AI agents running 24/7</li>
    <li>Competitor monitoring and price alerts</li>
    <li>Full inventory management with stockout alerts</li>
  </ul>
</div>

<p>
  <a href="{settings.FRONTEND_URL}/settings?tab=billing" class="btn">Subscribe Now — from $49/mo →</a>
</p>
<p style="font-size:13px;color:#6b7280;">
  Questions about plans?
  <a href="mailto:{settings.EMAIL_REPLY_TO}" style="color:{_BRAND_COLOR};">Email us</a>
  — we're happy to help.
</p>
""",
    )


# ── EmailService ───────────────────────────────────────────────────────
def _resend_configured() -> bool:
    key = settings.RESEND_API_KEY or ""
    return bool(key) and key not in ("re_...", "") and len(key) > 10


async def _send_async(to: str | list[str], subject: str, html: str) -> None:
    """
    Send via Resend. Called from asyncio.create_task() — never raises.
    Uses run_in_executor so the blocking Resend SDK call doesn't block the event loop.
    """
    if not _resend_configured():
        logger.debug("Email skipped (RESEND_API_KEY not set): %s", subject)
        return
    try:
        import resend as _resend
        import asyncio
        _resend.api_key = settings.RESEND_API_KEY
        recipients = [to] if isinstance(to, str) else to

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: _resend.Emails.send({
                "from": settings.EMAIL_FROM,
                "reply_to": settings.EMAIL_REPLY_TO,
                "to": recipients,
                "subject": subject,
                "html": html,
            }),
        )
        logger.info("Email sent: %s → %s", subject, recipients)
    except Exception as exc:
        logger.warning("Email send failed (%s): %s", subject, exc)


def send_nowait(to: str | list[str], subject: str, html: str) -> None:
    """Fire-and-forget wrapper — creates an asyncio task, never blocks."""
    asyncio.create_task(_send_async(to, subject, html))


class EmailService:
    """
    Thin wrapper that builds and dispatches transactional emails.
    All methods are fire-and-forget — they schedule the send and return
    immediately. Errors are logged, never raised.
    """

    @staticmethod
    def send_welcome(to: str, first_name: str) -> None:
        """Triggered by Clerk user.created webhook."""
        send_nowait(
            to=to,
            subject=f"Welcome to {_LOGO_TEXT} 🚀",
            html=_tpl_welcome(first_name),
        )

    @staticmethod
    def send_billing_receipt(
        to: str,
        first_name: str,
        plan_name: str,
        amount_cents: int,
        period_end_ts: int,
        invoice_url: Optional[str] = None,
    ) -> None:
        """Triggered by Stripe checkout.session.completed webhook."""
        from datetime import datetime, timezone
        amount = f"${amount_cents / 100:.2f}"
        period_end = datetime.fromtimestamp(period_end_ts, tz=timezone.utc).strftime("%B %d, %Y")
        send_nowait(
            to=to,
            subject=f"Your {_LOGO_TEXT} receipt — {plan_name} {amount}",
            html=_tpl_billing_receipt(first_name, plan_name, amount, period_end, invoice_url),
        )

    @staticmethod
    def send_subscription_cancelled(
        to: str,
        first_name: str,
        plan_name: str,
        access_until_ts: int,
    ) -> None:
        """Triggered by Stripe customer.subscription.deleted webhook."""
        from datetime import datetime, timezone
        access_until = datetime.fromtimestamp(access_until_ts, tz=timezone.utc).strftime("%B %d, %Y")
        send_nowait(
            to=to,
            subject=f"Your {_LOGO_TEXT} subscription has been cancelled",
            html=_tpl_subscription_cancelled(first_name, plan_name, access_until),
        )

    @staticmethod
    def send_low_stock_alert(
        to: str | list[str],
        items: list[dict],
    ) -> None:
        """
        Triggered by the stockout background loop in main.py.
        items: list of {product_name, sku, qty_on_hand, days_remaining}
        """
        if not items:
            return
        count = len(items)
        subject = (
            f"⚠️ {items[0]['product_name'][:40]} is running low"
            if count == 1
            else f"⚠️ {count} products need restocking — SellerVision AI"
        )
        send_nowait(to=to, subject=subject, html=_tpl_low_stock(items))

    @staticmethod
    def send_trial_ending(
        to: str,
        first_name: str,
        days_remaining: int,
        trial_end_ts: int,
    ) -> None:
        """Called by Celery beat task: fire at 3 days and 1 day before trial ends."""
        from datetime import datetime, timezone
        trial_end_date = datetime.fromtimestamp(trial_end_ts, tz=timezone.utc).strftime("%B %d, %Y")
        send_nowait(
            to=to,
            subject=(
                "⏰ Your SellerVision AI trial ends tomorrow"
                if days_remaining <= 1
                else f"⏰ {days_remaining} days left in your SellerVision AI trial"
            ),
            html=_tpl_trial_ending(first_name, days_remaining, trial_end_date),
        )
