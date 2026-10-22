import re
class QueryProcessor:

    def __init__(self):

        self.intent_keywords = {

            "COMPARE": [
                "compare",
                "versus",
                "vs"
            ],

            "BUY_RECOMMENDATION": [
                "buy",
                "purchase",
                "invest"
            ],

            "SELL_RECOMMENDATION": [
                "sell",
                "exit"
            ],

            "SHOW_CHART": [
                "chart",
                "graph",
                "technical"
            ],

            "EARNINGS": [
                "earnings",
                "eps",
                "quarter",
                "revenue"
            ],

            "RISK_ANALYSIS": [
                "risk",
                "risks"
            ],

            "NEWS": [
                "news",
                "headline",
                "latest"
            ],

            "WATCHLIST_ADD": [
                "watchlist",
                "add"
            ]
        }

    def detect_intent(self, query):

        lower = query.lower()

        for intent, keywords in self.intent_keywords.items():

            for keyword in keywords:

                if keyword in lower:

                    return intent

        return "ANALYZE"

    def extract_companies(self, query):

        query = re.sub(r"[?.,!]", "", query)

        stop_words = {

            "analyze",
            "analysis",
            "buy",
            "sell",
            "should",
            "show",
            "chart",
            "technical",
            "earnings",
            "stock",
            "compare",
            "vs",
            "versus",
            "and",
            "news",
            "latest",
            "please",
            "give",
            "tell",
            "about",
            "risk",
            "risks",
            "invest",
            "purchase",
            "watchlist",
            "add",
            "i"
        }

        companies = []

        for word in query.split():

            if word.lower() not in stop_words:

                companies.append(word)

        return companies

    def process(self, query):

        return {

            "intent": self.detect_intent(query),

            "companies": self.extract_companies(query),

            "timeframe": None,

            "metrics": []

        }

    def parse(self, query):
        return self.process(query)