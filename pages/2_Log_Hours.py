import streamlit as st
import pandas as pd
from datetime import date

def app(storage):
    st.markdown("<div class='card'><h3>Log Study Hours</h3>", unsafe_allow_html=True)
    user = st.session_state.get("user")
    if not user:
        st.warning("Please login to log hours")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    uid = user.get("user_id")
    plans = storage.read_csv("study_plans.csv")
    logs = storage.read_csv("study_logs.csv")
    if plans is None or plans.empty:
        plans = pd.DataFrame(columns=["user_id","subject","goal","planned_hours","date"])
    if logs is None or logs.empty:
        logs = pd.DataFrame(columns=["user_id","date","subject","hours_studied"])
    user_plans = plans[plans["user_id"]==uid] if "user_id" in plans.columns else pd.DataFrame()
    with st.form("log"):
        subj_list = ["--select--"]
        if not user_plans.empty:
            subj_list = sorted(user_plans["subject"].unique().tolist())
        subject = st.selectbox("Subject", subj_list)
        hours = st.number_input("Hours studied", min_value=0.0, step=0.25)
        entry_date = st.date_input("Date", date.today())
        submit = st.form_submit_button("Add Log")
    if submit:
        if subject=="--select--":
            st.error("Choose a subject")
        else:
            row = {"user_id":uid,"date":str(entry_date),"subject":subject,"hours_studied":hours}
            storage.append_row("study_logs.csv", row)
            st.success("Logged")
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='card'><h4>Your Logs</h4>", unsafe_allow_html=True)
    if logs is None or logs.empty:
        st.info("No logs yet")
    else:
        user_logs = logs[logs["user_id"]==uid] if "user_id" in logs.columns else pd.DataFrame()
        for i, r in user_logs.iterrows():
            st.markdown(f"<div style='padding:10px;border-radius:8px;margin:8px 0;background:#fff8f6'><b>{r.get('subject')}</b><div class='small'>{r.get('date')} • {r.get('hours_studied')} hrs</div></div>", unsafe_allow_html=True)
            cols = st.columns([1,1])
            if cols[0].button("Edit", key=f"edit_log_{i}"):
                st.session_state.edit_log = i
                st.rerun()
            if cols[1].button("Delete", key=f"del_log_{i}"):
                storage.delete_row("study_logs.csv", i)
                st.success("Deleted")
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    if "edit_log" in st.session_state:
        idx = st.session_state.edit_log
        logs = storage.read_csv("study_logs.csv")
        if logs is None or logs.empty:
            return
        if idx in logs.index:
            r = logs.loc[idx]
            st.markdown("<div class='card'><h4>Edit Log</h4>", unsafe_allow_html=True)
            with st.form("editlog"):
                s = st.text_input("Subject", value=r.get("subject",""))
                h = st.number_input("Hours", value=float(r.get("hours_studied",0.0)))
                d = st.date_input("Date", value=pd.to_datetime(r.get("date")) if r.get("date") else None)
                save = st.form_submit_button("Save")
            if save:
                logs.loc[idx,"subject"]=s
                logs.loc[idx,"hours_studied"]=h
                logs.loc[idx,"date"]=str(d)
                storage.update_csv("study_logs.csv", logs)
                del st.session_state["edit_log"]
                st.success("Updated")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
