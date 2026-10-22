import requests
import re


class CompanyResolver:


    def __init__(self):

        self.yahoo_search_url = (
            "https://query2.finance.yahoo.com/v1/finance/search"
        )


    def clean_query(self, query):

        query = query.lower()

        query = re.sub(r"'s\b", "", query)

        # Remove punctuation
        query = re.sub(r"[^a-zA-Z0-9\s]", " ", query)

        stop_words = {

            "analyze",
            "analysis",
            "earnings",
            "stock",
            "price",
            "performance",
            "company",
            "should",
            "buy",
            "sell",
            "is",
            "i",
            "my",
            "today",
            "now",
            "please",
            "the",
            "a",
            "an",
            "of",
            "for",
            "me",
            "show",
            "tell",
            "about",
            "give",
            "what",
            "how",
            "why",
            "can",
            "could",
            "would",
            "good",
            "bad",
            "recent", "latest", "quarter", "quarterly", "q1", "q2", "q3", "q4",
            "revenue", "growth", "risk", "risks", "factor", "factors", "outlook",
            "sentiment", "market", "trend", "trends", "company", "ticker", "stock",
            "for", "with", "and", "or", "vs", "versus", "compare", "comparison",
            "earnings", "eps", "financial", "performance", "overview", "analysis",
            "analyze", "analyse", "what", "which", "when", "where", "tell", "explain",
            "summary", "please", "show", "look", "like", "help", "think", "invest",
            "investment", "investments", "invested", "investing", "much", "money",
            "amount", "made", "returns", "return", "expected", "expect", "expecting",
            "expectations", "potential", "profit", "profits", "gain", "gains", "loss",
            "losses", "can", "will", "be", "in", "share", "shares", "over", "next",
            "year", "years", "month", "months", "long", "term", "portfolio", "my",
            "from", "your", "their", "possible", "estimate", "forecast", "forecasted",
            "likely", "future", "amounts", "dollars", "risk", "tolerance",
            "are", "am", "do", "does", "did", "was", "were", "has", "have", "had",
            "impact", "affect", "affects", "effect", "influence", "on", "of", "at",
            "key", "main", "major", "some", "any", "all", "their", "its", "this",
            "that", "these", "those", "between", "versus", "vs", "compared", "compare",
            "explain", "definition", "define", "means", "mean", "difference", "benefits",
            "benefit", "pros", "cons", "types", "type", "basics", "basically", "guide",
            "interest", "interests", "rate", "rates", "inflation", "recession", "economy",
            "economic", "economics", "bond", "bonds", "etf", "etfs", "fund", "funds",
            "mutual", "index", "indices", "indexed", "diversification", "diversified",
            "diversify", "budget", "tax", "taxes", "capital", "asset", "assets", "debt",
            "credit", "loan", "loans", "mortgage", "mortgages", "retirement", "401k",
            "ira", "yield", "dividend", "dividends", "valuation", "valuations", "financially",
            "market", "markets", "equity", "equities", "shareholder", "shareholders",
            "business", "businesses", "company's", "companys", "companies", "sector", "industry",
            "tell", "me", "please", "would", "should", "could", "might", "may", "will",
            "get", "make", "made", "put", "take", "better", "best", "good", "bad", "top",
            "stocks", "well", "fundamental", "technical", "thesis", "intrinsic",
            "value", "values", "p", "e", "pe", "ratio", "ratios", "savings", "saving",
            "account", "accounts", "checking", "score", "scores", "forex", "currency",
            "currencies", "crypto", "cryptocurrency", "cryptocurrencies", "bitcoin", "ethereum",
            "options", "futures", "derivative", "derivatives", "leverage", "margin", "short",
            "selling", "commodities", "commodity", "annuity", "annuities", "insurance",
            "supply", "demand", "employment", "unemployment", "gdp", "fed", "federal",
            "reserve", "central", "bank", "banks", "monetary", "policy", "fiscal", "budgeting",
            "compound", "work", "works", "worked", "working", "split", "splits", "apr", "apy",
            "roi", "rsi", "dcf", "capm", "wacc", "cagr", "ipo", "roe", "roa", "fcf",
            "ebit", "ebitda", "nav", "model", "models", "current", "currently", "know", "knows",
            "understand", "understanding", "start", "starting", "build", "building", "save", "saving",
            "allocate", "allocation", "dividends", "dividend", "interest-rate", "apr", "apy"

        }

        words = []

        for word in query.split():

            if word not in stop_words:

                words.append(word)

        return " ".join(words)


    def search_yahoo(self, query):

        print(f"\nSearching Yahoo for: {query}")

        params = {
            "q": query,
            "quotesCount": 10,
            "newsCount": 0
        }

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        try:

            response = requests.get(
                self.yahoo_search_url,
                params=params,
                headers=headers,
                timeout=10
            )

            print("HTTP Status:", response.status_code)

            data = response.json()

            quotes = data.get("quotes", [])

            print(f"Found {len(quotes)} quotes")

            if not quotes:
                return None

            for quote in quotes:

                print(
                    quote.get("symbol"),
                    quote.get("quoteType"),
                    quote.get("exchange")
                )

            equity_quotes = [
                q for q in quotes
                if q.get("quoteType") == "EQUITY"
            ]

            print("Equity Quotes:", len(equity_quotes))

            if not equity_quotes:
                return None

            quote = equity_quotes[0]

            result = {
                "ticker": quote.get("symbol"),
                "company": quote.get("longname") or quote.get("shortname")
            }

            print("Returning:", result)

            return result

        except Exception as e:

            print("Yahoo Search Error:", e)

            return None

    def resolve(self, user_input):

        cleaned = self.clean_query(user_input)

        # Skip Yahoo's search call when a query contains an unambiguous
        # uppercase ticker symbol (for example, "Analyze AAPL earnings").
        common_words = {"I", "Q1", "Q2", "Q3", "Q4", "EPS", "CEO", "USA", "AI"}
        symbols = re.findall(r"(?<![A-Za-z0-9])[A-Z][A-Z0-9.^=-]{1,9}(?![A-Za-z0-9])", user_input)
        for symbol in symbols:
            if (
                symbol not in common_words
                and not symbol.startswith("Q")
                and symbol.lower() in cleaned.split()
            ):
                return {"ticker": symbol, "company": symbol}

        if not cleaned:
            return {
                "ticker": None,
                "company": None,
                "error": "Company not found"
            }

        print("INPUT :", user_input)
        print("SEARCH:", cleaned)

        result = self.search_yahoo(cleaned)

        print("SEARCH RESULT:", result)

        if result is not None:
            return result

        return {
            "ticker": None,
            "company": None,
            "error": "Company not found"
        }
