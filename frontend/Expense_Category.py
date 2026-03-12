import calendar
import streamlit as st
from datetime import datetime
import requests
import pandas as pd

from config import get_api_url

API_URL = get_api_url()
# Date format used across app and Excel: dd-mm-yyyy
DATE_FMT_DISPLAY = "%d-%m-%Y"
DATE_FMT_API = "%Y-%m-%d"


def _fmt_date(d) -> str:
    """Format date for display: dd-mm-yyyy."""
    if hasattr(d, "strftime"):
        return d.strftime(DATE_FMT_DISPLAY)
    return str(d)


def total_expense_by_category():
    st.title("Expense Breakdown By Category")

    
    start_date = datetime.now().replace(day=1)
    last_day = calendar.monthrange(datetime.now().year, datetime.now().month)[1]
    end_date = datetime.now().replace(day=last_day)

    if st.button("Get month summary"):
        payload = {
            "start_date": start_date.strftime(DATE_FMT_API),
            "end_date": end_date.strftime(DATE_FMT_API),
        }
        try:
            response = requests.post(
                f"{API_URL}/analytics/month-summary",
                json=payload,
                timeout=5,
            )
            if response.status_code != 200:
                st.error("Failed to load data from server.")
                return
            data = response.json()
        except requests.RequestException:
            st.error("Could not connect to the server. Is the backend running on port 8000?")
            return

        # Always show the three metrics (even when 0)
        st.subheader(f"Summary for {start_date.strftime('%B %Y')} ({_fmt_date(start_date)} – {_fmt_date(end_date)})")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Income", f"₹ {data.get('total_income', 0):,.2f}")
        with col2:
            st.metric("Total Expenses", f"₹ {data.get('total_expenses', 0):,.2f}")
        with col3:
            balance = data.get("balance", 0)
            st.metric("Balance (Income − Expenses)", f"₹ {balance:,.2f}")

        # Category-wise expenses: show chart/table only when there is data
        by_cat = data.get("by_category", {})
        if not by_cat:
            st.info("No category-wise expenses in this month.")
        else:
            st.subheader("Category-wise expenses")
            df = pd.DataFrame(
                list(by_cat.items()),
                columns=["Category", "Amount"],
            )
            df = df.sort_values("Amount", ascending=False)
            st.bar_chart(data=df.set_index("Category")["Amount"], use_container_width=True)
            df["Amount"] = df["Amount"].map("{:,.2f}".format)
            st.table(df)

        # Optional: show raw API response for debugging
        with st.expander("View API response"):
            st.json(data)
