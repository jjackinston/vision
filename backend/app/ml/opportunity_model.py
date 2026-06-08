"""
SellerVision AI — ML Models
Scikit-learn + feature engineering for product opportunity scoring.
These models supplement LLM analysis with fast, deterministic predictions.
"""
import numpy as np
import pickle
import os
from typing import Optional
from dataclasses import dataclass
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import logging

logger = logging.getLogger(__name__)
MODEL_DIR = os.path.join(os.path.dirname(__file__), "saved_models")
os.makedirs(MODEL_DIR, exist_ok=True)


@dataclass
class ProductFeatures:
    """Extracted features for ML model input."""
    monthly_searches: float = 0
    search_trend_30d: float = 0          # % change
    review_count: float = 0
    review_rating: float = 0
    seller_count: float = 0
    price: float = 0
    bsr_rank: float = 0                  # normalized 0-1 (lower is better)
    estimated_monthly_revenue: float = 0
    cpc: float = 0
    listing_quality_score: float = 0
    image_count: float = 0
    has_aplus: float = 0                 # 0 or 1
    category_growth_rate: float = 0
    seasonal_factor: float = 1.0
    days_on_market: float = 0


class OpportunityScorer:
    """
    Fast ML-based opportunity scoring.
    Trained on historical product performance data.
    Falls back to heuristic scoring when no trained model exists.
    """

    def __init__(self):
        self.model_path = os.path.join(MODEL_DIR, "opportunity_scorer.pkl")
        self.scaler_path = os.path.join(MODEL_DIR, "opportunity_scaler.pkl")
        self._model: Optional[Pipeline] = None
        self._load_or_create()

    def _load_or_create(self):
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    self._model = pickle.load(f)
                logger.info("Loaded trained opportunity scorer")
                return
            except Exception as e:
                logger.warning(f"Could not load model: {e}")
        # Create untrained model — will use heuristic fallback until trained
        self._model = None

    def _extract_feature_vector(self, features: ProductFeatures) -> np.ndarray:
        """Convert ProductFeatures to numpy array for model input."""
        return np.array([[
            np.log1p(features.monthly_searches),
            features.search_trend_30d / 100,
            np.log1p(features.review_count),
            features.review_rating / 5.0,
            np.log1p(features.seller_count),
            np.log1p(features.price),
            1.0 - min(features.bsr_rank, 1.0),   # invert: lower BSR = better
            np.log1p(features.estimated_monthly_revenue),
            features.cpc,
            features.listing_quality_score / 100,
            features.image_count / 9.0,
            features.has_aplus,
            features.category_growth_rate / 100,
            features.seasonal_factor,
            np.log1p(features.days_on_market),
        ]])

    def predict_opportunity_score(self, features: ProductFeatures) -> float:
        """Returns opportunity score 0-100."""
        if self._model is not None:
            try:
                X = self._extract_feature_vector(features)
                return float(np.clip(self._model.predict(X)[0], 0, 100))
            except Exception as e:
                logger.warning(f"Model prediction failed, using heuristic: {e}")
        return self._heuristic_score(features)

    def _heuristic_score(self, f: ProductFeatures) -> float:
        """
        Rule-based scoring when model isn't trained.
        Weighted combination of demand, competition, and profitability signals.
        """
        score = 50.0

        # Demand signal (0-25 pts)
        demand = min(np.log1p(f.monthly_searches) / np.log1p(500000), 1.0)
        score += demand * 25

        # Competition penalty (0-20 pts)
        if f.seller_count > 0:
            competition_penalty = min(np.log1p(f.seller_count) / np.log1p(200), 1.0) * 20
            score -= competition_penalty

        # Review saturation penalty (0-15 pts)
        if f.review_count > 1000:
            review_penalty = min((f.review_count - 1000) / 10000, 1.0) * 15
            score -= review_penalty

        # Trend bonus (0-10 pts)
        if f.search_trend_30d > 0:
            score += min(f.search_trend_30d / 50, 1.0) * 10

        # Revenue signal (0-10 pts)
        revenue_signal = min(np.log1p(f.estimated_monthly_revenue) / np.log1p(100000), 1.0)
        score += revenue_signal * 10

        return float(np.clip(score, 0, 100))

    def predict_sales_30d(self, features: ProductFeatures, current_rank: int) -> int:
        """Estimate 30-day unit sales from BSR using category-specific curves."""
        # Amazon BSR → Sales estimator (simplified curve for Home & Kitchen)
        if current_rank <= 0:
            return 0
        if current_rank <= 100:
            return int(np.random.uniform(800, 2000))
        elif current_rank <= 1000:
            return int(3000 / np.sqrt(current_rank / 100))
        elif current_rank <= 10000:
            return int(300 / np.sqrt(current_rank / 1000))
        elif current_rank <= 100000:
            return int(30 / np.sqrt(current_rank / 10000))
        else:
            return int(max(1, 5 / np.sqrt(current_rank / 100000)))

    def train(self, X: np.ndarray, y: np.ndarray):
        """Train on historical product data. Call when labeled data is available."""
        model = Pipeline([
            ("scaler", StandardScaler()),
            ("gbr", GradientBoostingRegressor(
                n_estimators=200, max_depth=5, learning_rate=0.05,
                subsample=0.8, random_state=42
            )),
        ])
        model.fit(X, y)
        self._model = model
        with open(self.model_path, "wb") as f:
            pickle.dump(model, f)
        logger.info(f"Trained opportunity scorer on {len(X)} samples")


class StockoutPredictor:
    """Predicts days until stockout using sales velocity + seasonality."""

    def predict_days_until_stockout(
        self,
        quantity_on_hand: int,
        avg_daily_sales: float,
        lead_time_days: int = 30,
        safety_stock_days: int = 7,
    ) -> dict:
        if avg_daily_sales <= 0:
            return {"days_until_stockout": 999, "stockout_date": None, "reorder_qty": 0, "urgency": "healthy"}

        days_remaining = quantity_on_hand / avg_daily_sales
        days_to_order = days_remaining - lead_time_days - safety_stock_days

        # Recommended reorder quantity (90-day supply)
        reorder_qty = max(int(avg_daily_sales * 90), 50)

        from datetime import date, timedelta
        stockout_date = date.today() + timedelta(days=int(days_remaining))

        return {
            "days_until_stockout": int(days_remaining),
            "days_until_must_order": int(days_to_order),
            "stockout_date": stockout_date.isoformat(),
            "reorder_qty_recommended": reorder_qty,
            "urgency": (
                "critical" if days_remaining <= 14
                else "warning" if days_remaining <= 30
                else "healthy"
            ),
            "avg_daily_sales": round(avg_daily_sales, 2),
        }


class PricingOptimizer:
    """Recommends optimal price points based on competition and demand elasticity."""

    def recommend_price(
        self,
        current_price: float,
        competitor_prices: list[float],
        review_rating: float,
        review_count: int,
        marketplace: str = "amazon",
    ) -> dict:
        if not competitor_prices:
            return {"recommended_price": current_price, "reasoning": "No competitor data"}

        avg_comp = float(np.mean(competitor_prices))
        median_comp = float(np.median(competitor_prices))
        min_comp = float(np.min(competitor_prices))
        max_comp = float(np.max(competitor_prices))

        # Quality premium based on rating
        quality_premium = 1.0
        if review_rating >= 4.5 and review_count >= 100:
            quality_premium = 1.08
        elif review_rating >= 4.0 and review_count >= 50:
            quality_premium = 1.04
        elif review_rating < 3.5:
            quality_premium = 0.95

        # Recommended at median with quality adjustment, but never below min
        recommended = max(median_comp * quality_premium, min_comp * 1.02)

        # Price ceiling: max + 15% premium cap
        recommended = min(recommended, max_comp * 1.15)

        return {
            "recommended_price": round(recommended, 2),
            "current_price": current_price,
            "change_amount": round(recommended - current_price, 2),
            "change_percent": round((recommended - current_price) / current_price * 100, 1),
            "competitor_avg": round(avg_comp, 2),
            "competitor_median": round(median_comp, 2),
            "price_range": f"${min_comp:.2f} – ${max_comp:.2f}",
            "strategy": (
                "penetration" if recommended < avg_comp
                else "premium" if recommended > avg_comp * 1.05
                else "competitive"
            ),
            "reasoning": (
                f"Median competitor price is ${median_comp:.2f}. "
                f"{'Quality premium applied (+{:.0f}%)'.format((quality_premium-1)*100) if quality_premium > 1.0 else 'Standard competitive pricing recommended.'}"
            ),
        }


# Module-level singletons
opportunity_scorer = OpportunityScorer()
stockout_predictor = StockoutPredictor()
pricing_optimizer = PricingOptimizer()
