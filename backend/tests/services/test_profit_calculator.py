import pytest
from app.services.profit_calculator import ProfitCalculator


@pytest.fixture
def calc():
    return ProfitCalculator()


def test_amazon_fees_calculated(calc):
    result = calc.calculate({
        "marketplace": "amazon",
        "selling_price": 30.00,
        "product_cost": 5.00,
        "monthly_units": 100,
    })
    assert result["marketplace"] == "amazon"
    assert result["net_profit_per_unit"] > 0
    fees = result["fees_breakdown"]
    assert "referral" in fees
    assert "fba_fulfillment" in fees
    assert fees["total_per_unit"] > 0


def test_amazon_roi_positive(calc):
    result = calc.calculate({
        "marketplace": "amazon",
        "selling_price": 29.99,
        "product_cost": 5.00,
        "monthly_units": 100,
    })
    assert result["roi_percent"] > 100  # 5x product cost should yield >100% ROI


def test_break_even_calculation(calc):
    result = calc.calculate({
        "marketplace": "amazon",
        "selling_price": 20.00,
        "product_cost": 8.00,
        "monthly_units": 50,
        "ad_spend_daily": 10,
    })
    assert "break_even_units_monthly" in result
    assert result["break_even_units_monthly"] >= 0


def test_platform_comparison_sorted(calc):
    results = calc.compare_platforms(5.00, 29.99, 100)
    assert len(results) > 0
    profits = [r["net_profit_monthly"] for r in results]
    assert profits == sorted(profits, reverse=True)


def test_tiktok_lower_fees(calc):
    """TikTok has lower referral rate (6%) vs Amazon (15%)."""
    amazon = calc.calculate({"marketplace": "amazon", "selling_price": 30.00, "product_cost": 0.00})
    tiktok = calc.calculate({"marketplace": "tiktok", "selling_price": 30.00, "product_cost": 0.00})
    assert tiktok["fees_breakdown"]["total_per_unit"] < amazon["fees_breakdown"]["total_per_unit"]


def test_negative_profit_when_too_low_margin(calc):
    result = calc.calculate({
        "marketplace": "amazon",
        "selling_price": 8.00,
        "product_cost": 7.00,
        "ad_spend_daily": 20,
        "monthly_units": 10,
    })
    assert result["net_profit_per_unit"] < 0


def test_etsy_fees_include_listing(calc):
    result = calc.calculate({
        "marketplace": "etsy",
        "selling_price": 25.00,
        "product_cost": 5.00,
        "monthly_units": 30,
    })
    fees = result["fees_breakdown"]
    assert "listing_fee" in fees
    assert fees["listing_fee"] == 0.20


def test_shopify_no_fba_fee(calc):
    result = calc.calculate({
        "marketplace": "shopify",
        "selling_price": 49.99,
        "product_cost": 10.00,
        "monthly_units": 50,
    })
    fees = result["fees_breakdown"]
    assert "fba_fulfillment" not in fees
    assert "payment_processing" in fees


def test_annual_projection(calc):
    result = calc.calculate({
        "marketplace": "amazon",
        "selling_price": 29.99,
        "product_cost": 5.00,
        "monthly_units": 200,
    })
    monthly = result["net_profit_monthly"]
    annual = result["annual_net_profit_projection"]
    assert abs(annual - monthly * 12) < 0.01
