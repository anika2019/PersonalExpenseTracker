"""
FastAPI server connecting the MySQL data layer (db_helper) to the Streamlit frontend.
"""
import math
from datetime import datetime, timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend import db_helper

app = FastAPI(title="Expense Tracker API")

app.add_middleware(
    CORSMiddleware,
    # Allow Streamlit Cloud frontend + local dev.
    # Set FRONTEND_ORIGIN on Render if you want to restrict further.
    allow_origins=[
        "http://localhost:8501",
        "https://personalexpensetracker-cg6od6hcwjbxatihihk3jx.streamlit.app/",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Frontend uses YYYY-MM-DD; db_helper layer uses dd-mm-yyyy
def _frontend_date_to_excel(date_str: str) -> str:
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return d.strftime("%d-%m-%Y")


# Expense columns (exclude DATE, INCOME, SOURCE) for analytics
_EXPENSE_COLUMNS = [
    c for c in db_helper.COLUMNS
    if c not in ("DATE", "INCOME", "SOURCE")
]

# Column -> display name (for analytics responses)
COLUMN_TO_CATEGORY = {
    "HOMELOAN": "Home Loan",
    "MUTUALFUND": "Mutual Fund",
    "NEETU": "Neetu",
    "GROCERYOUTSIDEFOODMED": "Grocery & outside food & med",
    "MOBILEINTERNET": "Mobile & internet",
    "SCHOOLFEE": "School fee",
    "AJITCOURSE": "Ajit course",
    "CREDITCARD": "Credit card",
    "MOVIEENTERTAINMENT": "Movie & entertainment",
    "TRANSPORT": "Transport",
    "SHOPPING": "Shopping",
    "ELECTRIC": "Electric",
    "OTHERS": "Others",
}


@app.get("/expenses/{date_str}")
def get_expenses(date_str: str):
    """Return all rows for the given date. Each row has all columns (DATE, INCOME, SOURCE, HOME_LOAN, ...)."""
    excel_date = _frontend_date_to_excel(date_str)
    rows = db_helper.get_expenses_for_date(excel_date)
    return rows


@app.post("/expenses/{date_str}")
def save_expenses(date_str: str, body: list[dict]):
    """Save rows for the given date. Body: list of dicts with keys matching db_helper.COLUMNS (DATE set from date_str)."""
    excel_date = _frontend_date_to_excel(date_str)
    rows = []
    for e in body:
        row = {col: e.get(col, "") for col in db_helper.COLUMNS}
        row["DATE"] = excel_date
        rows.append(row)
    db_helper.save_expenses_for_date(excel_date, rows)
    return {"status": "ok"}


@app.post("/analytics/")
def analytics_by_category(payload: dict):
    """Return category totals and percentages for date range. Body: {start_date, end_date} (YYYY-MM-DD)."""
    start = _frontend_date_to_excel(payload["start_date"])
    end = _frontend_date_to_excel(payload["end_date"])
    all_rows = db_helper.get_expenses_in_range(start, end)
    start_d = datetime.strptime(start, "%d-%m-%Y")
    end_d = datetime.strptime(end, "%d-%m-%Y")
    totals = {}
    for row in all_rows:
        try:
            dt_str = row.get("DATE", "")
            if not dt_str:
                continue
            row_d = datetime.strptime(str(dt_str)[:10], "%d-%m-%Y")
            if start_d <= row_d <= end_d:
                for col in _EXPENSE_COLUMNS:
                    try:
                        val = float(row.get(col) or 0)
                    except (TypeError, ValueError):
                        continue
                    cat = COLUMN_TO_CATEGORY.get(col, col)
                    totals[cat] = totals.get(cat, 0) + val
        except (ValueError, TypeError):
            continue
    total_sum = sum(totals.values()) or 1
    return {
        cat: {"total": t, "percentage": (t / total_sum) * 100}
        for cat, t in totals.items()
    }


@app.post("/analytics/monthly/")
def analytics_monthly(payload: dict):
    """Return monthly totals for date range. Body: {start_date, end_date} (YYYY-MM-DD)."""
    start = _frontend_date_to_excel(payload["start_date"])
    end = _frontend_date_to_excel(payload["end_date"])
    rows = db_helper.get_expenses_in_range(start, end)
    by_month: dict[str, float] = {}
    for row in rows:
        try:
            dt_str = row.get("DATE", "")
            if not dt_str:
                continue
            row_d = datetime.strptime(str(dt_str)[:10], "%d-%m-%Y")
            month_key = row_d.strftime("%Y-%m")
            total = 0.0
            for col in _EXPENSE_COLUMNS:
                total += _safe_float(row.get(col))
            by_month[month_key] = by_month.get(month_key, 0.0) + total
        except (ValueError, TypeError):
            continue
    return {month: {"total": t} for month, t in by_month.items()}


@app.post("/analytics/monthly/categories/")
def analytics_monthly_by_category(payload: dict):
    """
    Return category-wise totals for a selected month.
    Body: {year: int, month: int} where month is 1-12.
    """
    year = int(payload["year"])
    month = int(payload["month"])
    # First and last day of the month in API format
    start_api = f"{year:04d}-{month:02d}-01"
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)
    end_api = (next_month - timedelta(days=1)).strftime("%Y-%m-%d")

    start = _frontend_date_to_excel(start_api)
    end = _frontend_date_to_excel(end_api)
    rows = db_helper.get_expenses_in_range(start, end)

    totals = {}
    for row in rows:
        for col in _EXPENSE_COLUMNS:
            val = _safe_float(row.get(col))
            if val == 0:
                continue
            cat = COLUMN_TO_CATEGORY.get(col, col)
            totals[cat] = totals.get(cat, 0.0) + val

    return {"year": year, "month": month, "by_category": {k: round(v, 2) for k, v in totals.items()}}


def _safe_float(x, default: float = 0.0) -> float:
    """Convert to float; treat NaN, None, and invalid as default."""
    if x is None or x == "":
        return default
    try:
        v = float(x)
        return default if (math.isnan(v) or math.isinf(v)) else v
    except (TypeError, ValueError):
        return default


def _month_summary(start_date: str, end_date: str) -> dict:
    """Compute total_income, total_expenses, balance, by_category for the date range."""
    start = _frontend_date_to_excel(start_date)
    end = _frontend_date_to_excel(end_date)
    rows = db_helper.get_expenses_in_range(start, end)
    total_income = 0.0
    total_expenses = 0.0
    by_category = {}
    for row in rows:
        total_income += _safe_float(row.get("INCOME"))
        for col in _EXPENSE_COLUMNS:
            val = _safe_float(row.get(col))
            total_expenses += val
            cat = COLUMN_TO_CATEGORY.get(col, col)
            by_category[cat] = by_category.get(cat, 0) + val
    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "balance": round(total_income - total_expenses, 2),
        "by_category": {k: round(v, 2) for k, v in by_category.items()},
    }


@app.get("/analytics/month-summary")
def get_month_summary(start_date: str, end_date: str):
    """Return total income, total expenses, balance, and category-wise expenses for the date range. Query: start_date, end_date (YYYY-MM-DD)."""
    return _month_summary(start_date, end_date)


@app.post("/analytics/month-summary")
def post_month_summary(payload: dict):
    """Return total income, total expenses, balance, and category-wise expenses. Body: {start_date, end_date} (YYYY-MM-DD)."""
    return _month_summary(payload["start_date"], payload["end_date"])
