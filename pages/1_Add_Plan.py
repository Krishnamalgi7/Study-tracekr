import streamlit as st
import pandas as pd
from datetime import date, datetime
from utils.ai_client import ClaudeAI


# --- CALLBACKS ---

def update_goal_text(text):
    st.session_state.plan_goal = text


def handle_save_plan(storage, user_id):
    # 1. Validation
    if not st.session_state.plan_subject:
        st.session_state.form_message = ("error", "Please enter a subject")
        return

    # 2. Prepare Data
    row = {
        "user_id": str(user_id),
        "subject": st.session_state.plan_subject.strip(),
        "goal": st.session_state.plan_goal.strip(),
        "planned_hours": st.session_state.plan_hours,
        "date": str(st.session_state.plan_date)
    }

    # 3. Save using Storage (Correct Path)
    # We use storage.append_row which handles loading/saving correctly
    storage.append_row("study_plans.csv", row)

    # 4. Clear Inputs
    st.session_state.plan_subject = ""
    st.session_state.plan_goal = ""

    # 5. Success
    st.session_state.form_message = ("success", "Plan saved successfully!")


def handle_delete_plan(storage, index):
    # 1. Load Plans to identify what we are deleting
    plans_df = storage.read_csv("study_plans.csv")

    if plans_df is not None and index in plans_df.index:
        # Get the row details before deleting
        row = plans_df.loc[index]
        subject_to_delete = str(row.get("subject", "")).strip().lower()
        user_id_to_delete = str(row.get("user_id", "")).replace(".0", "")
        original_subject_name = row.get("subject", "Unknown")

        # 2. Delete from Plans
        plans_df = plans_df.drop(index)
        storage.write_csv("study_plans.csv", plans_df)

        # 3. Delete from Logs (Clean up the study_logs.csv file)
        logs_df = storage.read_csv("study_logs.csv")
        if logs_df is not None and not logs_df.empty:
            # Normalize columns to ensure we match correctly
            logs_df.columns = logs_df.columns.str.strip().str.lower()
            if "userid" in logs_df.columns:
                logs_df = logs_df.rename(columns={"userid": "user_id"})

            if "user_id" in logs_df.columns and "subject" in logs_df.columns:
                # Prepare temporary columns for safe comparison
                logs_df["_temp_uid"] = logs_df["user_id"].astype(str).str.replace(r'\.0$', '', regex=True)
                logs_df["_temp_subj"] = logs_df["subject"].astype(str).str.strip().str.lower()

                # Logic: Keep rows that do NOT match (User ID AND Subject)
                mask_keep = ~(
                            (logs_df["_temp_uid"] == user_id_to_delete) & (logs_df["_temp_subj"] == subject_to_delete))

                # Filter data
                new_logs_df = logs_df[mask_keep].drop(columns=["_temp_uid", "_temp_subj"])

                # Save only if we actually removed something
                if len(new_logs_df) < len(logs_df):
                    storage.write_csv("study_logs.csv", new_logs_df)

        st.toast(f"Plan and logs for '{original_subject_name}' deleted!", icon="🗑️")


def handle_update_plan(storage, index, new_subj, new_goal, new_hours, new_date):
    df = storage.read_csv("study_plans.csv")
    if df is not None and index in df.index:
        df.at[index, "subject"] = new_subj
        df.at[index, "goal"] = new_goal
        df.at[index, "planned_hours"] = new_hours
        df.at[index, "date"] = str(new_date)
        storage.write_csv("study_plans.csv", df)
        st.toast("Plan updated!", icon="✅")


# --- MAIN APP ---
def app(storage):
    # --- SETUP STATE ---
    if "plan_subject" not in st.session_state: st.session_state.plan_subject = ""
    if "plan_goal" not in st.session_state: st.session_state.plan_goal = ""
    if "plan_hours" not in st.session_state: st.session_state.plan_hours = 1.0
    if "plan_date" not in st.session_state: st.session_state.plan_date = date.today()
    if "mini_chat_messages" not in st.session_state: st.session_state.mini_chat_messages = []

    if "form_message" not in st.session_state:
        st.session_state.form_message = None

    st.markdown("<h3>New Study Plan</h3>", unsafe_allow_html=True)

    col_form, col_chat = st.columns([1.3, 1], gap="large")

    # ==========================
    # LEFT: ADD & MANAGE PLANS
    # ==========================
    with col_form:
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        user = st.session_state.get("user")
        if not user:
            st.warning("Please login to add plans")
            return

        current_user_id = str(user.get("user_id"))

        # --- SECTION A: ADD NEW PLAN ---
        if st.session_state.form_message:
            msg_type, msg_text = st.session_state.form_message
            if msg_type == "error":
                st.error(msg_text)
            else:
                st.success(msg_text)
            st.session_state.form_message = None

        st.caption("Add a new goal")
        st.text_input("Subject", key="plan_subject", placeholder="e.g. Python")
        st.text_area("Goal", key="plan_goal", height=100, placeholder="Details...")

        c1, c2 = st.columns(2)
        with c1:
            st.number_input("Hours", 0.5, 24.0, 1.0, 0.5, key="plan_hours")
        with c2:
            st.date_input("Date", key="plan_date")

        # PASS STORAGE TO CALLBACK
        st.button("➕ Add Plan", type="primary", use_container_width=True,
                  on_click=handle_save_plan, args=(storage, current_user_id))

        st.markdown("</div>", unsafe_allow_html=True)

        # --- SECTION B: MANAGE PLANS (EDIT/DELETE) ---
        st.markdown("### 📝 Manage Your Plans")

        # LOAD FROM STORAGE (Handles 'data/' folder automatically)
        df = storage.read_csv("study_plans.csv")

        if df is None or df.empty:
            st.info("No plans found. Add one above!")
        else:
            # Force ID to string for comparison
            df["user_id"] = df["user_id"].astype(str)

            # Filter for current user
            user_plans = df[df["user_id"] == current_user_id]

            if user_plans.empty:
                st.info("No plans found for this account.")
            else:
                # Sort by latest first
                user_plans = user_plans.sort_index(ascending=False)

                for index, row in user_plans.iterrows():
                    with st.expander(f"📌 {row['subject']} ({row['date']})"):

                        with st.form(key=f"edit_{index}"):
                            e_subj = st.text_input("Subject", value=row['subject'])
                            e_goal = st.text_area("Goal", value=row['goal'])

                            ec1, ec2 = st.columns(2)
                            val_hours = float(row['planned_hours'])
                            e_hours = ec1.number_input("Hours", 0.5, 24.0, val_hours, 0.5)

                            try:
                                val_date = datetime.strptime(str(row['date']), "%Y-%m-%d").date()
                            except:
                                val_date = date.today()
                            e_date = ec2.date_input("Date", value=val_date)

                            c_upd, c_del = st.columns([1, 1])
                            with c_upd:
                                update_submitted = st.form_submit_button("Update", type="primary")
                            with c_del:
                                pass  # Delete handled outside

                        if update_submitted:
                            handle_update_plan(storage, index, e_subj, e_goal, e_hours, e_date)
                            st.rerun()

                        # Delete Button
                        if st.button("🗑️ Delete this plan", key=f"del_{index}"):
                            handle_delete_plan(storage, index)
                            st.rerun()

    # ==========================
    # RIGHT: AI ASSISTANT
    # ==========================
    with col_chat:
        st.markdown("""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 15px; height: 100%;">
            <h4 style="margin-top:0; color:#475569;">🤖 AI Helper</h4>
            <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 15px;">
                Ask for a study plan and click "Copy" to fill the form.
            </p>
        """, unsafe_allow_html=True)

        for idx, msg in enumerate(st.session_state.mini_chat_messages[-4:]):
            role_color = "#e0e7ff" if msg["role"] == "assistant" else "#f1f5f9"
            align = "left" if msg["role"] == "assistant" else "right"
            st.markdown(
                f"<div style='text-align:{align};margin-bottom:8px;'><span style='background:{role_color};padding:8px 12px;border-radius:12px;font-size:0.9rem;display:inline-block;'>{msg['content']}</span></div>",
                unsafe_allow_html=True)

            if msg["role"] == "assistant" and msg == st.session_state.mini_chat_messages[-1]:
                st.button("📋 Copy to Goal", key=f"copy_{idx}", on_click=update_goal_text, args=(msg["content"],))

        with st.form(key="mini_chat_form", clear_on_submit=True):
            user_question = st.text_input("Ask AI...", placeholder="e.g., Plan for SQL basics")
            submitted = st.form_submit_button("Ask")

        if submitted and user_question:
            st.session_state.mini_chat_messages.append({"role": "user", "content": user_question})
            client = ClaudeAI()
            with st.spinner("Thinking..."):
                response = client.ask(f"Write a short, clear study goal (under 50 words) for: {user_question}")
            st.session_state.mini_chat_messages.append({"role": "assistant", "content": response})
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)