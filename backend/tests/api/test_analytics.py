import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_root_endpoint(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert "SellerVision" in data["name"]


@pytest.mark.asyncio
async def test_ceo_recommendations(client):
    from unittest.mock import patch, AsyncMock
    mock_recs = {
        "date": "2025-06-04",
        "business_score": 72,
        "recommendations": {"actions": [{"action": "Test action", "urgency": "high"}]},
    }
    with patch("app.services.ceo_dashboard_service.CEODashboardService.get_daily_recommendations",
               new_callable=AsyncMock, return_value=mock_recs):
        resp = await client.get("/api/v1/analytics/ceo-recommendations")
    assert resp.status_code == 200
    data = resp.json()
    assert "business_score" in data or "recommendations" in data


@pytest.mark.asyncio
async def test_digital_twin_simulation(client):
    from unittest.mock import patch, AsyncMock
    mock_result = {
        "scenario_type": "price_change",
        "simulation": {"recommendation": "go", "total_6m_profit": 25000},
    }
    with patch("app.services.ceo_dashboard_service.DigitalTwinService.simulate",
               new_callable=AsyncMock, return_value=mock_result):
        resp = await client.post("/api/v1/analytics/simulate", params={
            "scenario_type": "price_change",
            "forecast_months": 6,
        }, json={"change_percent": 10})
    assert resp.status_code in (200, 422)


@pytest.mark.asyncio
async def test_platform_comparison_ordering(client):
    """Platforms should be returned sorted by profitability."""
    resp = await client.get("/api/v1/analytics/platform-comparison", params={
        "product_cost": 8.00,
        "selling_price": 35.00,
        "monthly_units": 200,
        "category": "home",
    })
    assert resp.status_code == 200
    data = resp.json()
    profits = [d["net_profit_monthly"] for d in data]
    assert profits == sorted(profits, reverse=True), "Should be sorted descending by profit"
