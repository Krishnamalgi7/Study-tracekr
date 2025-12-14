import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime


def format_date(date_str):
    """Convert YYYY-MM-DD to DD Mon YYYY format"""
    try:
        if date_str and date_str != "nan" and date_str != "":
            date_obj = datetime.strptime(str(date_str), "%Y-%m-%d")
            return date_obj.strftime("%d %b %Y")
    except:
        pass
    return "Not Set"


def sync_analytics_data(storage, uid):
    """
    Syncs ONLY LOGGED plans into analytics.
    AUTOMATICALLY DELETES logged plans from plan.csv and log.csv after syncing.
    Preserves existing analytics data without resetting.
    """
    # 1. Load All Data Sources
    plans_df = storage.read_csv("study_plans.csv")
    logs_df = storage.read_csv("study_logs.csv")
    analytics_df = storage.read_csv("analytics.csv")

    # Track which subjects have been logged (for cleanup)
    logged_subjects = set()

    # --- DATA STRUCTURES ---
    ledger = []

    # Helper to clean strings
    def clean(s):
        return str(s).strip().lower()

    # --- STEP A: LOAD EXISTING ANALYTICS (History) ---
    # Keep all existing analytics data intact
    if analytics_df is not None and not analytics_df.empty:
        if "user_id" in analytics_df.columns:
            user_hist = analytics_df[analytics_df["user_id"].astype(str).str.replace(r'\.0$', '', regex=True) == uid]
            ledger = user_hist.to_dict('records')

    # --- STEP B: PROCESS NEW LOGS ---
    # Only add NEW logs that aren't already in analytics
    if logs_df is not None and not logs_df.empty:
        uid_col = "user_id" if "user_id" in logs_df.columns else "userid"
        if uid_col in logs_df.columns:
            user_logs = logs_df[logs_df[uid_col].astype(str).str.replace(r'\.0$', '', regex=True) == uid]

            for _, log in user_logs.iterrows():
                l_subj = log.get("subject", "Unknown")
                l_date = str(log.get("date", ""))
                h_col = "hours" if "hours" in log else "hours_studied"
                l_hours = float(log.get(h_col, 0) or 0)

                # Track this subject as logged (for cleanup later)
                logged_subjects.add(clean(l_subj))

                # Check if this subject already exists in ledger
                match = None
                for row in ledger:
                    if clean(row.get("subject")) == clean(l_subj):
                        match = row
                        break

                if not match:
                    # This is a NEW log entry - add it to ledger
                    planned_hours = 0.0
                    planned_date = ""

                    # Try to get planned hours from plans_df
                    if plans_df is not None and not plans_df.empty and "user_id" in plans_df.columns:
                        user_plans = plans_df[
                            plans_df["user_id"].astype(str).str.replace(r'\.0$', '', regex=True) == uid]
                        plan_match = user_plans[
                            user_plans["subject"].astype(str).str.strip().str.lower() == clean(l_subj)]

                        if not plan_match.empty:
                            planned_hours = float(plan_match.iloc[0].get("planned_hours", 0) or 0)
                            planned_date = str(plan_match.iloc[0].get("date", ""))

                    ledger.append({
                        "user_id": uid,
                        "subject": l_subj,
                        "planned_date": planned_date,
                        "planned_hours": planned_hours,
                        "log_date": l_date,
                        "hours_studied": l_hours
                    })

    # --- STEP C: CLEANUP LOGGED PLANS FROM PLANS CSV ---
    if plans_df is not None and not plans_df.empty and logged_subjects:
        # Remove plans for this user that have been logged
        plans_df["_temp_uid"] = plans_df["user_id"].astype(str).str.replace(r'\.0$', '', regex=True)
        plans_df["_temp_subj"] = plans_df["subject"].astype(str).str.strip().str.lower()

        # Keep plans that are:
        # 1. Not this user's, OR
        # 2. This user's but NOT logged yet
        plans_df = plans_df[
            (plans_df["_temp_uid"] != uid) |
            (~plans_df["_temp_subj"].isin(logged_subjects))
            ]

        plans_df = plans_df.drop(columns=["_temp_uid", "_temp_subj"])
        storage.write_csv("study_plans.csv", plans_df)

    # --- STEP D: CLEANUP LOGS FROM LOGS CSV ---
    if logs_df is not None and not logs_df.empty and logged_subjects:
        uid_col = "user_id" if "user_id" in logs_df.columns else "userid"

        if uid_col in logs_df.columns:
            # Normalize for matching
            logs_df["_temp_uid"] = logs_df[uid_col].astype(str).str.replace(r'\.0$', '', regex=True)
            logs_df["_temp_subj"] = logs_df["subject"].astype(str).str.strip().str.lower()

            # Remove all logs for current user that we just processed
            logs_df = logs_df[
                (logs_df["_temp_uid"] != uid) |
                (~logs_df["_temp_subj"].isin(logged_subjects))
                ]

            logs_df = logs_df.drop(columns=["_temp_uid", "_temp_subj"], errors='ignore')
            storage.write_csv("study_logs.csv", logs_df)

    # --- STEP E: SAVE ANALYTICS ---
    # Get other users data to preserve it
    other_users_df = pd.DataFrame()
    if analytics_df is not None and not analytics_df.empty and "user_id" in analytics_df.columns:
        other_users_df = analytics_df[analytics_df["user_id"].astype(str).str.replace(r'\.0$', '', regex=True) != uid]

    current_df = pd.DataFrame(ledger)

    # Force Schema
    cols = ["user_id", "subject", "planned_date", "planned_hours", "log_date", "hours_studied"]
    if not current_df.empty:
        # Fill missing
        for c in cols:
            if c not in current_df.columns:
                current_df[c] = "" if "date" in c else 0.0
        # Select and Order
        current_df = current_df[cols]
    else:
        current_df = pd.DataFrame(columns=cols)

    final_df = pd.concat([other_users_df, current_df], ignore_index=True)

    # Convert numeric columns safely
    final_df["planned_hours"] = pd.to_numeric(final_df["planned_hours"], errors='coerce').fillna(0.0)
    final_df["hours_studied"] = pd.to_numeric(final_df["hours_studied"], errors='coerce').fillna(0.0)

    storage.write_csv("analytics.csv", final_df)

    return current_df


def app(storage):
    st.markdown("<div class='card'><h3>📊 Analytics Dashboard</h3>", unsafe_allow_html=True)

    user = st.session_state.get("user")
    if not user:
        st.warning("Please login to view analytics")
        return

    uid = str(user.get("user_id")).replace('.0', '')

    try:
        df = sync_analytics_data(storage, uid)
    except Exception as e:
        st.error(f"Sync Error: {e}")
        import traceback
        st.code(traceback.format_exc())
        return

    if df.empty:
        st.info("📭 No logged study sessions yet. Start by logging your study hours!")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # --- VISUALIZATION ---
    st.markdown("#### 🏆 Progress by Subject")

    # Transform data for the graph - FIXED: Separate dates for Planned vs Studied
    graph_data = []

    for _, row in df.iterrows():
        subj = row.get("subject")
        p_date = str(row.get("planned_date", ""))
        l_date = str(row.get("log_date", ""))

        p_hrs = float(row.get("planned_hours", 0))
        s_hrs = float(row.get("hours_studied", 0))

        # Add Planned entry with planned_date
        if p_hrs > 0:
            graph_data.append({
                "Subject": subj,
                "Date": format_date(p_date),  # Use planned date for planned hours
                "Type": "Planned",
                "Hours": p_hrs
            })

        # Add Studied entry with log_date
        if s_hrs > 0:
            graph_data.append({
                "Subject": subj,
                "Date": format_date(l_date),  # Use log date for studied hours
                "Type": "Studied",
                "Hours": s_hrs
            })

    if graph_data:
        df_g = pd.DataFrame(graph_data)

        fig = px.bar(
            df_g,
            x="Subject",
            y="Hours",
            color="Type",
            barmode="group",
            hover_data=["Date"],
            color_discrete_map={"Planned": "#8b5cf6", "Studied": "#10b981"},
            title=""
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            margin=dict(t=20, b=20, l=20, r=20)
        )
        fig.update_traces(
            hovertemplate="<b>%{x}</b><br>Hours: %{y}<br>Date: %{customdata[0]}<extra></extra>"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data to chart.")

    st.markdown("<hr style='margin: 30px 0; opacity: 0.2;'>", unsafe_allow_html=True)

    # --- DETAILED TABLE (Collapsible) ---
    with st.expander("📋 Detailed View", expanded=False):
        display_df = df.copy()

        # Format dates for display
        display_df["planned_date_formatted"] = display_df["planned_date"].apply(format_date)
        display_df["log_date_formatted"] = display_df["log_date"].apply(format_date)

        display_df = display_df[
            ["subject", "planned_hours", "hours_studied", "planned_date_formatted", "log_date_formatted"]]
        display_df.columns = ["Subject", "Planned (hrs)", "Studied (hrs)", "Planned Date", "Logged Date"]
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("<hr style='margin: 30px 0; opacity: 0.2;'>", unsafe_allow_html=True)

    # --- RESET ---
    with st.expander("⚙️ Data Management"):
        st.warning("**Danger Zone:** This will permanently delete your analytics and log history.")

        if st.button("🗑️ Reset All Analytics Data", type="secondary"):
            # Clear Analytics
            al = storage.read_csv("analytics.csv")
            if al is not None:
                new_al = al[al["user_id"].astype(str).str.replace(r'\.0$', '', regex=True) != uid]
                storage.write_csv("analytics.csv", new_al)

            # Clear Logs
            lg = storage.read_csv("study_logs.csv")
            if lg is not None:
                col = "user_id" if "user_id" in lg.columns else "userid"
                if col in lg.columns:
                    new_lg = lg[lg[col].astype(str).str.replace(r'\.0$', '', regex=True) != uid]
                    storage.write_csv("study_logs.csv", new_lg)

            st.success("✅ All analytics and logs cleared!")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)