import math


class RecommendationEngine:

    def __init__(self, fundamental_report, technical_report):

        self.fundamental = fundamental_report
        self.technical = technical_report

    ############################################################
    # Public API
    ############################################################

    def generate_report(self):

        fundamental_score = self.fundamental.get(
            "fundamental_score", 50
        )

        technical_score = self.technical.get(
            "technical_score", 50
        )

        valuation_score = self._valuation_score()

        momentum_score = self._momentum_score()

        risk_score = self._risk_score()

        overall_score = round(

            (
                fundamental_score * 0.35
                + technical_score * 0.35
                + valuation_score * 0.10
                + momentum_score * 0.10
                + risk_score * 0.10
            )

        )

        recommendation = self._recommendation(overall_score)

        confidence = self._confidence()

        return {

            "overall_score": overall_score,

            "recommendation": recommendation,

            "confidence": confidence,

            "entry_timing": self._entry_timing(),

            "investment_horizon": self._investment_horizon(),

            "risk_level": self._risk_level(),

            "fundamental_score": fundamental_score,

            "technical_score": technical_score,

            "momentum_score": momentum_score,

            "valuation_score": valuation_score,

            "risk_score": risk_score,

            "reasoning": {

                "positives":

                    self.fundamental.get("strengths", [])

                    + self.technical.get("strengths", []),

                "negatives":

                    self.fundamental.get("weaknesses", [])

                    + self.technical.get("weaknesses", [])
            }
        }

    ############################################################
    # Recommendation
    ############################################################

    def _recommendation(self, score):

        if score >= 90:
            return "STRONG BUY"

        if score >= 80:
            return "BUY"

        if score >= 70:
            return "ACCUMULATE"

        if score >= 60:
            return "HOLD"

        if score >= 45:
            return "WAIT FOR PULLBACK"

        if score >= 30:
            return "REDUCE"

        return "SELL"

    ############################################################
    # Valuation
    ############################################################

    def _valuation_score(self):

        metrics = self.fundamental.get("metrics", {})

        pe = metrics.get("Trailing PE", {}).get("value")

        if pe is None:
            return 50

        if pe < 15:
            return 95

        if pe < 20:
            return 85

        if pe < 25:
            return 75

        if pe < 30:
            return 65

        if pe < 40:
            return 55

        return 40

    ############################################################
    # Momentum
    ############################################################

    def _momentum_score(self):

        indicators = self.technical.get(
            "indicators", {}
        )

        rsi = indicators.get(
            "RSI", {}
        ).get(
            "value"
        )

        if rsi is None:
            return 50

        if 45 <= rsi <= 60:
            return 95

        if 35 <= rsi < 45:
            return 80

        if 60 < rsi <= 70:
            return 75

        if 70 < rsi <= 80:
            return 60

        if rsi > 80:
            return 35

        if rsi < 25:
            return 30

        return 50

    ############################################################
    # Risk
    ############################################################

    def _risk_score(self):

        score = 100

        for weakness in self.fundamental.get(
            "weaknesses", []
        ):

            text = weakness.lower()

            if "revenue" in text:
                score -= 10

            if "debt" in text:
                score -= 10

            if "cash flow" in text:
                score -= 12

            if "valuation" in text:
                score -= 8

        for weakness in self.technical.get(
            "weaknesses", []
        ):

            text = weakness.lower()

            if "bearish" in text:
                score -= 12

            if "pullback" in text:
                score -= 8

            if "downtrend" in text:
                score -= 12

            if "overbought" in text:
                score -= 8

        return max(score, 20)

    ############################################################
    # Confidence
    ############################################################

    def _confidence(self):

        f = self.fundamental.get(
            "fundamental_score", 50
        )

        t = self.technical.get(
            "technical_score", 50
        )

        difference = abs(f - t)

        confidence = 100 - difference

        confidence = max(55, confidence)

        confidence = min(98, confidence)

        return confidence

    ############################################################
    # Entry Timing
    ############################################################

    def _entry_timing(self):

        rsi = self.technical.get(
            "indicators", {}
        ).get(
            "RSI", {}
        ).get(
            "value"
        )

        if rsi is None:
            return "Neutral"

        if rsi > 80:
            return "Wait for Pullback"

        if rsi > 70:
            return "Slight Pullback Preferred"

        if rsi < 30:
            return "Good Buying Opportunity"

        return "Good Entry"

    ############################################################
    # Investment Horizon
    ############################################################

    def _investment_horizon(self):

        trend = self.technical.get(
            "indicators", {}
        ).get(
            "Trend", {}
        ).get(
            "classification", ""
        ).lower()

        if "strong bullish" in trend:
            return "Long Term"

        if "bullish" in trend:
            return "Medium Term"

        if "bearish" in trend:
            return "Short Term"

        return "Neutral"

    ############################################################
    # Risk Level
    ############################################################

    def _risk_level(self):

        risk = self._risk_score()

        if risk >= 85:
            return "Low"

        if risk >= 70:
            return "Medium"

        return "High"


    def generate_report(self):

        fundamental_score = self.fundamental.get(
            "fundamental_score", 50
        )

        technical_score = self.technical.get(
            "technical_score", 50
        )

        valuation_score = self._valuation_score()

        momentum_score = self._momentum_score()

        risk_score = self._risk_score()

        overall_score = round(
            (
                fundamental_score * 0.35
                + technical_score * 0.35
                + valuation_score * 0.10
                + momentum_score * 0.10
                + risk_score * 0.10
            )
        )

        recommendation = self._recommendation(overall_score)

        confidence = self._confidence()

        buy_probability = self._buy_probability(
            overall_score,
            confidence
        )

        entry = self._entry_price()

        stop = self._stop_loss(entry)

        target = self._take_profit(entry)

        rr = self._risk_reward(entry, stop, target)

        return {

            "overall_score": overall_score,

            "recommendation": recommendation,

            "buy_probability": buy_probability,

            "confidence": confidence,

            "entry_price": entry,

            "current_price": self._current_price(),

            "stop_loss": stop,

            "take_profit": target,

            "risk_reward": rr,

            "entry_timing": self._entry_timing(),

            "investment_horizon": self._investment_horizon(),

            "risk_level": self._risk_level(),

            "fundamental_score": fundamental_score,

            "technical_score": technical_score,

            "momentum_score": momentum_score,

            "valuation_score": valuation_score,

            "risk_score": risk_score,

            "reasoning": {

                "positives":

                    self.fundamental.get("strengths", [])

                    + self.technical.get("strengths", []),

                "negatives":

                    self.fundamental.get("weaknesses", [])

                    + self.technical.get("weaknesses", [])
            }
        }

    ############################################################
    # Buy Probability
    ############################################################

    def _buy_probability(self, score, confidence):

        probability = (
            score * 0.75 +
            confidence * 0.25
        )

        probability = round(probability)

        probability = max(0, min(100, probability))

        return probability


    ############################################################
    # Current Price
    ############################################################

    def _current_price(self):

        trend = self.technical.get(
            "indicators",
            {}
        ).get(
            "Trend",
            {}
        )

        return trend.get("current_price")


    ############################################################
    # Entry Price
    ############################################################

    def _entry_price(self):

        trend = self.technical.get(
            "indicators",
            {}
        ).get(
            "Trend",
            {}
        )

        price = trend.get("current_price")

        atr = self.technical.get(
            "indicators",
            {}
        ).get(
            "ATR",
            {}
        ).get(
            "value",
            0
        )

        if price is None:

            return None

        return round(price - atr, 2)


    ############################################################
    # Stop Loss
    ############################################################

    def _stop_loss(self, entry):

        if entry is None:

            return None

        atr = self.technical.get(
            "indicators",
            {}
        ).get(
            "ATR",
            {}
        ).get(
            "value",
            0
        )

        return round(entry - atr * 1.5, 2)


    ############################################################
    # Take Profit
    ############################################################

    def _take_profit(self, entry):

        if entry is None:

            return None

        atr = self.technical.get(
            "indicators",
            {}
        ).get(
            "ATR",
            {}
        ).get(
            "value",
            0
        )

        return round(entry + atr * 4, 2)


    ############################################################
    # Risk Reward
    ############################################################

    def _risk_reward(self, entry, stop, target):

        if None in (entry, stop, target):

            return None

        risk = entry - stop

        reward = target - entry

        if risk <= 0:

            return None

        return round(reward / risk, 2)