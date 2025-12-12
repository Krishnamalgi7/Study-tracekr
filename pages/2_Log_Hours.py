import streamlit as st
import pandas as pd
from datetime import date


def app(storage):
    st.markdown("<h3>⏱️ Log Study Hours</h3>", unsafe_allow_html=True)

    user = st.session_state.get("user")
    if not user:
        st.warning("Please login to log hours.")
        return

    current_user_id = str(user.get("user_id"))

    # 1. LOAD PLANS
    plans_df = storage.read_csv("study_plans.csv")

    # --- FIX: HANDLE MISSING PLANS GRACEFULLY ---
    if plans_df.empty:
        st.info("You don't have any study plans yet. Go to **Add Plan** to create one!")
        return

    # Ensure user_id is string for matching
    plans_df["user_id"] = plans_df["user_id"].astype(str)

    # Filter for CURRENT USER only
    user_plans = plans_df[plans_df["user_id"] == current_user_id]

    if user_plans.empty:
        st.info("You don't have any study plans yet. Go to **Add Plan** to create one!")
        return
    # ---------------------------------------------

    # 2. FORM TO LOG HOURS
    with st.markdown("<div class='card'>", unsafe_allow_html=True):
        with st.form("log_hours_form"):
            # Select from active plans
            selected_subject = st.selectbox("Select Subject", user_plans["subject"].unique())

            c1, c2 = st.columns(2)
            hours_studied = c1.number_input("Hours Studied", 0.1, 24.0, 1.0, 0.5)
            study_date = c2.date_input("Date", value=date.today())

            notes = st.text_area("Notes (optional)", placeholder="What did you cover?")

            submitted = st.form_submit_button("✅ Save Log", type="primary")

            if submitted:
                # Prepare log entry
                log_entry = {
                    "user_id": current_user_id,
                    "subject": selected_subject,
                    "hours": hours_studied,
                    "date": str(study_date),
                    "notes": notes if notes else ""
                }

                # Use storage.append_row to save (it now handles the warning safely)
                storage.append_row("study_logs.csv", log_entry)

                st.success(f"Logged {hours_studied} hours for {selected_subject}!")