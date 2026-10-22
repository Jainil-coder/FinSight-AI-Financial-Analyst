import numpy as np
import pandas as pd


class TechnicalAnalyzer:

    """
    Technical Analysis Engine

    Part 1

    ✓ Moving Averages
    ✓ RSI
    ✓ MACD
    ✓ Trend Detection
    """

    ###############################################################
    # Constructor
    ###############################################################

    def __init__(self, market_snapshot):

        self.category_scores = {
    "Trend": None,
    "Momentum": None,
    "Volatility": None,
    "Volume": None,
    "Structure": None
}
        self.indicators = {}

        self.signals = []

        self.strengths = []

        self.weaknesses = []


        self.market = market_snapshot
        self.history = market_snapshot["history"].copy()

    ###############################################################
    # Helper
    ###############################################################

    def latest(self, column):

        if column in self.history.columns:

            return float(self.history[column].iloc[-1])

        return None

    ###############################################################
    # Simple Moving Average
    ###############################################################

    def calculate_sma(self, period):

        column = f"SMA_{period}"

        self.history[column] = (

            self.history["Close"]

            .rolling(period)

            .mean()

        )

        return column

    ###############################################################
    # Exponential Moving Average
    ###############################################################

    def calculate_ema(self, period):

        column = f"EMA_{period}"

        self.history[column] = (

            self.history["Close"]

            .ewm(

                span=period,

                adjust=False

            )

            .mean()

        )

        return column

    ###############################################################
    # Relative Strength Index
    ###############################################################

    def calculate_rsi(self, period=14):

        delta = self.history["Close"].diff()

        gain = delta.clip(lower=0)

        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(period).mean()

        avg_loss = loss.rolling(period).mean()

        rs = avg_gain / avg_loss

        rsi = 100 - (100 / (1 + rs))

        self.history["RSI"] = rsi

        return "RSI"

    ###############################################################
    # MACD
    ###############################################################

    def calculate_macd(self):

        ema12 = (

            self.history["Close"]

            .ewm(span=12, adjust=False)

            .mean()

        )

        ema26 = (

            self.history["Close"]

            .ewm(span=26, adjust=False)

            .mean()

        )

        macd = ema12 - ema26

        signal = macd.ewm(

            span=9,

            adjust=False

        ).mean()

        histogram = macd - signal

        self.history["MACD"] = macd

        self.history["MACD_SIGNAL"] = signal

        self.history["MACD_HIST"] = histogram

    ###############################################################
    # Moving Average Analysis
    ###############################################################

    def analyze_moving_averages(self):

        # Calculate all moving averages
        self.calculate_sma(50)
        self.calculate_sma(200)

        self.calculate_ema(20)
        self.calculate_ema(50)
        self.calculate_ema(200)

        # Latest values
        current_price = self.latest("Close")

        ema20 = self.latest("EMA_20")
        ema50 = self.latest("EMA_50")
        ema200 = self.latest("EMA_200")

        sma50 = self.latest("SMA_50")
        sma200 = self.latest("SMA_200")

        trend_score = 0

        trend = "Unknown"

        signal = ""

        # ----------------------------------------------------------
        # Determine Trend
        # ----------------------------------------------------------

        if current_price > ema20 > ema50 > ema200:

            trend = "Strong Bullish"

            trend_score = 95

            signal = "Price > EMA20 > EMA50 > EMA200"

            self.strengths.append(
                "Strong long-term bullish trend"
            )

        elif current_price > ema20 > ema50:

            trend = "Bullish"

            trend_score = 80

            signal = "Price above EMA20 and EMA50"

            self.strengths.append(
                "Bullish short-to-medium term trend"
            )

        elif current_price > ema20:

            trend = "Weak Bullish"

            trend_score = 65

            signal = "Price above EMA20"

        elif current_price < ema20 < ema50 < ema200:

            trend = "Strong Bearish"

            trend_score = 20

            signal = "Price < EMA20 < EMA50 < EMA200"

            self.weaknesses.append(
                "Strong long-term bearish trend"
            )

        elif current_price < ema20 < ema50:

            trend = "Bearish"

            trend_score = 35

            signal = "Price below EMA20 and EMA50"

            self.weaknesses.append(
                "Bearish short-term trend"
            )

        else:

            trend = "Sideways"

            trend_score = 50

            signal = "Mixed moving averages"

        # ----------------------------------------------------------
        # Long-Term Confirmation
        # ----------------------------------------------------------

        if sma50 is not None and sma200 is not None:

            if sma50 > sma200:

                self.signals.append(
                    "Golden Cross (SMA50 > SMA200)"
                )

            elif sma50 < sma200:

                self.signals.append(
                    "Death Cross (SMA50 < SMA200)"
                )

        # ----------------------------------------------------------
        # Store Category Score
        # ----------------------------------------------------------

        self.category_scores["Trend"] = trend_score

        # ----------------------------------------------------------
        # Store Indicator Details
        # ----------------------------------------------------------

        self.indicators["Trend"] = {

            "classification": trend,

            "score": trend_score,

            "signal": signal,

            "current_price": round(current_price, 2),

            "ema20": round(ema20, 2),

            "ema50": round(ema50, 2),

            "ema200": round(ema200, 2),

            "sma50": round(sma50, 2) if sma50 else None,

            "sma200": round(sma200, 2) if sma200 else None,

            "description": (
                "Trend is determined using the relationship "
                "between the current price and the 20, 50 and "
                "200 period exponential moving averages."
            )

        }

        ###############################################################
        # RSI Analysis
        ###############################################################

    def analyze_rsi(self):

        self.calculate_rsi()

        rsi = self.latest("RSI")

        if rsi is None:
            return

        momentum_score = 0

        if rsi < 30:

            signal = "Oversold"

            momentum_score = 80

            self.signals.append(
                "RSI indicates oversold conditions"
            )

            self.strengths.append(
                "Possible bullish reversal zone"
            )

        elif rsi < 45:

            signal = "Weak"

            momentum_score = 65

        elif rsi <= 65:

            signal = "Healthy"

            momentum_score = 90

            self.strengths.append(
                "Healthy bullish momentum"
            )

        elif rsi <= 75:

            signal = "Overbought"

            momentum_score = 60

            self.weaknesses.append(
                "Approaching overbought territory"
            )

        else:

            signal = "Extremely Overbought"

            momentum_score = 35

            self.weaknesses.append(
                "High probability of pullback"
            )

        self.indicators["RSI"] = {

            "value": round(rsi,2),

            "signal": signal,

            "score": momentum_score,

            "description":
                "Relative Strength Index measures momentum on a scale from 0 to 100."

        }

        return momentum_score
    ###############################################################
    # MACD Analysis
    ###############################################################

    def analyze_macd(self):

        self.calculate_macd()

        macd = self.latest("MACD")

        signal_line = self.latest("MACD_SIGNAL")

        histogram = self.latest("MACD_HIST")

        macd_score = 0

        if macd > signal_line:

            status = "Bullish"

            macd_score = 90

            self.signals.append(
                "Bullish MACD crossover"
            )

        elif macd < signal_line:

            status = "Bearish"

            macd_score = 35

            self.weaknesses.append(
                "Bearish MACD crossover"
            )

        else:

            status = "Neutral"

            macd_score = 60

        self.indicators["MACD"] = {

            "macd": round(macd,3),

            "signal": round(signal_line,3),

            "histogram": round(histogram,3),

            "status": status,

            "score": macd_score,

            "description":
                "MACD compares short and long term momentum."

        }

        return macd_score

    ###############################################################
    # Calculate Technical Score
    ###############################################################

    def calculate_technical_score(self):

        trend = self.category_scores["Trend"]

        rsi_score = self.indicators["RSI"]["score"]

        macd_score = self.indicators["MACD"]["score"]

        momentum = round((rsi_score + macd_score) / 2)

        self.category_scores["Momentum"] = momentum

        scores = [

            score

            for score in self.category_scores.values()

            if score is not None

        ]

        if len(scores) == 0:

            return 0

        return round(sum(scores) / len(scores))


    ###############################################################
    # Grade
    ###############################################################

    def calculate_grade(self, score):

        if score >= 90:
            return "A+"

        elif score >= 80:
            return "A"

        elif score >= 70:
            return "B"

        elif score >= 60:
            return "C"

        return "D"


    ###############################################################
    # Summary
    ###############################################################

    def generate_summary(self):

        trend = self.indicators["Trend"]["classification"]

        rsi = self.indicators["RSI"]["signal"]

        macd = self.indicators["MACD"]["status"]

        return (

            f"The stock is currently in a "

            f"{trend.lower()} trend. "

            f"Momentum is {rsi.lower()} "

            f"and MACD is {macd.lower()}."

        )

    ###############################################################
    # Average True Range (ATR)
    ###############################################################

    def calculate_atr(self, period=14):

        high_low = self.history["High"] - self.history["Low"]

        high_close = (
            self.history["High"] -
            self.history["Close"].shift()
        ).abs()

        low_close = (
            self.history["Low"] -
            self.history["Close"].shift()
        ).abs()

        tr = pd.concat(

            [high_low, high_close, low_close],

            axis=1

        ).max(axis=1)

        self.history["ATR"] = (

            tr

            .rolling(period)

            .mean()

        )

        return "ATR"

    ###############################################################
    # ATR Analysis
    ###############################################################

    def analyze_atr(self):

        self.calculate_atr()

        atr = self.latest("ATR")

        price = self.latest("Close")

        atr_percent = (atr / price) * 100

        if atr_percent < 1.5:

            level = "Low"

            score = 90

        elif atr_percent < 3:

            level = "Normal"

            score = 80

        elif atr_percent < 5:

            level = "High"

            score = 60

        else:

            level = "Very High"

            score = 35

        self.category_scores["Volatility"] = score

        self.indicators["ATR"] = {

            "value": round(atr,2),

            "percent": round(atr_percent,2),

            "level": level,

            "score": score,

            "description":

            "Average True Range measures the average daily price movement."

        }

    ###############################################################
    # Bollinger Bands
    ###############################################################

    def calculate_bollinger(self, period=20):

        sma = self.history["Close"].rolling(period).mean()

        std = self.history["Close"].rolling(period).std()

        self.history["BB_UPPER"] = sma + (2 * std)

        self.history["BB_LOWER"] = sma - (2 * std)

        self.history["BB_MIDDLE"] = sma


    ###############################################################
    # Bollinger Analysis
    ###############################################################

    def analyze_bollinger(self):

        self.calculate_bollinger()

        price = self.latest("Close")

        upper = self.latest("BB_UPPER")

        lower = self.latest("BB_LOWER")

        middle = self.latest("BB_MIDDLE")

        if price > upper:

            signal = "Above Upper Band"

        elif price < lower:

            signal = "Below Lower Band"

        elif price > middle:

            signal = "Upper Half"

        else:

            signal = "Lower Half"

        self.indicators["Bollinger"] = {

            "upper": round(upper,2),

            "middle": round(middle,2),

            "lower": round(lower,2),

            "signal": signal,

            "description":

            "Bollinger Bands measure volatility around the moving average."

        }

    ###############################################################
    # Average Directional Index (ADX)
    ###############################################################

    def calculate_adx(self, period=14):

        high = self.history["High"]
        low = self.history["Low"]
        close = self.history["Close"]

        plus_dm = high.diff()
        minus_dm = -low.diff()

        plus_dm = plus_dm.where(
            (plus_dm > minus_dm) & (plus_dm > 0),
            0
        )

        minus_dm = minus_dm.where(
            (minus_dm > plus_dm) & (minus_dm > 0),
            0
        )

        tr1 = high - low

        tr2 = (high - close.shift()).abs()

        tr3 = (low - close.shift()).abs()

        tr = pd.concat(
            [tr1, tr2, tr3],
            axis=1
        ).max(axis=1)

        atr = tr.rolling(period).mean()

        plus_di = 100 * (
            plus_dm.rolling(period).mean() / atr
        )

        minus_di = 100 * (
            minus_dm.rolling(period).mean() / atr
        )

        dx = (

            (plus_di - minus_di).abs()

            /

            (plus_di + minus_di)

        ) * 100

        self.history["ADX"] = dx.rolling(period).mean()

    ###############################################################
    # ADX Analysis
    ###############################################################

    def analyze_adx(self):

        self.calculate_adx()

        adx = self.latest("ADX")

        if adx is None:

            return

        if adx < 20:

            level = "Weak Trend"

            score = 45

        elif adx < 25:

            level = "Developing Trend"

            score = 65

        elif adx < 40:

            level = "Strong Trend"

            score = 90

        else:

            level = "Very Strong Trend"

            score = 100

        self.indicators["ADX"] = {

            "value": round(adx,2),

            "strength": level,

            "score": score,

            "description":

            "ADX measures trend strength regardless of direction."

        }

        trend_score = self.category_scores.get("Trend")

        if trend_score is not None:

            self.category_scores["Trend"] = round(

                (trend_score + score) / 2

            )

    ###############################################################
    # Generate Report
    ###############################################################

    def generate_report(self):

        self.analyze_moving_averages()
        self.analyze_rsi()
        self.analyze_macd()
        self.analyze_atr()
        self.analyze_bollinger()
        self.analyze_adx()

        technical_score = self.calculate_technical_score()

        grade = self.calculate_grade(technical_score)

        summary = self.generate_summary()

        return {

            "technical_score": technical_score,

            "grade": grade,

            "summary": summary,

            "category_scores": self.category_scores,

            "indicators": self.indicators,

            "signals": self.signals,

            "strengths": self.strengths,

            "weaknesses": self.weaknesses

        }