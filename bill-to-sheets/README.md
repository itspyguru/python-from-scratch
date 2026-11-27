# AI bill reader: bill photos and Gmail invoices to Google Sheets

Give it a photo of a bill, or let it pick up invoice PDFs from your Gmail, and it fills a Google Sheet:
shop, date, category, items, the total converted to rupees at that day's exchange rate, no duplicates,
and a Summary tab with SUMIFS formulas and a chart. Built with Gemini (through OpenRouter), Pydantic,
gspread and the Gmail API.

## Files

- `extract.py`: sends a photo or PDF to Gemini as base64 and gets back clean data in a Pydantic shape.
- `sheets.py`: writes rows with gspread (service account), converts currency with frankfurter.dev,
  skips duplicates and builds the Summary tab and chart.
- `gmail_fetch.py`: finds invoice/receipt emails with the Gmail API (read-only OAuth) and downloads the PDFs.
- `main.py`: runs everything: bills in `bills/` plus the Gmail PDFs, into the Sheet.

## Run it

1. Google Cloud: create a project, enable the Sheets, Drive and Gmail APIs, create a service account and
   download its JSON key as `service_account.json`, then create an OAuth Desktop client and download it as
   `credentials.json`.
2. Create a Google Sheet and share it with the service account's email (Editor).
3. Get an OpenRouter key at https://openrouter.ai/keys.

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then fill in your values
mkdir bills                     # put your bill photos/PDFs here
python main.py
```

Never commit `.env`, `service_account.json`, `credentials.json` or `token.json`.
