# Verity — project rules for Claude

## What this is
Hackathon prototype (VIT AI Innovate-A-Thon, Q18). Detects scam messages and
suspicious simulated UPI transactions, explains the risk in plain language
(en/hi/ta) with safe next steps. Synthetic data only. No real UPI
integration.

## Stack
- Backend: Python 3.11+, FastAPI, pydantic v2, scikit-learn, joblib, pytest,
  ruff
- Frontend: React 18 + Vite + TypeScript (strict) + Tailwind, recharts
- Run: docker compose up  (backend :8000, frontend :5173)

## Folder ownership — edit ONLY your folder
- data/, ml/        -> S-ML
- backend/          -> S-BACKEND
- frontend/         -> S-FRONTEND
- docs/, tests/e2e/ -> S-DOCS
- contracts/, CLAUDE.md, Makefile, docker-compose.yml -> lead only.
  Need a contract change? Append it to docs/CONTRACT_REQUESTS.md and stop.

## Contract
contracts/api.md is the source of truth. Backend responses must validate
against contracts/schemas.py; frontend uses contracts/types.ts. Never rename
fields. Endpoints are prefixed /api/v1.

## Commands
make setup | make data | make train | make eval | make dev | make test | make
smoke

## Hard rules
- NEVER fetch, open, or resolve URLs found in user messages. Parse strings
  only.
- NEVER use real personal data. All names, VPAs, phone numbers are synthetic.
- The app must work with NO LLM key. LLM is optional re-phrasing only and may
  never change a label or score.
- No secrets in git. Read keys from env (ANTHROPIC_API_KEY optional).
- Python: type hints everywhere, functions < 50 lines, pytest for every
  service.
- TS: no `any`, components < 200 lines, accessible (labels, aria, keyboard).
- Commit after every working step with a clear message.

## Design (frontend)
- Light theme only. Off-white canvas, white cards, ink text, one deep-blue
  brand colour. No dark mode, no neon, no gradients-on-black "AI" look.
- Type: Source Serif 4 for display headings, Inter for UI, JetBrains Mono for
  data. Noto Sans Devanagari / Tamil for hi/ta. All fonts self-hosted
  (@fontsource) so the offline demo looks identical.
- Risk states always use colour + icon + text: SAFE green, SUSPICIOUS amber,
  HIGH_RISK red. Never colour alone.
- Motion: only the 200 ms gauge reveal.

## Definition of done (every task)
1. Code runs; you ran it and saw the output.
2. Tests for the new code pass (`make test`).
3. No edits outside your folder.
4. docs/PROGRESS.md updated: done / broken / next (3 lines).
