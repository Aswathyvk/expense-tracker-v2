"""
Expense Tracker — Backend (API only)

FastAPI + SQLite (stdlib sqlite3, no ORM — one table, no relations, ORM would
be pure overhead at this scale).

This process serves JSON only. The frontend is a fully separate static
HTML/JS file (../frontend/index.html) that talks to this API over HTTP.
CORS is enabled wildcard ("*") deliberately — see README for the tradeoff.

Run:
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000

Interactive API docs: http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, List
import sqlite3
import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")
CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Other"]

app = FastAPI(title="Expense Tracker API", version="1.0.0")

# Local single-user tool, frontend is a static file opened from disk (file://
# origin) or served from any port — wildcard CORS is the pragmatic choice
# here. For a shared/deployed version this should be locked down to the
# actual frontend origin instead of "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            note TEXT
        )
        """
    )
    conn.commit()
    conn.close()


init_db()


# ---------- Schemas ----------

class ExpenseIn(BaseModel):
    title: str
    amount: float
    category: str
    date: Optional[str] = Field(default=None, validate_default=True)
    note: Optional[str] = None

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v):
        v = (v or "").strip()
        if not v:
            raise ValueError("Title cannot be empty")
        if len(v) > 200:
            raise ValueError("Title too long (max 200 chars)")
        return v

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v):
        if v is None:
            raise ValueError("Amount is required")
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        if v > 100_000_000:
            raise ValueError("Amount is unreasonably large")
        return round(v, 2)

    @field_validator("category")
    @classmethod
    def category_valid(cls, v):
        if v not in CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(CATEGORIES)}")
        return v

    @field_validator("date")
    @classmethod
    def date_valid(cls, v):
        # Runs even when omitted (validate_default=True) so a missing date
        # reliably becomes today's date rather than landing in the DB as NULL.
        if v is None or v == "":
            return datetime.date.today().isoformat()
        try:
            datetime.date.fromisoformat(v)
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v

    @field_validator("note")
    @classmethod
    def note_len(cls, v):
        if v and len(v) > 2000:
            raise ValueError("Note too long (max 2000 chars)")
        return v


class ExpenseOut(BaseModel):
    id: int
    title: str
    amount: float
    category: str
    date: str
    note: Optional[str] = ""


class SummaryOut(BaseModel):
    month: str
    total: float
    breakdown: Dict[str, float]


class DeleteOut(BaseModel):
    deleted: int


def escape_like(value: str) -> str:
    """Escape SQL LIKE wildcards so a literal % or _ typed by the user
    doesn't act as a pattern character."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


# ---------- Routes ----------

@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/categories", response_model=List[str])
def list_categories():
    return CATEGORIES


@app.post("/api/expenses", response_model=ExpenseOut)
def create_expense(expense: ExpenseIn):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO expenses (title, amount, category, date, note) VALUES (?, ?, ?, ?, ?)",
        (expense.title, expense.amount, expense.category, expense.date, expense.note or ""),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM expenses WHERE id = ?", (cur.lastrowid,)).fetchone()
    conn.close()
    return dict(row)


@app.get("/api/expenses", response_model=List[ExpenseOut])
def list_expenses(
    category: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    title: Optional[str] = Query(None),
):
    query = "SELECT * FROM expenses WHERE 1=1"
    params: list = []

    if category and category in CATEGORIES:
        query += " AND category = ?"
        params.append(category)

    if date_from:
        try:
            datetime.date.fromisoformat(date_from)
        except ValueError:
            raise HTTPException(400, "date_from must be YYYY-MM-DD")
        query += " AND date >= ?"
        params.append(date_from)

    if date_to:
        try:
            datetime.date.fromisoformat(date_to)
        except ValueError:
            raise HTTPException(400, "date_to must be YYYY-MM-DD")
        query += " AND date <= ?"
        params.append(date_to)

    if title:
        query += " AND title LIKE ? ESCAPE '\\'"
        params.append(f"%{escape_like(title.strip())}%")

    # A "weird" range (from > to) needs no special-casing — it just yields
    # zero matching rows, same as any other filter combo with no matches.
    query += " ORDER BY date DESC, id DESC"

    conn = get_db()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/api/expenses/{expense_id}", response_model=ExpenseOut)
def get_expense(expense_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "Expense not found")
    return dict(row)


@app.put("/api/expenses/{expense_id}", response_model=ExpenseOut)
def update_expense(expense_id: int, expense: ExpenseIn):
    conn = get_db()
    existing = conn.execute("SELECT id FROM expenses WHERE id = ?", (expense_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(404, "Expense not found")
    conn.execute(
        "UPDATE expenses SET title=?, amount=?, category=?, date=?, note=? WHERE id=?",
        (expense.title, expense.amount, expense.category, expense.date, expense.note or "", expense_id),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
    conn.close()
    return dict(row)


@app.delete("/api/expenses/{expense_id}", response_model=DeleteOut)
def delete_expense(expense_id: int):
    conn = get_db()
    existing = conn.execute("SELECT id FROM expenses WHERE id = ?", (expense_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(404, "Expense not found")
    conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()
    return {"deleted": expense_id}


@app.get("/api/summary", response_model=SummaryOut)
def monthly_summary(month: Optional[str] = Query(None, description="YYYY-MM, defaults to current month")):
    if not month:
        month = datetime.date.today().strftime("%Y-%m")
    else:
        try:
            datetime.datetime.strptime(month, "%Y-%m")
        except ValueError:
            raise HTTPException(400, "month must be YYYY-MM")

    conn = get_db()
    rows = conn.execute(
        "SELECT category, SUM(amount) as total FROM expenses WHERE date LIKE ? GROUP BY category",
        (f"{month}%",),
    ).fetchall()
    total_row = conn.execute(
        "SELECT SUM(amount) as total FROM expenses WHERE date LIKE ?", (f"{month}%",)
    ).fetchone()
    conn.close()

    breakdown = {r["category"]: round(r["total"], 2) for r in rows}
    total = round(total_row["total"], 2) if total_row["total"] else 0.0
    return {"month": month, "total": total, "breakdown": breakdown}
