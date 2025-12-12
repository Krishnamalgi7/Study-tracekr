import streamlit as st
import pandas as pd
import plotly.express as px


def sync_analytics_data(storage, uid):
    """
    Merges current plans and logs into a persistent analytics.csv file.
    This ensures that even if a plan is deleted from study_plans.csv,
    the history remains in analytics.csv.
    """
    # 1. Load Current "Live" Data
    plans = storage.read_csv("study_plans.csv")
    logs = storage.read_csv("study_logs.csv")

    # We will collect data in a list of dictionaries first to avoid concat warnings
    current_data_rows = []

    # --- PROCESS PLANS ---
    if plans is not None and not plans.empty:
        p_df = plans.copy()
        # Clean columns
        p_df.columns = p_df.columns.str.strip().str.lower()
        if "user_id" not in p_df.columns and "userid" in p_df.columns: p_df = p_df.rename(columns={"userid": "user_id"})
        if "planned hours" in p_df.columns: p_df = p_df.rename(columns={"planned hours": "planned_hours"})

        # Filter for user
        if "user_id" in p_df.columns:
            p_df["user_id"] = p_df["user_id"].astype(str).str.replace(r'\.0$', '', regex=True)
            user_plans = p_df[p_df["user_id"] == uid].copy()

            if not user_plans.empty and "subject" in user_plans.columns:
                user_plans["clean_subject"] = user_plans["subject"].astype(str).str.strip().str.lower()
                # Use to_numeric to prevent issues
                user_plans["planned_hours"] = pd.to_numeric(user_plans["planned_hours"], errors='coerce').fillna(0.0)

                # Aggregate Plans
                p_agg = user_plans.groupby("clean_subject", as_index=False).agg({
                    "subject": "first",  # Keep original casing of first occurrence
                    "planned_hours": "sum"
                })

                # Add to our list
                for _, row in p_agg.iterrows():
                    current_data_rows.append({
                        "user_id": uid,
                        "subject": row["subject"],
                        "clean_subject": row["clean_subject"],
                        "planned_hours": row["planned_hours"],
                        "hours_studied": 0.0
                    })

    # Convert what we have so far to a DataFrame for easier merging with logs
    if current_data_rows:
        current_data = pd.DataFrame(current_data_rows)
    else:
        current_data = pd.DataFrame(columns=["user_id", "subject", "clean_subject", "planned_hours", "hours_studied"])

    # --- PROCESS LOGS ---
    if logs is not None and not logs.empty:
        l_df = logs.copy()
        l_df.columns = l_df.columns.str.strip().str.lower()
        if "user_id" not in l_df.columns and "userid" in l_df.columns: l_df = l_df.rename(columns={"userid": "user_id"})

        # Numeric cleanup
        if "hours_studied" in l_df.columns:
            l_df["hours_studied"] = pd.to_numeric(l_df["hours_studied"], errors='coerce').fillna(0.0)
        else:
            l_df["hours_studied"] = 0.0

        if "hours" in l_df.columns:
            l_df["hours"] = pd.to_numeric(l_df["hours"], errors='coerce').fillna(0.0)
            l_df["hours_studied"] = l_df["hours_studied"] + l_df["hours"]

        if "user_id" in l_df.columns:
            l_df["user_id"] = l_df["user_id"].astype(str).str.replace(r'\.0$', '', regex=True)
            user_logs = l_df[l_df["user_id"] == uid].copy()

            if not user_logs.empty and "subject" in user_logs.columns:
                user_logs["clean_subject"] = user_logs["subject"].astype(str).str.strip().str.lower()

                # Aggregate Logs
                l_agg = user_logs.groupby("clean_subject", as_index=False).agg({
                    "subject": "first",
                    "hours_studied": "sum"
                })

                # Merge into current_data logic
                # We iterate through aggregated logs
                new_log_rows = []
                for _, row in l_agg.iterrows():
                    # Check if subject exists in plans (in our current_data DataFrame)
                    if not current_data.empty:
                        mask = current_data["clean_subject"] == row["clean_subject"]
                        if mask.any():
                            current_data.loc[mask, "hours_studied"] = row["hours_studied"]
                            continue

                    # If not found, it's a log without a current plan
                    new_log_rows.append({
                        "user_id": uid,
                        "subject": row["subject"],
                        "clean_subject": row["clean_subject"],
                        "planned_hours": 0.0,
                        "hours_studied": row["hours_studied"]
                    })

                # Concatenate once at the end if needed
                if new_log_rows:
                    current_data = pd.concat([current_data, pd.DataFrame(new_log_rows)], ignore_index=True)

    # 2. Load Persistent Analytics File
    analytics = storage.read_csv("analytics.csv")

    # Create if missing
    if analytics is None or analytics.empty:
        analytics = pd.DataFrame(columns=["user_id", "subject", "clean_subject", "planned_hours", "hours_studied"])

    # Ensure columns exist
    if "clean_subject" not in analytics.columns: analytics["clean_subject"] = ""
    if "user_id" not in analytics.columns: analytics["user_id"] = ""

    # Clean IDs in file
    analytics["user_id"] = analytics["user_id"].astype(str).str.replace(r'\.0$', '', regex=True)

    # 3. UPSERT LOGIC (Update existing, Add new, BUT DO NOT DELETE missing)

    # Filter analytics for other users (we keep them as is)
    other_users_data = analytics[analytics["user_id"] != uid]

    # Filter analytics for THIS user
    my_saved_data = analytics[analytics["user_id"] == uid].copy()

    if not my_saved_data.empty:
        my_saved_data["clean_subject"] = my_saved_data["subject"].astype(str).str.strip().str.lower()
        # Ensure numeric types
        my_saved_data["planned_hours"] = pd.to_numeric(my_saved_data["planned_hours"], errors='coerce').fillna(0.0)
        my_saved_data["hours_studied"] = pd.to_numeric(my_saved_data["hours_studied"], errors='coerce').fillna(0.0)

    final_user_data = my_saved_data.copy()
    new_rows_to_add = []

    # Update logic
    for _, row in current_data.iterrows():
        subj = row["clean_subject"]

        # Check if we already have this subject in saved history
        mask = final_user_data["clean_subject"] == subj

        if mask.any():
            # Update existing record

            # CRITICAL FIX: Only overwrite planned_hours if the current plan exists (> 0).
            # If current plan is 0 (deleted), we KEEP the historical value.
            if row["planned_hours"] > 0:
                final_user_data.loc[mask, "planned_hours"] = row["planned_hours"]

            # Always update studied hours as they accumulate
            final_user_data.loc[mask, "hours_studied"] = row["hours_studied"]
        else:
            # Add new subject
            new_rows_to_add.append(row)

    # Concatenate new rows if any
    if new_rows_to_add:
        final_user_data = pd.concat([final_user_data, pd.DataFrame(new_rows_to_add)], ignore_index=True)

    # Combine back with other users
    # Use pd.concat properly
    dfs_to_concat = []
    if not other_users_data.empty:
        dfs_to_concat.append(other_users_data)
    if not final_user_data.empty:
        dfs_to_concat.append(final_user_data)

    if dfs_to_concat:
        updated_analytics = pd.concat(dfs_to_concat, ignore_index=True)
    else:
        updated_analytics = pd.DataFrame(
            columns=["user_id", "subject", "clean_subject", "planned_hours", "hours_studied"])

    # Save
    if hasattr(storage, 'write_csv'):
        storage.write_csv("analytics.csv", updated_analytics)
    elif hasattr(storage, 'save_csv'):
        storage.save_csv("analytics.csv", updated_analytics)
    else:
        updated_analytics.to_csv("analytics.csv", index=False)

    return final_user_data


def app(storage):
    st.markdown("<div class='card'><h3>Analytics</h3>", unsafe_allow_html=True)

    # 1. Auth Check
    user = st.session_state.get("user")
    if not user:
        st.warning("Please login to view analytics")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    uid = str(user.get("user_id")).replace('.0', '')

    # 2. SYNC DATA (The Magic Step)
    # This reads current plans and logs and backs them up to analytics.csv
    try:
        user_analytics = sync_analytics_data(storage, uid)
    except Exception as e:
        st.error(f"Error syncing data: {e}")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    if user_analytics.empty:
        st.info("No study history found.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # 3. DISPLAY CHART
    # Use the user_analytics dataframe directly

    # Formatting for Chart
    user_analytics["Subject"] = user_analytics["subject"].astype(str).str.title()
    user_analytics["planned_hours"] = pd.to_numeric(user_analytics["planned_hours"]).fillna(0.0)
    user_analytics["hours_studied"] = pd.to_numeric(user_analytics["hours_studied"]).fillna(0.0)

    # --- CHART: Planned vs Actual ---
    if not user_analytics.empty:
        fig3 = px.bar(
            user_analytics,
            x="Subject",
            y=["planned_hours", "hours_studied"],
            barmode="group",
            title="Planned vs Studied",
            labels={"value": "Hours", "variable": "Type"}
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<hr style='margin: 20px 0; opacity: 0.2;'>", unsafe_allow_html=True)

    # --- RESET BUTTON ---
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("**Reset Data**")
        st.caption("Clear your permanent analytics history AND your study logs.")

    with col2:
        if st.button("Reset Analytics", type="primary"):
            # 1. Reset 'analytics.csv' (History)
            analytics = storage.read_csv("analytics.csv")
            if analytics is not None and not analytics.empty:
                if "user_id" in analytics.columns:
                    analytics["user_id"] = analytics["user_id"].astype(str).str.replace(r'\.0$', '', regex=True)
                    # Keep ONLY other users
                    new_analytics = analytics[analytics["user_id"] != uid]

                    if hasattr(storage, 'write_csv'):
                        storage.write_csv("analytics.csv", new_analytics)
                    elif hasattr(storage, 'save_csv'):
                        storage.save_csv("analytics.csv", new_analytics)
                    else:
                        new_analytics.to_csv("analytics.csv", index=False)

            # 2. Reset 'study_logs.csv' (Active Logs)
            # We must clear the logs too, otherwise they will re-sync immediately
            logs = storage.read_csv("study_logs.csv")
            if logs is not None and not logs.empty:
                # Normalize column for check
                tgt_col = "user_id" if "user_id" in logs.columns else "userid"

                if tgt_col in logs.columns:
                    # Create temporary normalized ID for filtering
                    logs["_temp_uid"] = logs[tgt_col].astype(str).str.replace(r'\.0$', '', regex=True)
                    # Keep rows that do NOT belong to this user
                    new_logs = logs[logs["_temp_uid"] != uid].drop(columns=["_temp_uid"])

                    if hasattr(storage, 'write_csv'):
                        storage.write_csv("study_logs.csv", new_logs)
                    elif hasattr(storage, 'save_csv'):
                        storage.save_csv("study_logs.csv", new_logs)
                    else:
                        new_logs.to_csv("study_logs.csv", index=False)

            st.success("History and Logs cleared!")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)