import yfinance as yf
import pandas as pd

from config import (
    DEFAULT_TIMEFRAME,
    DEFAULT_INTERVAL
)


class MarketDataService:

    def __init__(self, ticker):

        self.ticker = ticker.upper()

        self.stock = yf.Ticker(self.ticker)

    ###########################################################
    # Company Information
    ###########################################################

    def get_company_info(self):

        try:
            return self.stock.info

        except Exception:

            return {}

    ###########################################################
    # Historical Price Data
    ###########################################################

    def get_price_history(
            self,
            period=DEFAULT_TIMEFRAME,
            interval=DEFAULT_INTERVAL):

        try:

            history = self.stock.history(

                period=period,

                interval=interval,

                auto_adjust=True

            )

            return history

        except Exception:

            return pd.DataFrame()

    ###########################################################
    # Quarterly Income Statement
    ###########################################################

    def get_quarterly_income(self):

        try:

            return self.stock.quarterly_income_stmt

        except Exception:

            return pd.DataFrame()

    ###########################################################
    # Balance Sheet
    ###########################################################

    def get_balance_sheet(self):

        try:

            return self.stock.balance_sheet

        except Exception:

            return pd.DataFrame()

    ###########################################################
    # Cash Flow
    ###########################################################

    def get_cashflow(self):

        try:

            return self.stock.cashflow

        except Exception:

            return pd.DataFrame()

    ###########################################################
    # Quarterly Cash Flow
    ###########################################################

    def get_quarterly_cashflow(self):

        try:

            return self.stock.quarterly_cashflow

        except Exception:

            return pd.DataFrame()

    ###########################################################
    # Quarterly Balance Sheet
    ###########################################################

    def get_quarterly_balance_sheet(self):

        try:

            return self.stock.quarterly_balance_sheet

        except Exception:

            return pd.DataFrame()

    ###########################################################
    # Analyst Recommendations
    ###########################################################

    def get_recommendations(self):

        try:

            return self.stock.recommendations

        except Exception:

            return pd.DataFrame()

    ###########################################################
    # Earnings Dates
    ###########################################################

    def get_earnings_dates(self):

        try:

            return self.stock.earnings_dates

        except Exception:

            return pd.DataFrame()

    ###########################################################
    # News
    ###########################################################

    def get_news(self):

        try:

            return self.stock.news

        except Exception:

            return []

    ###########################################################
    # Complete Dataset
    ###########################################################

    def get_market_snapshot(self):

        return {

            "ticker": self.ticker,

            "company_info": self.get_company_info(),

            "history": self.get_price_history(),

            "quarterly_income": self.get_quarterly_income(),

            "balance_sheet": self.get_balance_sheet(),

            "cashflow": self.get_cashflow(),

            "quarterly_cashflow": self.get_quarterly_cashflow(),

            "quarterly_balance_sheet":
                self.get_quarterly_balance_sheet(),

            "recommendations":
                self.get_recommendations(),

            "earnings_dates":
                self.get_earnings_dates(),

            "news":
                self.get_news()

        }