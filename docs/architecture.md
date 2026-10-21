# Architecture

Streamlit → ScreeningService → ContentService → LangGraph.

LangGraph starts `analyze_job` and `classify_resume` concurrently. An eligibility barrier
requires both to finish. Only a valid job and valid resume trigger `assess`.

LangChain provides structured OpenAI calls. LangSmith tracing is opt-in. The UI never invokes
models directly. Models never execute arbitrary tools. Scores are nullable for review outcomes.

## Operational boundaries

- Input files are parsed locally; pasted text bypasses extraction.
- Job URL fetching is bounded but **not hardened against DNS rebinding**. Use a network egress
  policy or a pinned-address fetcher before deploying to an untrusted public environment.
- JavaScript-rendered or authenticated job boards may require pasting the description.
- AI match scores are heuristic and require human review; do not automate hiring decisions.
- LangSmith can capture personal data in prompts and responses; use synthetic data for development.
