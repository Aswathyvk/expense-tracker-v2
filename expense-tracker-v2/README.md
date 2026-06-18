# Expense Tracker

Personal expense tracker. Single user, runs locally, no deployment.
Frontend and backend are two fully independent pieces — separate folders,
separate processes, communicating only over HTTP.

## Stack & why

- **Backend:** Python + FastAPI (`backend/main.py`), one file. SQLite via
  the stdlib `sqlite3` module, no ORM — one table, no relations, so an ORM
  is pure overhead. Pydantic gives request validation for free; FastAPI
  gives interactive docs at `/docs` for free.
- **Frontend:** A single static HTML file (`frontend/index.html`), vanilla
  JS, inline CSS. No build step, no framework, no bundler. It is **not**
  served by the backend — open the file directly in a browser
  (`file://` URL) and it talks to the backend purely over `fetch()`.
- **Why split them:** the brief allows "any frontend or plain HTML/JS" and
  doesn't require them to be one process. Keeping them separate processes
  forces an explicit, inspectable contract (HTTP + CORS) between the two
  instead of folding the UI into the API server. Cost: CORS has to be
  configured (see tradeoffs below). Worth it for a clean separation of
  concerns at basically zero extra effort.

## How to run

**1. Backend** (Python 3.9+):
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Leave this running. API docs at http://127.0.0.1:8000/docs — useful for
poking at endpoints directly.

**2. Frontend:**
Just open `frontend/index.html` in any browser (double-click it, or
File → Open in your browser). No server, no build step. It looks for the
backend at `http://127.0.0.1:8000/api` — that's the only place the backend
location is configured (top of the `<script>` block), change it there if
you run the API somewhere else.

The header shows a live "backend connected / unreachable" badge so it's
obvious if the two pieces aren't talking.

## What's implemented

1. **Add expense** — title, amount, category (Food / Transport / Shopping /
   Bills / Entertainment / Other), date (defaults to today — computed in
   local time, not UTC, so it's correct for IST), optional note.
2. **List all expenses** — sorted by date, most recent first (ties broken
   by id descending), all fields shown.
3. **Edit / delete** any expense.
4. **Monthly summary** — total spent + breakdown by category, for any month
   (defaults to current month).
5. **Filters** — by category, date range (from/to), and title (partial,
   case-insensitive). Filters combine (AND).

## Edge cases handled

- Empty list / empty month → clear empty state, not a blank screen.
- Amount must be a positive number (rejects 0, negative, non-numeric,
  unreasonably large).
- Title required, rejected if blank/whitespace-only.
- Category restricted to the fixed list, enforced server-side (not just
  the UI dropdown — the API itself rejects an invalid category).
- Date format validated (`YYYY-MM-DD`); a missing date silently defaults
  to today rather than erroring.
- "Weird" date ranges (`from` after `to`) don't crash — they return zero
  results, same as any other filter combo with no matches.
- Editing/deleting a non-existent id returns a clean 404, not a stack trace.
- A literal `%` or `_` typed into the title filter is treated as a literal
  character, not a SQL wildcard (escaped before the `LIKE` query).
- Every frontend network call is wrapped in try/catch — if the backend
  isn't running, the UI says so instead of failing silently or throwing.
- Add/Save button disables while a request is in flight, so a fast
  double-click can't create a duplicate expense.
- All validation happens server-side (Pydantic), so the API can't be fed
  bad data even if someone bypasses the HTML form entirely (e.g. via
  `/docs` or curl).

## What's skipped (and why)

- **Auth / multi-user** — explicitly out of scope per the brief.
- **Deployment** — local only, per the brief.
- **Automated test suite** — skipped to prioritize the 5 functional
  requirements within the time box. Instead, every endpoint and validation
  branch (bad amount, bad category, blank title, bad date, 404s, empty
  states, LIKE-wildcard escaping) was manually smoke-tested end-to-end
  before calling it done.
- **Multi-currency** — brief specifies single local currency, no conversion.
- **Pagination** — not implemented; expense counts for a personal tracker
  are small enough to return the full filtered list. Would add if list
  sizes grew large.

## Known tradeoffs / rough edges

- **CORS is wildcard (`allow_origins=["*"]`)** so the frontend works
  whether it's opened as a local file or served from any port. This is
  fine for a local single-user tool but is *not* what you'd ship for a
  real deployment — there, CORS should be locked to the actual frontend
  origin.
- Amounts are stored as SQLite `REAL` (float), not fixed-point. Fine at
  this scale/volume; a production money system would use integer
  minor-units or `Decimal` to avoid float rounding drift over time.
- No confirmation beyond a basic `confirm()` dialog before delete.
- Currency symbol (₹) is hardcoded in the UI, not configurable.
- No optimistic UI updates — every action re-fetches from the server
  after the request completes. Simpler, slightly more round-trips; not a
  problem at this scale.
