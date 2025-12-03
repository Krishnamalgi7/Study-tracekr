import streamlit as st
import pandas as pd

def app(storage):
    st.markdown("<div class='card'><h3>New Study Plan</h3>", unsafe_allow_html=True)
    user = st.session_state.get("user")
    if not user:
        st.warning("Please login to add plans")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    uid = user.get("user_id")
    df = storage.read_csv("study_plans.csv")
    if df is None or df.empty:
        df = pd.DataFrame(columns=["user_id","subject","goal","planned_hours","date"])
    with st.form("plan"):
        subject = st.text_input("Subject")
        goal = st.text_area("Goal description")
        hours = st.number_input("Planned hours", min_value=0.0, step=0.5)
        date = st.date_input("Date")
        submit = st.form_submit_button("Save Plan")
    if submit:
        row = {"user_id":uid,"subject":subject.strip(),"goal":goal.strip(),"planned_hours":hours,"date":str(date)}
        storage.append_row("study_plans.csv", row)
        st.success("Plan added")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='card'><h4>Your Plans</h4>", unsafe_allow_html=True)
    plans = storage.read_csv("study_plans.csv")
    if plans is None or plans.empty:
        st.info("No plans yet")
    else:
        ups = plans[plans["user_id"]==uid] if "user_id" in plans.columns else pd.DataFrame()
        for i, r in ups.iterrows():
            st.markdown(f"<div style='padding:12px;border-radius:8px;margin:8px 0;background:linear-gradient(90deg,rgba(255,250,240,0.6),#fff);'><b>{r.get('subject')}</b><div class='small'>{r.get('goal')}</div><div class='small'>Planned {r.get('planned_hours')} hrs • {r.get('date')}</div></div>", unsafe_allow_html=True)
            cols = st.columns([1,1])
            if cols[0].button("Edit", key=f"edit_plan_{i}"):
                st.session_state.edit_plan = i
                st.rerun()
            if cols[1].button("Delete", key=f"del_plan_{i}"):
                storage.delete_row("study_plans.csv", i)
                st.success("Deleted")
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    if "edit_plan" in st.session_state:
        idx = st.session_state.edit_plan
        plans = storage.read_csv("study_plans.csv")
        if plans is None or plans.empty:
            return
        if idx in plans.index:
            r = plans.loc[idx]
            st.markdown("<div class='card'><h4>Edit Plan</h4>", unsafe_allow_html=True)
            with st.form("edit"):
                s = st.text_input("Subject", value=r.get("subject",""))
                g = st.text_area("Goal", value=r.get("goal",""))
                h = st.number_input("Hours", value=float(r.get("planned_hours",0.0)))
                d = st.date_input("Date", value=pd.to_datetime(r.get("date")) if r.get("date") else None)
                save = st.form_submit_button("Save")
            if save:
                plans.loc[idx,"subject"]=s
                plans.loc[idx,"goal"]=g
                plans.loc[idx,"planned_hours"]=h
                plans.loc[idx,"date"]=str(d)
                storage.update_csv("study_plans.csv", plans)
                del st.session_state["edit_plan"]
                st.success("Updated")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
