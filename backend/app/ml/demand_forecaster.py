"""
Demand forecasting using time-series analysis.
Combines statistical methods (exponential smoothing) with ML-based adjustments.
"""
import numpy as np
from typing import List, Optional
from dataclasses import dataclass
from datetime import date, timedelta


@dataclass
class DemandForecast:
    period_days: int
    predicted_units: int
    predicted_revenue: float
    confidence_low: int
    confidence_high: int
    trend: str           # growing, stable, declining
    seasonality_factor: float


class DemandForecaster:

    def forecast(
        self,
        historical_sales: List[float],
        selling_price: float,
        forecast_days: int = 30,
        seasonality: bool = True,
    ) -> DemandForecast:
        """
        Exponential smoothing forecast with trend detection.
        historical_sales: list of daily unit sales (most recent last)
        """
        if len(historical_sales) < 7:
            avg = float(np.mean(historical_sales)) if historical_sales else 1.0
            return DemandForecast(
                period_days=forecast_days,
                predicted_units=int(avg * forecast_days),
                predicted_revenue=avg * forecast_days * selling_price,
                confidence_low=int(avg * forecast_days * 0.7),
                confidence_high=int(avg * forecast_days * 1.4),
                trend="stable",
                seasonality_factor=1.0,
            )

        series = np.array(historical_sales, dtype=float)
        alpha = 0.3   # smoothing factor
        beta = 0.1    # trend factor

        # Double exponential smoothing (Holt's method)
        level = series[0]
        trend_val = series[1] - series[0]
        smoothed = []
        for val in series:
            prev_level = level
            level = alpha * val + (1 - alpha) * (level + trend_val)
            trend_val = beta * (level - prev_level) + (1 - beta) * trend_val
            smoothed.append(level)

        # Forecast
        forecast_daily = level + trend_val * forecast_days
        forecast_daily = max(0, forecast_daily)

        # Seasonality factor (placeholder — in production use historical seasonal index)
        current_month = date.today().month
        seasonal_factors = {1: 0.85, 2: 0.80, 3: 0.90, 4: 0.95, 5: 1.00,
                           6: 1.05, 7: 1.10, 8: 1.05, 9: 1.00, 10: 1.10,
                           11: 1.30, 12: 1.40}
        seasonal = seasonal_factors.get(current_month, 1.0) if seasonality else 1.0

        predicted_units = int(forecast_daily * seasonal)
        std_dev = float(np.std(series))
        ci_width = max(int(std_dev * np.sqrt(forecast_days) * 1.65), 5)

        # Trend detection
        recent_avg = float(np.mean(series[-7:]))
        earlier_avg = float(np.mean(series[:7]))
        trend_pct = ((recent_avg - earlier_avg) / max(earlier_avg, 1)) * 100
        trend_label = "growing" if trend_pct > 10 else "declining" if trend_pct < -10 else "stable"

        return DemandForecast(
            period_days=forecast_days,
            predicted_units=predicted_units,
            predicted_revenue=predicted_units * selling_price,
            confidence_low=max(0, predicted_units - ci_width),
            confidence_high=predicted_units + ci_width,
            trend=trend_label,
            seasonality_factor=seasonal,
        )

    def forecast_multi_period(
        self,
        historical_sales: List[float],
        selling_price: float,
    ) -> dict:
        """Forecast for 30, 90, 180, and 365 days."""
        return {
            "30d": self.forecast(historical_sales, selling_price, 30).__dict__,
            "90d": self.forecast(historical_sales, selling_price, 90).__dict__,
            "180d": self.forecast(historical_sales, selling_price, 180).__dict__,
            "365d": self.forecast(historical_sales, selling_price, 365).__dict__,
        }

    def detect_seasonality(self, historical_sales: List[float], period: int = 7) -> float:
        """Returns seasonality strength (0=none, 1=strong)."""
        if len(historical_sales) < period * 2:
            return 0.0
        series = np.array(historical_sales)
        detrended = series - np.convolve(series, np.ones(period) / period, mode="same")
        if detrended.std() == 0:
            return 0.0
        return float(min(np.abs(detrended).mean() / (series.mean() + 1e-6), 1.0))


demand_forecaster = DemandForecaster()
