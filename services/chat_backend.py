"""LangChain answer generation for company-specific and general finance queries."""

import json
from typing import Any

from config import GEMINI_MODEL, GOOGLE_API_KEY


def _history_text(history):
    safe_history = []
    for item in (history or [])[-8:]:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if role in {"user", "assistant"} and isinstance(content, str):
            safe_history.append({"role": role, "content": content[:1200]})
    return json.dumps(safe_history, ensure_ascii=False)


def _invoke(system_prompt, question, context=None, history=None):
    if not GOOGLE_API_KEY:
        return None
    try:
        # Legacy LangChain Core versions read langchain.verbose internally.
        # Initialize it through the supported API so that compatibility read
        # does not emit a deprecation warning on every model request.
        from langchain.globals import set_verbose
        from langchain_core.messages import HumanMessage, SystemMessage
        from langchain_google_genai import ChatGoogleGenerativeAI

        set_verbose(False)
        model = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=0.2,
        )
        prompt = f"Question: {question}\nConversation history: {_history_text(history)}"
        if context is not None:
            prompt += f"\nAvailable company data (JSON): {json.dumps(context, allow_nan=False)}"
        result = model.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt),
        ])
        content: Any = result.content
        if isinstance(content, list):
            content = " ".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in content
            )
        text = str(content).strip()
        return text or None
    except Exception:
        return None


def answer_stock_question(question, insights, history=None, use_model=True):
    """Answer a company question using only the returned quote/fundamental context."""
    base_fallback = (
        f"I found {insights['company']} ({insights['ticker']}). The available snapshot reports "
        f"{insights['sentiment'].lower()} sentiment, revenue of {insights['revenue']['value']} "
        f"({insights['revenue']['qoq']}), and an outlook of {insights['outlook']}. "
        f"Reported risk factors: {', '.join(insights['risk_factors'])}. "
        "Ask about a particular metric for a focused explanation."
    )
    question_lower = question.lower()
    metrics = insights.get("financial_metrics", {})
    if any(word in question_lower for word in ("risk", "downside", "concern", "threat")):
        fallback = (
            f"The available snapshot flags these risk factors for {insights['company']}: "
            f"{', '.join(insights['risk_factors'])}. This summary is limited to the metrics "
            "available from the market data provider and may not cover every business risk."
        )
    elif any(word in question_lower for word in ("return", "profit", "gain", "how much", "invest")):
        fallback = (
            "No return is guaranteed, and this snapshot cannot determine a suitable investment "
            "amount or predict future performance. Position size depends on your budget, time "
            "horizon, portfolio, and risk tolerance; any scenario would be hypothetical."
        )
    elif any(word in question_lower for word in ("valuation", "p/e", "pe ratio", "expensive", "cheap")):
        pe = metrics.get("trailing_pe")
        pe_text = f"trailing P/E is {pe:.1f}" if isinstance(pe, (int, float)) else "trailing P/E is unavailable"
        fallback = (
            f"For {insights['company']}, {pe_text}. P/E is only one valuation measure and "
            "should be compared with the company's growth, peers, and balance-sheet risks."
        )
    elif any(word in question_lower for word in ("revenue", "earnings", "sales", "eps")):
        fallback = (
            f"The latest available quarterly revenue for {insights['company']} is "
            f"{insights['revenue']['value']} ({insights['revenue']['qoq']}). "
            f"The current outlook signal is {insights['outlook']}."
        )
    else:
        fallback = base_fallback
    response = _invoke(
        """You are a financial research assistant. Answer the user's actual question directly.
Use only the supplied company data for claims about this company. If a requested metric or
historical detail is absent, say that it is unavailable; do not invent data. You may explain
general financial concepts, but distinguish them from company-specific facts. Never promise
returns or provide a personalized buy/sell instruction or position size. For investment amount
or expected-return questions, explain that no return is guaranteed, ask for budget and horizon
before illustrating a hypothetical scenario, and label any scenario as illustrative. Keep the
answer concise and readable.""",
        question,
        context=insights,
        history=history,
    )
    return (response or fallback) if use_model else fallback


def answer_general_finance_question(question, history=None):
    """Answer finance questions that do not identify a particular company."""
    fallback = (
        "I can help explain general finance concepts. For a company-specific answer, include a "
        "clear company name or ticker; the live company lookup did not return usable data. "
        "General AI answers require GOOGLE_API_KEY to be configured in the app environment."
    )
    response = _invoke(
        """You are a clear, careful financial education assistant. Answer general finance,
markets, investing, accounting, and economic questions in accessible language. Do not claim
to know live prices, current rates, recent events, or jurisdiction-specific tax/legal rules
unless the user supplied those facts. Say when information may be time-sensitive or when a
location/context is needed. Do not promise investment returns or give personalized investment
recommendations. Explain calculations and assumptions when relevant. For scenario analysis,
ask for missing inputs and label results hypothetical. No structured company data was supplied
for this request: do not invent company-specific metrics or current analysis. If the question
depends on a particular company's latest performance, say that and ask for a company name or
ticker. If a question is outside finance, say briefly that you specialize in finance.""",
        question,
        history=history,
    )
    return response or fallback


def explain_insights(question, insights, use_model=True):
    """Backward-compatible entry point for callers from earlier app versions."""
    if not use_model:
        return answer_stock_question(question, insights)
    return answer_stock_question(question, insights)
