# AI Daily News Bot

Automated bot that collects 30 top AI news items daily from 12+ RSS feeds and Google News, uses Gemini AI to filter, categorize and summarize, then sends a formatted email digest.

## Setup

1. Fork/clone this repo
2. Get API keys:
   - [Google AI Studio](https://aistudio.google.com/) → Gemini API key
   - [Resend](https://resend.com/) → API key + verify sender domain
3. Add GitHub Secrets:
   - `GEMINI_API_KEY`
   - `RESEND_API_KEY`
   - `EMAIL_TO` (your email)
   - `EMAIL_FROM` (verified sender, e.g. `news@yourdomain.com`)

## How it works

Runs daily at 10:00 Beijing time via GitHub Actions:

1. **Collect** — Fetches from 12 RSS feeds + 5 Google News keyword searches
2. **Filter** — Pre-filters ArXiv papers by AI keywords, deduplicates by title similarity
3. **AI Process** — Gemini 2.5 Flash selects top 30, classifies into 6 categories, generates Chinese summaries
4. **Send** — Formatted HTML email via Resend

## Local testing

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -v

# Run pipeline locally (needs env vars)
export GEMINI_API_KEY=your_key
export RESEND_API_KEY=your_key
export EMAIL_TO=you@example.com
export EMAIL_FROM=onboarding@resend.dev
python -m src.main
```

## Cost

$0/month — all services used within free tiers.
