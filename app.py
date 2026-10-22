from flask import Flask, jsonify, render_template, request
import math
from services.company_resolver import CompanyResolver
from services.chat_backend import answer_general_finance_question, answer_stock_question

app = Flask(__name__)
company_resolver = CompanyResolver()


def clean_json(value):
    """Convert analytics-library values into strict JSON-safe primitives."""
    if isinstance(value, dict):
        return {str(key): clean_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean_json(item) for item in value]
    if isinstance(value, float):
        number = float(value)
        return number if math.isfinite(number) else None
    # Handle optional numpy/pandas scalar objects without importing their large
    # packages during Flask startup.
    if not isinstance(value, (str, int, bool)) and hasattr(value, "item"):
        try:
            return clean_json(value.item())
        except (TypeError, ValueError):
            pass
    if not isinstance(value, (str, int, bool)) and hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except (TypeError, ValueError):
            pass
    if str(value) in {"<NA>", "NaT"}:
        return None
    return value


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/analyze")
def analyze():
    payload = request.get_json(silent=True) or {}
    query = payload.get("query", "")
    if not isinstance(query, str) or not query.strip():
        return jsonify({"success": False, "error": "Enter a company or ticker to analyze."}), 400

    try:
        history = payload.get("history", [])
        resolver = company_resolver
        search_terms = resolver.clean_query(query.strip())
        if not search_terms:
            return jsonify({
                "success": True,
                "ticker": None,
                "company": None,
                "insight": None,
                "reply": "Preparing an answer to your finance question…",
                "answer_type": "general_finance",
                "needs_answer": True,
            })

        resolved = resolver.resolve(query.strip())
        ticker = resolved.get("ticker") if isinstance(resolved, dict) else None
        if not ticker:
            return jsonify({
                "success": True,
                "ticker": None,
                "company": None,
                "insight": None,
                "reply": "Preparing an answer to your finance question…",
                "answer_type": "general_finance",
                "needs_answer": True,
            })

        from services.insights import get_stock_insights

        insight = get_stock_insights(ticker)
        reply = answer_stock_question(query.strip(), insight, history=history, use_model=False)
        return jsonify(clean_json({
            "success": True,
            "ticker": ticker,
            "company": insight["company"],
            "insight": insight,
            "reply": reply,
            "answer_type": "company_finance",
            "needs_answer": True,
        }))
    except Exception as exc:
        app.logger.exception("Analysis request failed")
        return jsonify({
            "success": False,
            "error": "Market data could not be loaded. Check the ticker and try again.",
        }), 502


@app.post("/answer")
def answer():
    payload = request.get_json(silent=True) or {}
    query = payload.get("query", "")
    ticker = payload.get("ticker")
    history = payload.get("history", [])
    if not isinstance(query, str) or not query.strip():
        return jsonify({"success": False, "error": "A question is required."}), 400
    try:
        if isinstance(ticker, str) and ticker.strip():
            from services.insights import get_stock_insights

            insight = get_stock_insights(ticker.strip().upper())
            reply = answer_stock_question(query.strip(), insight, history=history)
        else:
            reply = answer_general_finance_question(query.strip(), history=history)
        return jsonify({"success": True, "reply": reply})
    except Exception:
        app.logger.exception("Finance answer generation failed")
        return jsonify({"success": False, "error": "The detailed answer could not be generated."}), 502


@app.get("/health")
def health():
    return jsonify({"status": "running", "service": "Financial AI Assistant"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
