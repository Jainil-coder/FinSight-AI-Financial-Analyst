# FinSight: AI Financial Analyst

FinSight is a Flask-based financial chat application for company research and general finance questions. Ask about a public company by name or ticker, or ask a general finance question. Company queries display a market-data insight card first while a LangChain-powered answer is generated.

> **Disclaimer:** FinSight is for educational and informational purposes only. It does not provide personalized investment advice or guarantee future performance. Market data may be delayed, incomplete, or unavailable.

## Features

- Ask company questions using a company name or ticker symbol.
- View an insight card with available revenue, quarter-over-quarter change, sentiment, outlook, and risk factors.
- Ask general finance questions about concepts, markets, accounting, or investing.
- Get answers generated with LangChain and Google Gemini when `GOOGLE_API_KEY` is configured.
- See company insight cards before the longer AI response finishes.
- Keep a watchlist and recent conversations in browser session storage.
- Use the responsive chat interface on desktop and mobile.

The two welcome cards are example prompts only. You can type other questions in the chat box.

## Requirements

- Python 3.10 or newer
- Internet access for ticker lookup and market data
- A Google AI API key for generated finance answers (optional for the company data card)

## Install

### Windows PowerShell

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Configure

Create a `.env` file in the project root:

```dotenv
GOOGLE_API_KEY=your_google_ai_api_key
```

The key is used by LangChain's Google Gemini integration for detailed company answers and general finance Q&A. Keep `.env` private and do not commit API keys to GitHub. Without the key, company insight cards and their data-based summaries can still be shown, but AI-generated general answers are unavailable.

## Run

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in a browser. The application uses Yahoo Finance search for company resolution and `yfinance` for market data, so those features require an internet connection and depend on upstream availability.

## Example questions

```text
Analyze Tesla's recent earnings
What are the main risks for NVDA?
Explain Apple's P/E ratio
What is compound interest?
How do interest rates affect stocks?
```

For hypothetical return scenarios, provide assumptions such as an amount and time horizon. FinSight should label scenarios as hypothetical and must not present them as guaranteed returns.

## API

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/` | Serves the chat interface. |
| `POST` | `/analyze` | Resolves a company and returns a quick insight card, or starts a general finance answer. |
| `POST` | `/answer` | Generates the detailed answer for a company or general finance question. |
| `GET` | `/health` | Returns the Flask service status. |

Example request to `/analyze`:

```json
{
  "query": "What are the main risks for Tesla?",
  "history": []
}
```

## Project structure

```text
.
├── app.py                     # Flask routes and JSON handling
├── config.py                  # Environment and analysis configuration
├── requirements.txt           # Python dependencies
├── services/
│   ├── chat_backend.py        # LangChain/Gemini finance responses
│   ├── company_resolver.py    # Company and ticker lookup
│   ├── insights.py            # Market-data insight cards
│   ├── market_data.py         # Market data access
│   ├── analysis_engine.py     # Fundamental and technical analysis
│   └── ...                    # Analysis and formatting services
├── static/
│   ├── script.js              # Chat, history, and watchlist behavior
│   └── style.css              # Application styling
├── templates/
│   └── index.html             # Chat interface
└── tests/                     # Existing analysis and resolver checks
```

## Data and limitations

- Market fields depend on Yahoo Finance data availability; unavailable metrics are not replaced with sample values.
- General finance answers come from the configured language model and may need verification for time-sensitive topics.
- Chat history and watchlist are stored in the browser's session storage, not in a user account or shared database.
- This project is a research aid, not a trading system or source of guaranteed price targets.
