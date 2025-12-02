import streamlit as st
import pandas as pd

def app(storage):
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Add Study Plan")
    st.write("Create structured study plans to stay organized.")

    user = st.session_state.user
    uid = user["user_id"]

    df = storage.read_csv("study_plans.csv")
    if df is None or df.empty:
        df = pd.DataFrame(columns=["user_id", "subject", "goal", "planned_hours", "date"])

    with st.form("plan_form"):
        subject = st.text_input("Subject")
        goal = st.text_area("Goal Description")
        planned_hours = st.number_input("Planned Hours", min_value=0.0, step=1.0)
        date = st.date_input("Select Date")
        submitted = st.form_submit_button("Add Plan")

    if submitted:
        new_row = {
            "user_id": uid,
            "subject": subject.strip(),
            "goal": goal.strip(),
            "planned_hours": planned_hours,
            "date": str(date)
        }
        storage.append_row("study_plans.csv", new_row)
        st.success("Study plan added successfully!")
        st.rerun()

    user_plans = df[df["user_id"] == uid]

    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Your Study Plans")

    if user_plans.empty:
        st.info("No study plans added yet.")
    else:
        for i, row in user_plans.iterrows():
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.write(f"### {row['subject']}")
            st.write(f"**Goal:** {row['goal']}")
            st.write(f"**Planned Hours:** {row['planned_hours']}")
            st.write(f"**Date:** {row['date']}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Edit {i}"):
                    st.session_state["edit_index"] = i
            with col2:
                if st.button(f"Delete {i}"):
                    storage.delete_row("study_plans.csv", i)
                    st.success("Deleted.")
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    if "edit_index" in st.session_state:
        idx = st.session_state["edit_index"]
        if idx in user_plans.index:
            edit_row = user_plans.loc[idx]
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.subheader("Edit Plan")

            with st.form("edit_form"):
                new_subject = st.text_input("Subject", edit_row["subject"])
                new_goal = st.text_area("Goal", edit_row["goal"])
                new_hours = st.number_input("Hours", value=float(edit_row["planned_hours"]))
                new_date = st.date_input("Date", pd.to_datetime(edit_row["date"]))
                save = st.form_submit_button("Save Changes")

            if save:
                df.loc[idx, "subject"] = new_subject
                df.loc[idx, "goal"] = new_goal
                df.loc[idx, "planned_hours"] = new_hours
                df.loc[idx, "date"] = str(new_date)
                storage.update_csv("study_plans.csv", df)
                del st.session_state["edit_index"]
                st.success("Updated!")
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
