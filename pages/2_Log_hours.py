import streamlit as st
import pandas as pd
from datetime import date

def app(storage):
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Log Study Hours")
    st.write("Track your daily study progress.")

    user = st.session_state.user
    uid = user["user_id"]

    plans = storage.read_csv("study_plans.csv")
    logs = storage.read_csv("study_logs.csv")

    if plans is None or plans.empty:
        plans = pd.DataFrame(columns=["user_id", "subject", "goal", "planned_hours", "date"])
    if logs is None or logs.empty:
        logs = pd.DataFrame(columns=["user_id", "date", "subject", "hours_studied"])

    user_plans = plans[plans["user_id"] == uid]

    with st.form("log_form"):
        subjects = ["None"]
        if not user_plans.empty:
            subjects = sorted(user_plans["subject"].unique().tolist())

        subject = st.selectbox("Subject", subjects)
        hours = st.number_input("Hours Studied", min_value=0.0, step=0.5)
        entry_date = st.date_input("Date", date.today())
        submitted = st.form_submit_button("Log Hours")

    if submitted:
        if subject == "None":
            st.error("Please add a study plan first.")
        else:
            row = {
                "user_id": uid,
                "date": str(entry_date),
                "subject": subject,
                "hours_studied": hours
            }
            storage.append_row("study_logs.csv", row)
            st.success("Study hours logged.")
            st.rerun()

    user_logs = logs[logs["user_id"] == uid]

    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Your Logged Hours")

    if user_logs.empty:
        st.info("No logs yet.")
    else:
        for i, row in user_logs.iterrows():
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.write(f"### {row['subject']}")
            st.write(f"**Date:** {row['date']}")
            st.write(f"**Hours:** {row['hours_studied']}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Edit Log {i}"):
                    st.session_state["edit_log"] = i
            with col2:
                if st.button(f"Delete Log {i}"):
                    storage.delete_row("study_logs.csv", i)
                    st.success("Deleted.")
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

    if "edit_log" in st.session_state:
        idx = st.session_state["edit_log"]
        if idx in user_logs.index:
            row = user_logs.loc[idx]
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.subheader("Edit Log")

            with st.form("edit_log_form"):
                new_subject = st.text_input("Subject", value=row["subject"])
                new_hours = st.number_input("Hours", value=float(row["hours_studied"]))
                new_date = st.date_input("Date", pd.to_datetime(row["date"]))
                save = st.form_submit_button("Save Changes")

            if save:
                logs.loc[idx, "subject"] = new_subject
                logs.loc[idx, "hours_studied"] = new_hours
                logs.loc[idx, "date"] = str(new_date)
                storage.update_csv("study_logs.csv", logs)
                del st.session_state["edit_log"]
                st.success("Updated!")
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
