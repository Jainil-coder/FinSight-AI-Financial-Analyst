from services.query_processor import QueryProcessor
from services.company_resolver import CompanyResolver
from services.analysis_engine import AnalysisEngine

class AnalysisRouter:

    """
    Main backend entry point.

    Flow:

    User Input
        ↓
    Query Processor
        ↓
    Company Resolver
        ↓
    Analysis Engine
        ↓
    JSON Response
    """

    def __init__(self):

        self.query_processor = QueryProcessor()

        self.company_resolver = CompanyResolver()

        self.analysis_engine = AnalysisEngine()

    ###############################################################
    # PUBLIC
    ###############################################################

    def process(self, user_input):

        # Accept either string query or pre-parsed dictionary
        if isinstance(user_input, dict):
            query_str = user_input.get("query", "")
            parsed = user_input
        else:
            query_str = str(user_input)
            parsed = self.query_processor.process(query_str)

        intent = parsed.get("intent")

        ###########################################################
        # Resolve Company
        ###########################################################

        # Resolve from the full question so multi-word company names and
        # ordinary phrasing survive query parsing.
        resolved = self.company_resolver.resolve(query_str)

        ticker = resolved.get("ticker") if isinstance(resolved, dict) else getattr(resolved, "ticker", None)
        company = (
            resolved.get("name") or resolved.get("company") or ticker
            if isinstance(resolved, dict)
            else getattr(resolved, "name", ticker)
        )

        if ticker is None:

            return {

                "success": False,

                "message": "Unable to identify company."

            }

        ###########################################################
        # Run Analysis
        ###########################################################

        analysis = self.analysis_engine.analyze(

            ticker

        )

        ###########################################################
        # Response
        ###########################################################

        return {

            "success": True,

            "intent": intent,

            "query": query_str,

            "ticker": ticker,

            "company": company,

            "analysis": analysis

        }

    # Method aliases to prevent attribute errors regardless of caller
    def route(self, user_input):
        return self.process(user_input)

    def analyze(self, user_input):
        return self.process(user_input)
