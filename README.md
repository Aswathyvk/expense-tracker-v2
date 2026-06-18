# 💰 Expense Tracker

A simple, fast, single-user expense tracking application built as a small full-stack web app.

The application allows users to record daily expenses, view spending history, edit or delete entries, filter expenses, and view monthly spending summaries.

Designed for local execution with a completely independent frontend and backend communicating exclusively through HTTP.

---

## ✨ Features

### Expense Management

* Add expenses with:

  * Title
  * Amount
  * Category
  * Date
  * Optional note
* View all expenses sorted by most recent date
* Edit existing expenses
* Delete expenses

### Monthly Summary

* Total amount spent for a selected month
* Category-wise spending breakdown

### Filtering

Filter expenses using:

* Category
* Date range (From / To)
* Title search (partial, case-insensitive)

### User Experience

* Empty-state handling
* Live backend connectivity status
* Form validation
* Duplicate submission prevention
* Responsive layout
* Clear error handling

---

## 🏗️ Architecture

The application intentionally keeps the frontend and backend as completely independent components.

```text
expense-tracker/
│
├── backend/
│   ├── main.py
│   ├── expenses.db
│   ├── requirements.txt
│
└── frontend/
    └── index.html
```

```text
Browser (Frontend)
        │
        │ HTTP (fetch)
        ▼
 FastAPI Backend
        │
        ▼
     SQLite
```

The frontend is not served by the backend and can be opened directly in any browser.

---

## 🛠️ Tech Stack

### Backend

* Python 3.9+
* FastAPI
* SQLite
* Pydantic

### Frontend

* HTML5
* Vanilla JavaScript
* Inline CSS

### Why This Stack?

#### FastAPI

* Lightweight and fast
* Built-in request validation through Pydantic
* Interactive API documentation at `/docs`

#### SQLite

* Zero configuration
* Perfect fit for a small local application
* No external database installation required

#### Vanilla JavaScript

* No build process
* No framework overhead
* Faster development within the assessment time limit

---

## 🚀 Getting Started

### Prerequisites

* Python 3.9+
* pip

---

## Backend Setup

Navigate to the backend folder:

```bash
cd backend
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the API server:

```bash
uvicorn main:app --reload --port 8000
```

Backend will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Frontend Setup

Open the frontend directly in your browser:

```text
frontend/index.html
```

No build step.

No npm install.

No frontend server required.

The frontend communicates with:

```text
http://127.0.0.1:8000/api
```

If the backend is running elsewhere, update the API URL at the top of the JavaScript section in `index.html`.

---

## 📋 Supported Categories

* Food
* Transport
* Shopping
* Bills
* Entertainment
* Other

---

## 📊 Monthly Summary

The application provides:

* Total spending for a selected month
* Category-wise expense breakdown

Example:

```text
June 2026

Total Spent: ₹12,450

Food           ₹3,200
Transport      ₹1,500
Shopping       ₹4,750
Bills          ₹2,000
Entertainment  ₹1,000
```

---

## 🔍 Filtering

Users can combine multiple filters simultaneously:

| Filter    | Description          |
| --------- | -------------------- |
| Category  | Exact category match |
| Date From | Start date           |
| Date To   | End date             |
| Title     | Partial title search |

Filters are combined using logical AND.

---

## ✅ Validation & Edge Cases

### Expense Validation

* Title is required
* Blank or whitespace-only titles are rejected
* Amount must be positive
* Invalid categories are rejected
* Date format must be valid (`YYYY-MM-DD`)

### Application Behavior

* Empty expense list handled gracefully
* Empty monthly summaries display meaningful messages
* Non-existent records return clean 404 responses
* Backend outages are surfaced in the UI
* Duplicate submissions prevented while requests are in progress
* Literal `%` and `_` characters in search terms are safely escaped

---

## 🔗 API Endpoints

| Method | Endpoint             | Description     |
| ------ | -------------------- | --------------- |
| GET    | `/api/expenses`      | List expenses   |
| POST   | `/api/expenses`      | Create expense  |
| PUT    | `/api/expenses/{id}` | Update expense  |
| DELETE | `/api/expenses/{id}` | Delete expense  |
| GET    | `/api/summary`       | Monthly summary |

Interactive documentation:

```text
http://127.0.0.1:8000/docs
```

---

## ⚖️ Design Decisions & Tradeoffs

### Separate Frontend & Backend

The frontend and backend run independently and communicate only through HTTP.

**Benefits**

* Clear separation of concerns
* Easier API testing
* Technology-agnostic architecture

**Tradeoff**

* Requires CORS configuration

---

### SQLite REAL for Amount Storage

Amounts are stored as SQLite `REAL`.

**Benefits**

* Simpler implementation
* Suitable for local personal tracking

**Tradeoff**

* Production financial systems should use fixed-point precision (`Decimal` or integer minor units).

---

### Wildcard CORS Configuration

```python
allow_origins=["*"]
```

Used to support opening the frontend directly from the local filesystem.

**Tradeoff**

* Suitable for local development only
* Production deployments should restrict origins

---

## ❌ Out of Scope

The following items were intentionally excluded to prioritize the required functionality within the assessment time limit:

* Authentication
* Multi-user support
* Deployment
* Currency conversion
* Pagination
* Reporting exports
* Automated test suite

---

## 🔮 Future Improvements

* User authentication
* Multi-user support
* CSV/Excel export
* Charts and analytics
* Configurable currencies
* Dark mode
* Automated test coverage
* Docker support
* Pagination for large datasets

---

## 🎯 Assessment Goals Covered

* ✅ Add expenses
* ✅ View expenses
* ✅ Edit expenses
* ✅ Delete expenses
* ✅ Monthly summary
* ✅ Category breakdown
* ✅ Filtering
* ✅ Input validation
* ✅ Error handling
* ✅ Clean API design
* ✅ Local execution

---

## License

This project was created as part of a software engineering practical assessment and is intended for demonstration and evaluation purposes.
