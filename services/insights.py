"""Small, data-derived earnings summaries for the chat interface."""

import math
import threading
import time

_CACHE_SECONDS = 300
_cache = {}
_cache_lock = threading.Lock()


def _safe_float(value):
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def get_stock_insights(ticker):
    """Fetch only the quote and recent quarterly revenue needed by the card."""
    import yfinance as yf

    symbol = ticker.upper()
    now = time.monotonic()
    with _cache_lock:
        cached = _cache.get(symbol)
        if cached and now - cached[0] < _CACHE_SECONDS:
            return dict(cached[1])

    stock = yf.Ticker(symbol)
    try:
        info = stock.info or {}
    except Exception:
        info = {}
    try:
        income = stock.quarterly_income_stmt
    except Exception:
        income = None

    latest_revenue = previous_revenue = None
    growth = None
    try:
        if income is not None and not income.empty and "Total Revenue" in income.index:
            revenues = income.loc["Total Revenue"]
            if len(revenues):
                latest_revenue = _safe_float(revenues.iloc[0])
            if len(revenues) > 1:
                previous_revenue = _safe_float(revenues.iloc[1])
            if latest_revenue is not None and previous_revenue:
                growth = (latest_revenue - previous_revenue) / abs(previous_revenue) * 100
    except Exception:
        pass

    margin = _safe_float(info.get("profitMargins"))
    yearly_change = _safe_float(info.get("52WeekChange"))
    beta = _safe_float(info.get("beta"))
    pe = _safe_float(info.get("trailingPE"))
    current_price = _safe_float(info.get("currentPrice") or info.get("regularMarketPrice"))
    currency = info.get("currency")
    company_profile = {
        "sector": info.get("sector"),
        "industry": info.get("industry"),
    }
    financial_metrics = {
        "current_price": current_price,
        "currency": currency,
        "market_cap": _safe_float(info.get("marketCap")),
        "trailing_pe": pe,
        "forward_pe": _safe_float(info.get("forwardPE")),
        "earnings_per_share": _safe_float(info.get("trailingEps")),
        "profit_margin_percent": margin * 100 if margin is not None else None,
        "beta": beta,
        "change_over_52_weeks_percent": yearly_change * 100 if yearly_change is not None else None,
        "dividend_yield_percent": (
            _safe_float(info.get("dividendYield")) * 100
            if _safe_float(info.get("dividendYield")) is not None else None
        ),
    }
    score = 0
    if growth is not None:
        score += 2 if growth >= 5 else (-2 if growth < 0 else 0)
    if margin is not None:
        score += 1 if margin >= 0.15 else (-1 if margin < 0.05 else 0)
    if yearly_change is not None:
        score += 1 if yearly_change > 0.10 else (-1 if yearly_change < -0.15 else 0)
    recommendation = str(info.get("recommendationKey") or "").lower()
    if recommendation in {"strong_buy", "buy"}:
        score += 1
    elif recommendation in {"sell", "strong_sell", "underperform"}:
        score -= 1

    if score >= 3:
        sentiment, tone, outlook = "Bullish", "positive", "Positive"
    elif score >= 1:
        sentiment, tone, outlook = "Slightly Bullish", "positive", "Constructive"
    elif score <= -3:
        sentiment, tone, outlook = "Bearish", "negative", "Cautious"
    elif score <= -1:
        sentiment, tone, outlook = "Slightly Bearish", "negative", "Neutral to Cautious"
    else:
        sentiment, tone, outlook = "Neutral", "neutral", "Neutral"

    risks = []
    if growth is not None and growth < 0:
        risks.append("Revenue contraction")
    elif growth is not None and growth < 5:
        risks.append("Slowing revenue growth")
    if margin is not None and margin < 0.10:
        risks.append("Margin pressure")
    if pe is not None and pe > 40:
        risks.append("Elevated valuation")
    if beta is not None and beta > 1.5:
        risks.append("High share-price volatility")
    if yearly_change is not None and yearly_change < -0.15:
        risks.append("Weak 12-month price momentum")
    if recommendation in {"sell", "strong_sell", "underperform"}:
        risks.append("Negative analyst consensus")
    if not risks:
        risks.append("No major risks surfaced in the available data")

    if latest_revenue is None:
        revenue_value = "Unavailable"
    elif abs(latest_revenue) >= 1_000_000_000:
        revenue_value = f"${latest_revenue / 1_000_000_000:.2f}B"
    elif abs(latest_revenue) >= 1_000_000:
        revenue_value = f"${latest_revenue / 1_000_000:.1f}M"
    else:
        revenue_value = f"${latest_revenue:,.0f}"

    growth_text = f"{growth:+.1f}% QoQ" if growth is not None else "Growth unavailable"
    insight = {
        "company": info.get("longName") or info.get("shortName") or symbol,
        "ticker": symbol,
        "profile": company_profile,
        "financial_metrics": financial_metrics,
        "sentiment": sentiment,
        "sentiment_tone": tone,
        "revenue": {"value": revenue_value, "qoq": growth_text, "growth_percent": growth},
        "risk_factors": risks,
        "outlook": outlook,
        "recommendation": recommendation.replace("_", " ").title() or "Unavailable",
        "confidence": None,
        "price": current_price,
    }
    with _cache_lock:
        _cache[symbol] = (time.monotonic(), insight)
    return dict(insight)
