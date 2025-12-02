import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

def app(storage):
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Analytics Dashboard")
    st.write("Visual insights of your study progress.")

    user = st.session_state.user
    uid = user["user_id"]

    logs = storage.read_csv("study_logs.csv")
    plans = storage.read_csv("study_plans.csv")

    if logs is None or logs.empty:
        logs = pd.DataFrame(columns=["user_id", "date", "subject", "hours_studied"])
    if plans is None or plans.empty:
        plans = pd.DataFrame(columns=["user_id", "subject", "goal", "planned_hours", "date"])

    user_logs = logs[logs["user_id"] == uid]
    user_plans = plans[plans["user_id"] == uid]

    if user_logs.empty:
        st.info("No logs available for analytics.")
        return

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)

    st.subheader("Total Hours Studied")
    total_hours = user_logs["hours_studied"].sum()
    st.markdown(f"<div class='huge'>{total_hours}</div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.subheader("Hours Per Subject")
    subject_sum = user_logs.groupby("subject")["hours_studied"].sum().reset_index()
    fig = px.pie(subject_sum, names="subject", values="hours_studied", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.subheader("Daily Study Trend")
    user_logs["date"] = pd.to_datetime(user_logs["date"])
    daily = user_logs.groupby("date")["hours_studied"].sum().reset_index()
    fig2 = px.line(daily, x="date", y="hours_studied")
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.subheader("Goals vs Actual Hours")
    merged = pd.merge(user_plans, user_logs, on=["user_id", "subject"], how="left")
    merged["hours_studied"] = merged["hours_studied"].fillna(0)
    grouped = merged.groupby("subject", as_index=False).agg({"planned_hours": "sum", "hours_studied": "sum"})

    fig3 = px.bar(grouped, x="subject", y=["planned_hours", "hours_studied"], barmode="group")
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)
