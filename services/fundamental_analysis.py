import pandas as pd


class FundamentalAnalyzer:

    def __init__(self, market_snapshot):

        self.data = market_snapshot

        self.info = market_snapshot["company_info"]

        self.income = market_snapshot["quarterly_income"]

        self.balance = market_snapshot["balance_sheet"]

        self.cashflow = market_snapshot["cashflow"]

        self.metrics = {}

        self.strengths = []

        self.weaknesses = []

        self.score = 0


    # --------------------------------------------------------
    # Safe Getter
    # --------------------------------------------------------

    def safe(self, key, default=None):

        return self.info.get(key, default)


    # --------------------------------------------------------
    # Revenue Growth
    # --------------------------------------------------------

    def analyze_growth(self):

        growth_score = 0

        revenue_growth = None
        latest_revenue = None

        try:

            revenues = self.income.loc["Total Revenue"]

            latest = float(revenues.iloc[0])
            latest_revenue = latest

            previous = float(revenues.iloc[1])

            revenue_growth = ((latest - previous) / previous) * 100

        except Exception:

            revenue_growth = None

        if revenue_growth is not None:

            if revenue_growth >= 20:

                growth_score = 20

                status = "Excellent"

                self.strengths.append("Very strong revenue growth")

            elif revenue_growth >= 10:

                growth_score = 16

                status = "Strong"

                self.strengths.append("Healthy revenue growth")

            elif revenue_growth >= 0:

                growth_score = 12

                status = "Stable"

            elif revenue_growth >= -10:

                growth_score = 6

                status = "Weak"

                self.weaknesses.append("Revenue growth slowing")

            else:

                growth_score = 2

                status = "Poor"

                self.weaknesses.append("Revenue contraction")

        else:

            status = "Unavailable"

        self.score += growth_score

        self.metrics["Revenue Growth"] = {

            "value": revenue_growth,

            "revenue": latest_revenue,

            "status": status

        }


    # --------------------------------------------------------
    # Profitability
    # --------------------------------------------------------

    def analyze_profitability(self):

        margin = self.safe("profitMargins")

        score = 0

        if margin is not None:

            margin *= 100

            if margin >= 25:

                score = 20

                status = "Excellent"

                self.strengths.append("Excellent profitability")

            elif margin >= 15:

                score = 16

                status = "Strong"

            elif margin >= 8:

                score = 10

                status = "Average"

            else:

                score = 4

                status = "Weak"

                self.weaknesses.append("Low profit margin")

        else:

            status = "Unavailable"

            margin = None

        self.score += score

        self.metrics["Profit Margin"] = {

            "value": margin,

            "status": status

        }


    # --------------------------------------------------------
    # Valuation
    # --------------------------------------------------------

    def analyze_valuation(self):

        pe = self.safe("trailingPE")

        score = 0

        if pe:

            if pe < 20:

                score = 15

                status = "Undervalued"

            elif pe < 30:

                score = 12

                status = "Fair"

            elif pe < 40:

                score = 8

                status = "Expensive"

            else:

                score = 3

                status = "Overvalued"

                self.weaknesses.append("Premium valuation")

        else:

            status = "Unavailable"

        self.score += score

        self.metrics["Trailing PE"] = {

            "value": pe,

            "status": status

        }


    # --------------------------------------------------------
    # Financial Health
    # --------------------------------------------------------

    def analyze_financial_health(self):

        debt_equity = self.safe("debtToEquity")

        score = 0

        if debt_equity is not None:

            if debt_equity < 50:

                score = 15

                status = "Healthy"

            elif debt_equity < 100:

                score = 10

                status = "Acceptable"

            else:

                score = 5

                status = "High Debt"

                self.weaknesses.append("High leverage")

        else:

            status = "Unavailable"

            debt_equity = None

        self.score += score

        self.metrics["Debt to Equity"] = {

            "value": debt_equity,

            "status": status

        }


    # --------------------------------------------------------
    # Cash Flow
    # --------------------------------------------------------

    def analyze_cashflow(self):

        free_cf = self.safe("freeCashflow")

        score = 0

        if free_cf:

            if free_cf > 0:

                score = 15

                status = "Positive"

                self.strengths.append("Positive free cash flow")

            else:

                score = 4

                status = "Negative"

                self.weaknesses.append("Negative free cash flow")

        else:

            status = "Unavailable"

        self.score += score

        self.metrics["Free Cash Flow"] = {

            "value": free_cf,

            "status": status

        }


    # --------------------------------------------------------
    # Analyst Consensus
    # --------------------------------------------------------

    def analyze_analyst_consensus(self):

        rec = self.safe("recommendationKey")

        score = 0

        if rec:

            rec = rec.lower()

            if rec == "strong_buy":

                score = 15

            elif rec == "buy":

                score = 13

            elif rec == "hold":

                score = 8

            elif rec == "sell":

                score = 4

            else:

                score = 2

        self.score += score

        self.metrics["Analyst Rating"] = {

            "value": rec,

            "status": "Consensus"

        }


    # --------------------------------------------------------
    # Final Report
    # --------------------------------------------------------

    def generate_report(self):

        self.analyze_growth()

        self.analyze_profitability()

        self.analyze_valuation()

        self.analyze_financial_health()

        self.analyze_cashflow()

        self.analyze_analyst_consensus()

        if self.score >= 85:

            grade = "A+"

        elif self.score >= 75:

            grade = "A"

        elif self.score >= 65:

            grade = "B"

        elif self.score >= 50:

            grade = "C"

        else:

            grade = "D"

        return {

            "fundamental_score": self.score,

            "grade": grade,

            "strengths": self.strengths,

            "weaknesses": self.weaknesses,

            "metrics": self.metrics

        }
