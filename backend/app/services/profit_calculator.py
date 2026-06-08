"""
Module 17: Multi-Platform Profit Calculator
Calculates net profit, ROI, break-even across all marketplaces.
"""
from dataclasses import dataclass
from typing import Optional

# Platform fee structures (updated 2025)
PLATFORM_FEES = {
    "amazon": {
        "referral_percent": 0.15,   # varies by category
        "fba_per_unit": 3.22,       # average, size-dependent
        "storage_per_unit_monthly": 0.75,
        "closing_fee": 0.0,
    },
    "walmart": {
        "referral_percent": 0.15,
        "fulfillment_per_unit": 3.45,
        "storage_per_unit_monthly": 0.60,
        "closing_fee": 0.0,
    },
    "ebay": {
        "referral_percent": 0.1325,
        "listing_fee": 0.35,
        "paypal_fee_percent": 0.0299,
        "paypal_fee_fixed": 0.49,
    },
    "shopify": {
        "transaction_fee_percent": 0.02,  # Basic plan
        "payment_fee_percent": 0.026,
        "payment_fee_fixed": 0.30,
        "monthly_divided_per_unit": 0.0,  # amortized
    },
    "tiktok": {
        "referral_percent": 0.06,  # TikTok promo rates
        "fulfillment_per_unit": 0.0,  # seller fulfilled
    },
    "etsy": {
        "listing_fee": 0.20,
        "transaction_fee_percent": 0.065,
        "payment_processing_percent": 0.03,
        "payment_processing_fixed": 0.25,
    },
}

CATEGORY_REFERRAL_OVERRIDES = {
    "amazon": {
        "electronics": 0.08,
        "clothing": 0.17,
        "jewelry": 0.20,
        "books": 0.15,
        "toys": 0.15,
        "home": 0.15,
        "sports": 0.15,
        "beauty": 0.08,
        "grocery": 0.08,
    }
}


class ProfitCalculator:

    def calculate(self, params: dict) -> dict:
        marketplace = params.get("marketplace", "amazon")
        selling_price = float(params.get("selling_price", 0))
        product_cost = float(params.get("product_cost", 0))
        shipping_to_warehouse = float(params.get("shipping_cost", 0))
        ad_spend_daily = float(params.get("ad_spend_daily", 0))
        monthly_units = int(params.get("monthly_units", 0))
        category = params.get("category", "home")
        storage_months = float(params.get("storage_months", 3))

        fees = self._calculate_platform_fees(
            marketplace, selling_price, category, monthly_units, storage_months
        )
        ad_cost_per_unit = (ad_spend_daily * 30 / monthly_units) if monthly_units > 0 else 0
        total_ad_monthly = ad_spend_daily * 30

        cogs_per_unit = product_cost + shipping_to_warehouse
        total_fees_per_unit = fees["total_per_unit"]
        total_cost_per_unit = cogs_per_unit + total_fees_per_unit + ad_cost_per_unit

        gross_profit_per_unit = selling_price - cogs_per_unit
        net_profit_per_unit = selling_price - total_cost_per_unit
        net_profit_monthly = net_profit_per_unit * monthly_units

        roi_percent = (net_profit_per_unit / cogs_per_unit * 100) if cogs_per_unit > 0 else 0
        margin_percent = (net_profit_per_unit / selling_price * 100) if selling_price > 0 else 0

        # Break-even units per month
        fixed_monthly_costs = total_ad_monthly + fees.get("monthly_fixed", 0)
        contribution_margin = selling_price - cogs_per_unit - fees.get("variable_per_unit", 0)
        break_even_units = int(fixed_monthly_costs / contribution_margin) if contribution_margin > 0 else 0

        return {
            "marketplace": marketplace,
            "selling_price": selling_price,
            "product_cost": product_cost,
            "shipping_cost": shipping_to_warehouse,
            "fees_breakdown": fees,
            "ad_cost_per_unit": round(ad_cost_per_unit, 2),
            "total_cost_per_unit": round(total_cost_per_unit, 2),
            "gross_profit_per_unit": round(gross_profit_per_unit, 2),
            "net_profit_per_unit": round(net_profit_per_unit, 2),
            "net_profit_monthly": round(net_profit_monthly, 2),
            "roi_percent": round(roi_percent, 1),
            "margin_percent": round(margin_percent, 1),
            "break_even_units_monthly": break_even_units,
            "monthly_units": monthly_units,
            "annual_net_profit_projection": round(net_profit_monthly * 12, 2),
        }

    def _calculate_platform_fees(
        self, marketplace: str, price: float, category: str, units: int, storage_months: float
    ) -> dict:
        fees = PLATFORM_FEES.get(marketplace, {})
        breakdown = {}

        if marketplace == "amazon":
            referral_pct = CATEGORY_REFERRAL_OVERRIDES["amazon"].get(category, fees["referral_percent"])
            referral = price * referral_pct
            fba = fees["fba_per_unit"]
            storage = fees["storage_per_unit_monthly"] * storage_months
            breakdown = {"referral": round(referral, 4), "fba_fulfillment": fba, "storage": round(storage, 4)}
            total = referral + fba + storage

        elif marketplace == "walmart":
            referral = price * fees["referral_percent"]
            fulfillment = fees["fulfillment_per_unit"]
            storage = fees["storage_per_unit_monthly"] * storage_months
            breakdown = {"referral": round(referral, 4), "fulfillment": fulfillment, "storage": round(storage, 4)}
            total = referral + fulfillment + storage

        elif marketplace == "ebay":
            referral = price * fees["referral_percent"]
            listing = fees["listing_fee"]
            payment = price * fees["paypal_fee_percent"] + fees["paypal_fee_fixed"]
            breakdown = {"final_value_fee": round(referral, 4), "listing_fee": listing, "payment_processing": round(payment, 4)}
            total = referral + listing + payment

        elif marketplace == "shopify":
            transaction = price * fees["transaction_fee_percent"]
            payment = price * fees["payment_fee_percent"] + fees["payment_fee_fixed"]
            breakdown = {"transaction_fee": round(transaction, 4), "payment_processing": round(payment, 4)}
            total = transaction + payment

        elif marketplace == "tiktok":
            referral = price * fees["referral_percent"]
            breakdown = {"commission": round(referral, 4)}
            total = referral

        elif marketplace == "etsy":
            listing = fees["listing_fee"]
            transaction = price * fees["transaction_fee_percent"]
            payment = price * fees["payment_processing_percent"] + fees["payment_processing_fixed"]
            breakdown = {"listing_fee": listing, "transaction_fee": round(transaction, 4), "payment_processing": round(payment, 4)}
            total = listing + transaction + payment

        else:
            total = price * 0.15
            breakdown = {"estimated_fees": round(total, 4)}

        return {
            **breakdown,
            "total_per_unit": round(total, 4),
            "variable_per_unit": round(total, 4),
            "monthly_fixed": 0.0,
        }

    def compare_platforms(self, product_cost: float, price: float, monthly_units: int, category: str = "home") -> list:
        """Compare profitability across all platforms."""
        results = []
        for marketplace in PLATFORM_FEES.keys():
            result = self.calculate({
                "marketplace": marketplace,
                "selling_price": price,
                "product_cost": product_cost,
                "monthly_units": monthly_units,
                "category": category,
            })
            results.append({
                "marketplace": marketplace,
                "net_profit_monthly": result["net_profit_monthly"],
                "roi_percent": result["roi_percent"],
                "margin_percent": result["margin_percent"],
                "fees_total": result["fees_breakdown"]["total_per_unit"],
            })
        return sorted(results, key=lambda x: x["net_profit_monthly"], reverse=True)
