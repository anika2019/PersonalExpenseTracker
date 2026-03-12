import streamlit as st
import requests
from datetime import datetime

API_URL = "http://localhost:8000"

# Must match backend db_helper.COLUMNS (except DATE - set from date picker)
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
NUMERIC_COLUMNS = [
    "INCOME",
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

# All form widget keys; cleared from session state after save so form refreshes to zero
FORM_INPUT_KEYS = (
    "inp_INCOME",
    "inp_SOURCE",
    "inp_HOME_LOAN",
    "inp_M_F",
    "inp_NEETU",
    "inp_GROCERY",
    "inp_MOB",
    "inp_SCHOOL",
    "inp_AJIT",
    "inp_CREDIT",
    "inp_MOVIE",
    "inp_TRANSPORT",
    "inp_SHOPPING",
    "inp_ELECTRIC",
    "inp_OTHERS",
)

# Date format used across app and Excel: dd-mm-yyyy
DATE_FMT_DISPLAY = "%d-%m-%Y"
DATE_FMT_API = "%Y-%m-%d"  # API still accepts YYYY-MM-DD; backend converts to dd-mm-yyyy


def _safe_float(val, default=0.0):
    if val is None or val == "":
        return default
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def _fmt_date(d) -> str:
    """Format date for display and Excel: dd-mm-yyyy."""
    if hasattr(d, "strftime"):
        return d.strftime(DATE_FMT_DISPLAY)
    return str(d)


def add_update_tab():
    selected_date = st.date_input(
        "Select Date",
        value=datetime.now().date(),
        key="add_update_date",
        format="DD-MM-YYYY",
    )
    date_str = selected_date.strftime(DATE_FMT_API)

    # Fetch existing data for this date
    try:
        response = requests.get(f"{API_URL}/expenses/{date_str}", timeout=5)
        if response.status_code == 200:
            existing_rows = response.json()
        else:
            existing_rows = []
    except requests.RequestException:
        st.error("Could not connect to the server. Is the backend running on port 8000?")
        existing_rows = []

    # Pre-fill from first row if we have data (clear income/source after a successful save)
    just_saved = st.session_state.get("add_update_just_saved", False)
    if existing_rows:
        st.subheader(f"Existing data for {_fmt_date(selected_date)}")
        st.dataframe(existing_rows, use_container_width=True, hide_index=True)
        if just_saved:
            first = {}
            st.session_state.add_update_just_saved = False
            for k in FORM_INPUT_KEYS:
                st.session_state.pop(k, None)
        else:
            first = existing_rows[0]
    else:
        first = {}
        if just_saved:
            st.session_state.add_update_just_saved = False
            for k in FORM_INPUT_KEYS:
                st.session_state.pop(k, None)

    st.subheader(f"Add / Update expense for {_fmt_date(selected_date)}")
    # After save: all form values 0 / empty; else use first row or defaults
    if just_saved:
        income_default = 0.0
        source_default = ""
        homeloan_default = mutualfund_default = neetu_default = 0.0
        grocery_default = mobile_default = school_default = ajit_default = 0.0
        credit_default = movie_default = transport_default = shopping_default = 0.0
        electric_default = others_default = 0.0
    else:
        income_default = _safe_float(first.get("INCOME")) if first else 0.0
        source_default = str(first.get("SOURCE", "") or "") if first else ""
        homeloan_default = _safe_float(first.get("HOMELOAN")) if first else 0.0
        mutualfund_default = _safe_float(first.get("MUTUALFUND")) if first else 0.0
        neetu_default = _safe_float(first.get("NEETU")) if first else 0.0
        grocery_default = _safe_float(first.get("GROCERYOUTSIDEFOODMED")) if first else 0.0
        mobile_default = _safe_float(first.get("MOBILEINTERNET")) if first else 0.0
        school_default = _safe_float(first.get("SCHOOLFEE")) if first else 0.0
        ajit_default = _safe_float(first.get("AJITCOURSE")) if first else 0.0
        credit_default = _safe_float(first.get("CREDITCARD")) if first else 0.0
        movie_default = _safe_float(first.get("MOVIEENTERTAINMENT")) if first else 0.0
        transport_default = _safe_float(first.get("TRANSPORT")) if first else 0.0
        shopping_default = _safe_float(first.get("SHOPPING")) if first else 0.0
        electric_default = _safe_float(first.get("ELECTRIC")) if first else 0.0
        others_default = _safe_float(first.get("OTHERS")) if first else 0.0

    form_version = st.session_state.get("add_update_form_version", 0)
    # Versioned keys so after save the form is brand new and all fields show zero
    key_suffix = f"_{form_version}"
    with st.form(key=f"expense_form_{form_version}"):
        row = {}
        row["INCOME"] = st.number_input(
            "INCOME",
            min_value=0.0,
            step=1.0,
            value=income_default,
            key=f"inp_INCOME{key_suffix}",
        )
        row["SOURCE"] = st.text_input(
            "SOURCE",
            value=source_default,
            key=f"inp_SOURCE{key_suffix}",
        )
        row["HOMELOAN"] = st.number_input(
            "Home Loan",
            min_value=0.0,
            step=1.0,
            value=homeloan_default,
            key=f"inp_HOME_LOAN{key_suffix}",
        )
        row["MUTUALFUND"] = st.number_input(
            "Mutual Fund",
            min_value=0.0,
            step=1.0,
            value=mutualfund_default,
            key=f"inp_M_F{key_suffix}",
        )
        row["NEETU"] = st.number_input(
            "NEETU",
            min_value=0.0,
            step=1.0,
            value=neetu_default,
            key=f"inp_NEETU{key_suffix}",
        )
        row["GROCERYOUTSIDEFOODMED"] = st.number_input(
            "Grocery & Outside Food & Med",
            min_value=0.0,
            step=1.0,
            value=grocery_default,
            key=f"inp_GROCERY{key_suffix}",
        )
        row["MOBILEINTERNET"] = st.number_input(
            "Mobile & Internet",
            min_value=0.0,
            step=1.0,
            value=mobile_default,
            key=f"inp_MOB{key_suffix}",
        )
        row["SCHOOLFEE"] = st.number_input(
            "School Fee",
            min_value=0.0,
            step=1.0,
            value=school_default,
            key=f"inp_SCHOOL{key_suffix}",
        )
        row["AJITCOURSE"] = st.number_input(
            "Ajit Course",
            min_value=0.0,
            step=1.0,
            value=ajit_default,
            key=f"inp_AJIT{key_suffix}",
        )
        row["CREDITCARD"] = st.number_input(
            "Credit Card",
            min_value=0.0,
            step=1.0,
            value=credit_default,
            key=f"inp_CREDIT{key_suffix}",
        )
        row["MOVIEENTERTAINMENT"] = st.number_input(
            "Movie & Entertainment",
            min_value=0.0,
            step=1.0,
            value=movie_default,
            key=f"inp_MOVIE{key_suffix}",
        )
        row["TRANSPORT"] = st.number_input(
            "TRANSPORT",
            min_value=0.0,
            step=1.0,
            value=transport_default,
            key=f"inp_TRANSPORT{key_suffix}",
        )
        row["SHOPPING"] = st.number_input(
            "Shopping (Misc)",
            min_value=0.0,
            step=1.0,
            value=shopping_default,
            key=f"inp_SHOPPING{key_suffix}",
        )
        row["ELECTRIC"] = st.number_input(
            "ELECTRIC",
            min_value=0.0,
            step=1.0,
            value=electric_default,
            key=f"inp_ELECTRIC{key_suffix}",
        )
        row["OTHERS"] = st.number_input(
            "OTHERS",
            min_value=0.0,
            step=1.0,
            value=others_default,
            key=f"inp_OTHERS{key_suffix}",
        )

        submit = st.form_submit_button("Save")
        if submit:
            # Build full row with DATE (server will override DATE from URL)
            full_row = {col: row.get(col, "") for col in COLUMNS}
            full_row["DATE"] = date_str
            try:
                resp = requests.post(
                    f"{API_URL}/expenses/{date_str}",
                    json=[full_row],
                    timeout=5,
                )
                if resp.status_code == 200:
                    st.success("Expenses saved successfully!")
                    st.session_state.add_update_just_saved = True
                    st.session_state.add_update_form_version = (
                        st.session_state.get("add_update_form_version", 0) + 1
                    )
                    st.rerun()
                else:
                    st.error(f"Failed to save. Status: {resp.status_code}")
            except requests.RequestException as e:
                st.error(f"Could not connect to server: {e}") 
