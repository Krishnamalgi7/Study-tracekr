import streamlit as st
import pandas as pd
import plotly.express as px

def app(storage):
    st.markdown("<div class='card'><h3>Analytics</h3>", unsafe_allow_html=True)
    user = st.session_state.get("user")
    if not user:
        st.warning("Please login to view analytics")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    uid = user.get("user_id")
    logs = storage.read_csv("study_logs.csv")
    plans = storage.read_csv("study_plans.csv")
    if logs is None or logs.empty:
        st.info("No study logs yet to show analytics")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    user_logs = logs[logs["user_id"]==uid] if "user_id" in logs.columns else pd.DataFrame()
    if user_logs.empty:
        st.info("No logs for analytics")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    total = user_logs["hours_studied"].sum()
    st.markdown(f"<div class='small'>Total Hours</div><div style='font-size:28px;font-weight:800'>{total} hrs</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    user_logs["date"] = pd.to_datetime(user_logs["date"])
    daily = user_logs.groupby("date")["hours_studied"].sum().reset_index()
    fig = px.line(daily, x="date", y="hours_studied", title="Daily Study Trend")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    subj = user_logs.groupby("subject")["hours_studied"].sum().reset_index()
    fig2 = px.pie(subj, names="subject", values="hours_studied", title="Hours per Subject", hole=0.4)
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    if plans is not None and not plans.empty and "user_id" in plans.columns:
        merged = pd.merge(plans[plans["user_id"]==uid], user_logs, on=["user_id","subject"], how="left")
        merged["hours_studied"] = merged["hours_studied"].fillna(0)
        grouped = merged.groupby("subject", as_index=False).agg({"planned_hours":"sum","hours_studied":"sum"})
        if not grouped.empty:
            fig3 = px.bar(grouped, x="subject", y=["planned_hours","hours_studied"], barmode="group", title="Planned vs Studied")
            st.plotly_chart(fig3, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
