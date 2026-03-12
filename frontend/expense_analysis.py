import streamlit as st
from Add_Update import add_update_tab
from Expense_Category import total_expense_by_category
from Analytics_by_Month import analytics_by_month


st.set_page_config(page_title="Personal Expense Tracker", layout="wide")
st.title("Expense Tracking System")

# Session state for form refresh after save (used by Add_Update tab)
if "add_update_just_saved" not in st.session_state:
    st.session_state.add_update_just_saved = False
if "add_update_form_version" not in st.session_state:
    st.session_state.add_update_form_version = 0

tab1, tab2, tab3 = st.tabs(
    ["Add/Update", "Total Expenses By Category", "Analytics by Month"]
)

with tab1:
    add_update_tab()

with tab2:
    total_expense_by_category()

with tab3:
    analytics_by_month()

