# TalentFlow AI 2.0

A fresh, independent implementation of a Streamlit candidate-screening application using
LangChain, LangGraph, and OpenAI. Includes PDF/DOCX and pasted text inputs, public job URL
retrieval, job understanding, resume classification, and evidence-grounded assessment.

## Run locally (Windows PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
# Edit .env and insert your own OPENAI_API_KEY
python -m pytest -q
streamlit run ui/app.py
```

Your old `.env` may be copied instead, but check that its variable names match `.env.example`.
Never commit `.env` or candidate resumes. The new folder is independent of your old repository.

## Inputs

Job: public URL, pasted JD, PDF, or DOCX. Candidate: pasted resume or PDF/DOCX.
Job title is inferred from the JD; unclear roles request clarification. The system makes up
to three LLM calls: job analysis and document classification, followed by assessment only
if both pass eligibility checks. The first two can run in parallel.

## Important limitations

- URLs requiring login or JavaScript rendering may not be accessible; paste the JD instead.
- The web reader validates public DNS answers but is **not a complete SSRF defense** against
  DNS rebinding. Do not deploy publicly without network-level egress controls.
- Image-only scans require OCR; paste text or upload a text-based document for now.
- The match score is a heuristic, not a calibrated hiring probability or hiring decision.
- LangSmith is off by default for privacy; use synthetic documents when enabling tracing.
- Dependency ranges are bounded but not lockfile-pinned. Pin resolved versions before production.

## Review

See `docs/architecture.md`. CI runs syntax compilation and unit tests. Model evaluation,
security review, and end-to-end deployment validation are still required.
