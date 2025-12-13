import streamlit as st
import pandas as pd
import plotly.express as px


def sync_analytics_data(storage, uid):
    """
    Syncs plans and logs into a master ledger.
    Uses 'Smart Matching' to merge Logs into Plans even if dates differ,
    preventing duplicate rows.
    """
    # 1. Load All Data Sources
    plans_df = storage.read_csv("study_plans.csv")
    logs_df = storage.read_csv("study_logs.csv")
    analytics_df = storage.read_csv("analytics.csv")

    # --- DATA STRUCTURES ---
    # We use a list of dictionaries to represent our "Master Ledger"
    ledger = []

    # Helper to clean strings
    def clean(s):
        return str(s).strip().lower()

    # --- STEP A: LOAD EXISTING ANALYTICS (History of Deleted Plans) ---
    # We start with what we already have to ensure deleted plans aren't lost.
    if analytics_df is not None and not analytics_df.empty:
        # Filter for current user only
        if "user_id" in analytics_df.columns:
            user_hist = analytics_df[analytics_df["user_id"].astype(str).str.replace(r'\.0$', '', regex=True) == uid]
            ledger = user_hist.to_dict('records')

    # --- STEP B: SYNC ACTIVE PLANS ---
    # We update existing ledger entries or add new ones from "study_plans.csv"
    if plans_df is not None and not plans_df.empty and "user_id" in plans_df.columns:
        user_plans = plans_df[plans_df["user_id"].astype(str).str.replace(r'\.0$', '', regex=True) == uid]

        for _, plan in user_plans.iterrows():
            p_subj = plan.get("subject", "Unknown")
            p_date = str(plan.get("date", ""))
            p_hours = float(plan.get("planned_hours", 0) or 0)

            # 1. Search for existing match in ledger (Exact Match by Date & Subject)
            match = None
            for row in ledger:
                # Check if subject matches
                if clean(row.get("subject")) == clean(p_subj):
                    # Check if planned date matches (if it exists)
                    r_p_date = str(row.get("planned_date", ""))
                    if r_p_date == p_date:
                        match = row
                        break

            if match:
                # Update existing plan (in case user edited hours)
                match["planned_hours"] = p_hours
                match["planned_date"] = p_date
            else:
                # Add new plan to ledger
                ledger.append({
                    "user_id": uid,
                    "subject": p_subj,
                    "planned_date": p_date,
                    "planned_hours": p_hours,
                    "log_date": "",  # Empty initially
                    "hours_studied": 0.0  # Empty initially
                })

    # --- STEP C: SYNC LOGS (The "Smart Match") ---
    # We iterate through logs and try to attach them to the best candidate in the ledger
    if logs_df is not None and not logs_df.empty:
        uid_col = "user_id" if "user_id" in logs_df.columns else "userid"
        if uid_col in logs_df.columns:
            user_logs = logs_df[logs_df[uid_col].astype(str).str.replace(r'\.0$', '', regex=True) == uid]

            # Reset all 'hours_studied' in ledger to 0 before re-tallying to avoid double counts
            for row in ledger:
                row["hours_studied"] = 0.0
                # We keep log_date if it exists, or update it below

            for _, log in user_logs.iterrows():
                l_subj = log.get("subject", "Unknown")
                l_date = str(log.get("date", ""))
                h_col = "hours" if "hours" in log else "hours_studied"
                l_hours = float(log.get(h_col, 0) or 0)

                # SEARCH FOR BEST MATCH
                best_match = None

                # Pass 1: Exact Date Match
                for row in ledger:
                    if clean(row.get("subject")) == clean(l_subj):
                        # Use planned_date or log_date to check
                        if str(row.get("planned_date")) == l_date or str(row.get("log_date")) == l_date:
                            best_match = row
                            break

                # Pass 2: Fuzzy Match (If no exact date match, find an open plan)
                # This fixes the "2 rows" issue!
                if not best_match:
                    for row in ledger:
                        if clean(row.get("subject")) == clean(l_subj):
                            # Matches Subject
                            # And hasn't been 'claimed' by hours yet (or is the only plan)
                            # We attach to the first plan that has planned hours but 0 studied hours
                            if float(row.get("planned_hours", 0)) > 0 and float(row.get("hours_studied", 0)) == 0:
                                best_match = row
                                break

                if best_match:
                    # Merge Log into Plan
                    best_match["hours_studied"] += l_hours
                    # Update log date (if multiple logs, this shows the latest one)
                    best_match["log_date"] = l_date
                else:
                    # No plan found? Create "Unplanned Study" row
                    ledger.append({
                        "user_id": uid,
                        "subject": l_subj,
                        "planned_date": "",  # Unplanned
                        "planned_hours": 0.0,
                        "log_date": l_date,
                        "hours_studied": l_hours
                    })

    # --- STEP D: SAVE AND CLEANUP ---
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

    # Convert numeric columns safely before saving to avoid "nan" string issues
    final_df["planned_hours"] = pd.to_numeric(final_df["planned_hours"], errors='coerce').fillna(0.0)
    final_df["hours_studied"] = pd.to_numeric(final_df["hours_studied"], errors='coerce').fillna(0.0)

    storage.write_csv("analytics.csv", final_df)

    return current_df


def app(storage):
    st.markdown("<div class='card'><h3>Analytics</h3>", unsafe_allow_html=True)

    user = st.session_state.get("user")
    if not user:
        st.warning("Please login to view analytics")
        return

    uid = str(user.get("user_id")).replace('.0', '')

    try:
        df = sync_analytics_data(storage, uid)
    except Exception as e:
        st.error(f"Sync Error: {e}")
        return

    if df.empty:
        st.info("No activity found.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # --- VISUALIZATION ---
    st.markdown("#### 🏆 Overall Progress")

    # We transform the data for the graph
    graph_data = []

    for _, row in df.iterrows():
        subj = row.get("subject")
        p_date = str(row.get("planned_date", ""))
        l_date = str(row.get("log_date", ""))

        # Display Date Logic: Prefer Plan Date, fallback to Log Date
        disp_date = p_date if p_date and p_date != "nan" else l_date

        p_hrs = float(row.get("planned_hours", 0))
        s_hrs = float(row.get("hours_studied", 0))

        if p_hrs > 0:
            graph_data.append({"Subject": subj, "Date": disp_date, "Type": "Planned", "Hours": p_hrs})
        if s_hrs > 0:
            graph_data.append({"Subject": subj, "Date": disp_date, "Type": "Studied", "Hours": s_hrs})

    if graph_data:
        df_g = pd.DataFrame(graph_data)

        fig = px.bar(
            df_g,
            x="Subject",
            y="Hours",
            color="Type",
            barmode="group",
            hover_data=["Date"],
            color_discrete_map={"Planned": "#8b5cf6", "Studied": "#10b981"}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data to chart.")

    st.markdown("<hr style='margin: 30px 0; opacity: 0.2;'>", unsafe_allow_html=True)

    # --- RESET ---
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("**Reset Data**")
        st.caption("Clear history.")
    with c2:
        if st.button("Reset Analytics", type="primary"):
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

            st.success("Cleared!")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)