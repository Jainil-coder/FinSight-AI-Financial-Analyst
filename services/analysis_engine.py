from services.market_data import MarketDataService
from services.fundamental_analysis import FundamentalAnalyzer
from services.technical_analysis import TechnicalAnalyzer
from services.recommendation_engine import RecommendationEngine


class AnalysisEngine:
    def __init__(self):
        pass

    ####################################################################
    # Complete Analysis Pipeline
    ####################################################################

    def analyze(self, ticker):
        ticker = ticker.upper()

        ###############################################################
        # Download market data once
        ###############################################################

        market = MarketDataService(ticker)
        snapshot = market.get_market_snapshot()

        ###############################################################
        # Fundamental Analysis
        ###############################################################

        fundamental_analyzer = FundamentalAnalyzer(snapshot)
        fundamental_report = fundamental_analyzer.generate_report()

        ###############################################################
        # Technical Analysis
        ###############################################################

        technical_analyzer = TechnicalAnalyzer(snapshot)
        technical_report = technical_analyzer.generate_report()

        ###############################################################
        # Recommendation Engine
        ###############################################################

        recommendation_engine = RecommendationEngine(
            fundamental_report,
            technical_report
        )

        recommendation_report = recommendation_engine.generate_report()

        ###############################################################
        # Final Response
        ###############################################################

        company_info = snapshot.get("company_info", {})
        market_data = {
            "current_price": company_info.get("currentPrice"),
            "previous_close": company_info.get("previousClose"),
            "open": company_info.get("open"),
            "day_high": company_info.get("dayHigh"),
            "day_low": company_info.get("dayLow"),
            "market_cap": company_info.get("marketCap"),
            "volume": company_info.get("volume"),
            "average_volume": company_info.get("averageVolume"),
            "fifty_two_week_high": company_info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": company_info.get("fiftyTwoWeekLow"),
            "beta": company_info.get("beta"),
            "dividend_yield": company_info.get("dividendYield")
        }

        return {

            "ticker": ticker,

            "company": {
                "name": company_info.get("longName"),
                "sector": company_info.get("sector"),
                "industry": company_info.get("industry"),
                "exchange": company_info.get("exchange"),
                "currency": company_info.get("currency")
            },

            "market_data": market_data,

            "fundamental": fundamental_report,

            "technical": technical_report,

            "recommendation": recommendation_report,

            "earnings": self._format_earnings(snapshot),

            "news": self._format_news(snapshot)
        }

    ####################################################################
    # Earnings
    ####################################################################

    def _format_earnings(self, snapshot):

        earnings = snapshot.get("earnings_dates")

        if earnings is None:
            return []

        try:
            return earnings.head(8).to_dict("index")

        except Exception:
            return []

    ####################################################################
    # News
    ####################################################################

    def _format_news(self, snapshot):

        news = snapshot.get("news", [])

        cleaned = []

        try:

            for item in news[:8]:

                cleaned.append({

                    "title":
                        item.get("title"),

                    "publisher":
                        item.get("publisher"),

                    "link":
                        item.get("link"),

                    "published":
                        item.get("providerPublishTime")
                })

        except Exception:
            pass

        return cleaned

    ####################################################################
    # Compare Stocks (Future)
    ####################################################################

    def compare(self, tickers):

        reports = []

        for ticker in tickers:

            try:

                reports.append(self.analyze(ticker))

            except Exception:

                continue

        return reports

    ####################################################################
    # Portfolio Analysis (Future)
    ####################################################################

    def analyze_portfolio(self, tickers):

        portfolio = []

        for ticker in tickers:

            try:

                portfolio.append(self.analyze(ticker))

            except Exception:

                continue

        return portfolio

    ####################################################################
    # Watchlist Scan (Future)
    ####################################################################

    def scan_watchlist(self, tickers):

        watchlist = []

        for ticker in tickers:

            try:

                result = self.analyze(ticker)

                watchlist.append({

                    "ticker": ticker,

                    "recommendation":
                        result["recommendation"],

                    "technical_score":
                        result["technical"]["technical_score"],

                    "fundamental_score":
                        result["fundamental"]["fundamental_score"]
                })

            except Exception:

                continue

        return watchlist

    def _format_news(self, snapshot):

        news = snapshot.get("news", [])

        formatted = []

        for article in news[:10]:

            content = article.get("content", {})

            formatted.append({

                "title": content.get("title"),

                "publisher": content.get("provider", {}).get("displayName"),

                "published": content.get("pubDate"),

                "link": content.get("canonicalUrl", {}).get("url")

            })

        return formatted

    def _format_earnings(self, snapshot):

        earnings = snapshot.get("earnings_dates")

        if earnings is None:

            return []

        if earnings.empty:

            return []

        earnings = earnings.head(8)

        output = []

        for index, row in earnings.iterrows():

            output.append({

                "date": str(index),

                "estimate": row.get("EPS Estimate"),

                "actual": row.get("Reported EPS"),

                "surprise": row.get("Surprise(%)")

            })

        return output