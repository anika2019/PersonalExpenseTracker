import calendar
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

from config import get_api_url

API_URL = get_api_url()


def analytics_by_month():
    st.title("Monthly Category-wise Expenses")

    now = datetime.now()
    month_names = list(calendar.month_name)[1:]

    col1, col2 = st.columns(2)
    with col1:
        month_name = st.selectbox(
            "Month",
            options=month_names,
            index=now.month - 1,
            key="analytics_month_name",
        )
    with col2:
        year = st.selectbox(
            "Year",
            options=list(range(now.year - 5, now.year + 2)),
            index=5,
            key="analytics_year",
        )

    month = month_names.index(month_name) + 1

    if st.button("Get Category-wise Analytics", key="btn_monthly_category"):
        payload = {"year": int(year), "month": int(month)}
        try:
            resp = requests.post(
                f"{API_URL}/analytics/monthly/categories/",
                json=payload,
                timeout=8,
            )
            if resp.status_code != 200:
                st.error(f"Server error: {resp.status_code}")
                return
            data = resp.json()
        except requests.RequestException:
            st.error("Could not connect to the server. Is the backend running on port 8000?")
            return

        by_cat = data.get("by_category", {}) or {}

        st.subheader(f"{month_name} {year}")
        if not by_cat:
            st.info("No expense data found for this month.")
            with st.expander("View API response"):
                st.json(data)
            return

        df = pd.DataFrame(list(by_cat.items()), columns=["Category", "Amount"])
        df = df.sort_values("Amount", ascending=False)

        st.bar_chart(df.set_index("Category")["Amount"], use_container_width=True)
        df_display = df.copy()
        df_display["Amount"] = df_display["Amount"].map("{:,.2f}".format)
        st.table(df_display)

        with st.expander("View API response"):
            st.json(data)