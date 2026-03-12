import logging
import os
from contextlib import contextmanager
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()
import psycopg2
from psycopg2.extras import RealDictCursor


# Columns used across frontend/backend for a single day's record.
# Names are uppercased versions of the actual DB columns (Supabase/PostgreSQL).
COLUMNS = [
    "DATE", 
    "INCOME",
    "SOURCE",
    "HOMELOAN", 
    "MUTUALFUND",
    "NEETU",
    "GROCERYOUTSIDEFOODMED",
    "MOBILEINTERNET",
    "SCHOOLFEE",
    "AJITCOURSE",
    "CREDITCARD",
    "MOVIEENTERTAINMENT",
    "TRANSPORT",
    "SHOPPING",
    "ELECTRIC",
    "OTHERS",
]

DATE_FMT = "%d-%m-%Y"  # dd-mm-yyyy used between API/frontend and DB helper


# Configure custom logger
logger = logging.getLogger("db_helper")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
file_handler = logging.FileHandler("server.log")
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def get_db_connection():
    """Create and return a connection to Supabase (PostgreSQL). Uses DATABASE_URL env var."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        logger.error("DATABASE_URL environment variable is not set")
        return None
    try:
        connection = psycopg2.connect(url)
        return connection
    except psycopg2.Error as e:
        logger.error("Error while connecting to Supabase: %s", e)
        return None


@contextmanager
def get_cursor():
    """Context manager yielding a dict-like cursor and handling commit/close safely."""
    conn = get_db_connection()
    if conn is None:
        raise RuntimeError("Could not connect to database (check DATABASE_URL)")
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        logger.exception("Database operation failed")
        raise
    finally:
        cursor.close()
        conn.close()


def _parse_date(date_str: str) -> datetime.date:
    """Parse dd-mm-yyyy string to date object."""
    return datetime.strptime(date_str, DATE_FMT).date()


def get_expenses_for_date(date_str: str) -> list[dict]:
    """
    Fetch all expense records for a given date (date_str in dd-mm-yyyy).

    Returns a list of dicts with keys matching COLUMNS.
    """
    target_date = _parse_date(date_str)
    query = """
        SELECT
            TO_CHAR("date"::date, 'DD-MM-YYYY') AS "DATE",
            income AS "INCOME",
            source AS "SOURCE",
            homeloan AS "HOMELOAN",
            mutualfund AS "MUTUALFUND",
            neetu AS "NEETU",
            "GroceryOutsideFoodMed" AS "GROCERYOUTSIDEFOODMED",
            "MobileInternet" AS "MOBILEINTERNET",
            "SchoolFee" AS "SCHOOLFEE",
            ajitcourse AS "AJITCOURSE",
            creditcard AS "CREDITCARD",
            "MovieEntertainment" AS "MOVIEENTERTAINMENT",
            transport AS "TRANSPORT",
            shopping AS "SHOPPING",
            electric AS "ELECTRIC",
            others AS "OTHERS"
        FROM expenses
        WHERE "date"::date = %s
    """
    with get_cursor() as cur:
        cur.execute(query, (target_date,))
        rows = cur.fetchall()
    return rows or []


def save_expenses_for_date(date_str: str, records: list[dict]) -> None:
    """
    Append new expense records for a given date.

    records: list of dicts with keys matching COLUMNS.
    """
    target_date = _parse_date(date_str)
    with get_cursor() as cur:
        if not records:
            return
        insert_sql = """
            INSERT INTO expenses (
                "date",
                income,
                source,
                homeloan,
                mutualfund,
                neetu,
                "GroceryOutsideFoodMed",
                "MobileInternet",
                "SchoolFee",
                ajitcourse,
                creditcard,
                "MovieEntertainment",
                transport,
                shopping,
                electric,
                others
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        for rec in records:
            vals = (
                target_date,
                rec.get("INCOME", 0) or 0,
                rec.get("SOURCE", "") or "",
                rec.get("HOMELOAN", 0) or 0,
                rec.get("MUTUALFUND", 0) or 0,
                rec.get("NEETU", 0) or 0,
                rec.get("GROCERYOUTSIDEFOODMED", 0) or 0,
                rec.get("MOBILEINTERNET", 0) or 0,
                rec.get("SCHOOLFEE", 0) or 0,
                rec.get("AJITCOURSE", 0) or 0,
                rec.get("CREDITCARD", 0) or 0,
                rec.get("MOVIEENTERTAINMENT", 0) or 0,
                rec.get("TRANSPORT", 0) or 0,
                rec.get("SHOPPING", 0) or 0,
                rec.get("ELECTRIC", 0) or 0,
                rec.get("OTHERS", 0) or 0,
            )
            cur.execute(insert_sql, vals)


def get_expenses_in_range(start_date_str: str, end_date_str: str) -> list[dict]:
    """
    Fetch all expense records where DATE is between start_date_str and end_date_str (inclusive).
    Date strings are dd-mm-yyyy.

    Returns list of dicts with keys matching COLUMNS.
    """
    start_date = _parse_date(start_date_str)
    end_date = _parse_date(end_date_str)
    query = """
        SELECT
            TO_CHAR("date"::date, 'DD-MM-YYYY') AS "DATE",
            income AS "INCOME",
            source AS "SOURCE",
            homeloan AS "HOMELOAN",
            mutualfund AS "MUTUALFUND",
            neetu AS "NEETU",
            "GroceryOutsideFoodMed" AS "GROCERYOUTSIDEFOODMED",
            "MobileInternet" AS "MOBILEINTERNET",
            "SchoolFee" AS "SCHOOLFEE",
            ajitcourse AS "AJITCOURSE",
            creditcard AS "CREDITCARD",
            "MovieEntertainment" AS "MOVIEENTERTAINMENT",
            transport AS "TRANSPORT",
            shopping AS "SHOPPING",
            electric AS "ELECTRIC",
            others AS "OTHERS"
        FROM expenses
        WHERE "date"::date BETWEEN %s AND %s
    """
    with get_cursor() as cur:
        cur.execute(query, (start_date, end_date))
        rows = cur.fetchall()
    return rows or []