"""
Application Configuration
Central location for project settings.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ==========================
# LLM Configuration
# ==========================

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

GEMINI_MODEL = "gemini-2.5-flash"

# ==========================
# Technical Analysis Settings
# ==========================

DEFAULT_TIMEFRAME = "6mo"

DEFAULT_INTERVAL = "1d"

SHORT_EMA = 20
MEDIUM_EMA = 50
LONG_EMA = 200

RSI_PERIOD = 14

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

BOLLINGER_PERIOD = 20

ATR_PERIOD = 14

ADX_PERIOD = 14

# ==========================
# Recommendation Weights
# ==========================

FUNDAMENTAL_WEIGHT = 0.40
TECHNICAL_WEIGHT = 0.40
SENTIMENT_WEIGHT = 0.20

# ==========================
# General
# ==========================

REQUEST_TIMEOUT = 15