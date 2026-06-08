#!/usr/bin/env python3
"""
SellerVision AI — Stripe Product & Price Setup
================================================
Creates all 4 subscription products + monthly prices in your Stripe account.
Run ONCE after getting your Stripe API key.

Usage:
    python backend/scripts/setup_stripe_products.py --key sk_test_...

    # Or set env var first:
    export STRIPE_SECRET_KEY=sk_test_...
    python backend/scripts/setup_stripe_products.py

Output:
    Prints the 4 price IDs to paste into backend/.env.production
    and frontend/.env.production.
"""
import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Create SellerVision Stripe products and prices")
    parser.add_argument("--key", help="Stripe secret key (or set STRIPE_SECRET_KEY env var)")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Confirm you want to create LIVE mode products (not test mode)",
    )
    args = parser.parse_args()

    api_key = args.key or os.environ.get("STRIPE_SECRET_KEY", "")
    if not api_key:
        print("ERROR: Provide --key sk_test_... or set STRIPE_SECRET_KEY env var")
        sys.exit(1)

    if api_key.startswith("sk_live_") and not args.live:
        print(
            "ERROR: You passed a LIVE key but did not pass --live.\n"
            "Add --live to confirm you want to create live-mode products."
        )
        sys.exit(1)

    try:
        import stripe
    except ImportError:
        print("stripe not installed. Run: pip install stripe")
        sys.exit(1)

    stripe.api_key = api_key
    mode = "LIVE" if api_key.startswith("sk_live_") else "TEST"
    print(f"\n{'='*60}")
    print(f"  SellerVision AI — Stripe Setup ({mode} mode)")
    print(f"{'='*60}\n")

    PLANS = [
        {
            "key": "starter",
            "name": "Starter",
            "description": "For solo sellers getting started. 50 products, 500 keywords, 2 AI agents.",
            "price_cents": 4900,          # $49/month
            "env_var": "STRIPE_STARTER_PRICE_ID",
        },
        {
            "key": "professional",
            "name": "Professional",
            "description": "For growing sellers. 100 products, 5,000 keywords, 5 AI agents.",
            "price_cents": 14900,         # $149/month
            "env_var": "STRIPE_PROFESSIONAL_PRICE_ID",
        },
        {
            "key": "business",
            "name": "Business",
            "description": "For established brands. 500 products, 25,000 keywords, 7 AI agents.",
            "price_cents": 29900,         # $299/month
            "env_var": "STRIPE_BUSINESS_PRICE_ID",
        },
        {
            "key": "agency",
            "name": "Agency",
            "description": "For agencies and power sellers. Unlimited products & keywords, 7 AI agents, 25 users.",
            "price_cents": 59900,         # $599/month
            "env_var": "STRIPE_AGENCY_PRICE_ID",
        },
    ]

    results = {}

    for plan in PLANS:
        print(f"→ Creating product: {plan['name']}...")

        # Check if product already exists (idempotent by metadata tag)
        existing = stripe.Product.search(
            query=f"metadata['sellervision_plan']:'{plan['key']}'"
        )
        if existing.data:
            product = existing.data[0]
            print(f"  ✓ Product already exists: {product.id}")
        else:
            product = stripe.Product.create(
                name=f"SellerVision AI — {plan['name']}",
                description=plan["description"],
                metadata={"sellervision_plan": plan["key"]},
            )
            print(f"  ✓ Product created: {product.id}")

        # Check if price already exists for this product
        existing_prices = stripe.Price.list(product=product.id, active=True, limit=10)
        monthly_price = None
        for p in existing_prices.data:
            if (
                p.recurring
                and p.recurring.interval == "month"
                and p.recurring.interval_count == 1
                and p.unit_amount == plan["price_cents"]
                and p.currency == "usd"
            ):
                monthly_price = p
                break

        if monthly_price:
            print(f"  ✓ Price already exists: {monthly_price.id}  (${plan['price_cents']//100}/mo)")
        else:
            monthly_price = stripe.Price.create(
                product=product.id,
                unit_amount=plan["price_cents"],
                currency="usd",
                recurring={"interval": "month"},
                metadata={"sellervision_plan": plan["key"]},
            )
            print(f"  ✓ Price created: {monthly_price.id}  (${plan['price_cents']//100}/mo)")

        results[plan["env_var"]] = monthly_price.id

    # ── Print the env vars to copy ──────────────────────────────
    print(f"\n{'='*60}")
    print("  Copy these into backend/.env.production")
    print(f"  AND frontend/.env.production (for the checkout page)")
    print(f"{'='*60}\n")
    for env_var, price_id in results.items():
        print(f"{env_var}={price_id}")

    print(f"\n{'='*60}")
    print("  Also add the Stripe publishable key (pk_test_... / pk_live_...)")
    print("  to frontend/.env.production as:")
    print("  NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_...")
    print(f"{'='*60}\n")
    print("Done! All 4 products and prices are ready in Stripe.")


if __name__ == "__main__":
    main()
