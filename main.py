from dotenv import load_dotenv
import pandas as pd
load_dotenv()
import streamlit as st
import importlib
import pathlib
from auth import Auth
from storage import Storage

BASE_DIR = pathlib.Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

st.set_page_config(page_title="StudyPlanTracker", page_icon="📚", layout="wide", initial_sidebar_state="expanded")

css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
*{font-family:'Inter',sans-serif}

/* Hide default Streamlit chrome */
[data-testid="stSidebarNav"]{display:none!important}
[data-testid="stHeader"]{display:none!important}
footer{display:none!important}
[data-testid="collapsedControl"]{display:none!important}

/* Sidebar container: make scrollable with proper padding */
section[data-testid="stSidebar"]{
  position:fixed!important;
  top:0; left:0;
  height:100vh;
  width:300px!important; min-width:300px!important;
  transform:translateX(-260px);
  transition:transform .32s ease;
  background:rgba(255,255,255,0.96);
  backdrop-filter:blur(10px);
  border-right:1px solid #e2e8f0;
  box-shadow:4px 0 18px rgba(0,0,0,0.06);
  overflow-y:auto !important;
  -webkit-overflow-scrolling: touch !important;
  z-index:20000!important;
  padding-bottom: 100px !important; /* Increased to prevent overlap */
}
section[data-testid="stSidebar"]:hover{ transform:translateX(0); box-shadow:10px 0 30px rgba(0,0,0,0.12); }
section[data-testid="stSidebar"]::after{ content:""; position:absolute; right:0; top:0; height:90%; width:4px; background:linear-gradient(to bottom,transparent,#6366f1,transparent); opacity:.45; }

/* Header area */
div[data-testid="stSidebarUserContent"]{ padding-top:8px!important; padding-bottom:6px!important; padding-left:1rem!important; padding-right:1rem!important; }
section[data-testid="stSidebar"] h3{ margin:0 0 6px 0!important; font-size:1.05rem!important; }

/* Stack layout: reduced gap for compactness */
div[data-testid="stVerticalBlock"], section[data-testid="stSidebar"] > div{
  display:flex!important; flex-direction:column!important; gap:6px!important; align-items:stretch!important;
}

/* Menu buttons (pill style) - CONSISTENT ACROSS ALL PAGES */
section[data-testid="stSidebar"] .stButton > button,
section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] .stButton > button,
section[data-testid="stSidebar"] button[kind="secondary"]{
  display:flex!important; align-items:center!important; gap:10px!important;
  width:calc(100% - 36px)!important;
  margin:6px 18px!important;
  padding:10px 14px!important;
  background:linear-gradient(180deg,#eef2ff,#f3f4ff)!important;
  color:#4338ca!important;
  border-radius:12px!important;
  border:1px solid rgba(67,56,202,0.12)!important;
  box-shadow:0 6px 10px rgba(99,102,241,0.06)!important;
  font-weight:600!important; text-align:left!important;
  transition: padding-left .12s ease, transform .12s ease!important;
}
section[data-testid="stSidebar"] .stButton > button::before,
section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] .stButton > button::before{ 
  content:""!important; width:6px!important; height:26px!important; 
  border-radius:0 6px 6px 0!important; 
  background:linear-gradient(180deg,#5b4ef7,#7a5cff)!important; 
  margin-right:8px!important; 
}
section[data-testid="stSidebar"] .stButton > button:hover,
section[data-testid="stSidebar"] button[kind="secondary"]:hover{ 
  transform:translateX(5px)!important; 
  padding-left:18px!important;
  background:linear-gradient(180deg,#eef2ff,#f3f4ff)!important;
}
section[data-testid="stSidebar"] .stButton > button[aria-pressed="true"]{ 
  background:linear-gradient(180deg,#e1e7ff,#e7ebff)!important; 
  border-left:4px solid #4338ca!important; 
  padding-left:16px!important; 
}

/* Spacer to push logout button down and prevent overlap */
.menu-bottom-spacer{
  height:30px !important;  /* Increased height for better spacing */
  width:100%;
  flex-shrink:0;
}

/* Logout container - fixed positioning */
/* Logout pinned and visible above footer */
section[data-testid="stSidebar"] .logout-container{
  position: fixed !important;
  bottom: 80px !important;
  left: 12px !important;
  width: 276px !important;
  margin: 0 !important; 
  padding: 8px 0 !important;
  z-index: 25000 !important; 
  display: block !important;
  background: rgba(255,255,255,0.98) !important;
  backdrop-filter: blur(8px) !important;
}

/* Logout button styling */
section[data-testid="stSidebar"] .logout-container a,
section[data-testid="stSidebar"] .logout-container button{
  display:block!important; width:100%!important;
  padding:12px 16px!important; border-radius:12px!important;
  background:linear-gradient(180deg,#fff1f2,#ffe4e6)!important;
  color:#be123c!important; border:1px solid #fecdd3!important;
  font-weight:600!important; text-align:left!important; text-decoration:none!important;
  box-shadow:0 8px 14px rgba(249,115,22,0.05)!important;
  transition: all 0.2s ease !important;
}
section[data-testid="stSidebar"] .logout-container a:hover,
section[data-testid="stSidebar"] .logout-container button:hover{
  padding-left:22px!important; 
  background:#ffe4e6!important;
  box-shadow:0 10px 20px rgba(249,115,22,0.1)!important;
}

/* Small-screen fallback */
@media (max-width:900px){
  section[data-testid="stSidebar"]{ 
    transform:translateX(0)!important; 
    padding-bottom:120px!important; 
  }
  section[data-testid="stSidebar"] .logout-container{ 
    position:relative!important; 
    bottom:auto!important; 
    margin-top:20px!important;
    width: auto !important;
    left: auto !important;
  }
}

/* Keep logout button red on all pages */
section[data-testid="stSidebar"] .logout-container button[kind="secondary"]{
  background:linear-gradient(180deg,#fff1f2,#ffe4e6)!important;
  color:#be123c!important;
  border:1px solid #fecdd3!important;
}

/* FORCE logout position - Override everything */
div.logout-container,
section[data-testid="stSidebar"] div.logout-container,
.logout-container {
  position: fixed !important;
  bottom: 100px !important;
  left: 12px !important;
  width: 276px !important;
  z-index: 99999 !important;
}
</style>
"""

st.markdown(css, unsafe_allow_html=True)

storage = Storage(DATA_DIR)
storage.ensure_all_files_exist()
auth = Auth(storage)


def register_action(email, pwd, pwd2):
    if not email or not pwd:
        return False, "Email and password required"
    if pwd != pwd2:
        return False, "Passwords do not match"

    success, msg = auth.register(email, pwd)
    if not success:
        return False, msg

    user, login_msg = auth.login(email, pwd)
    if user:
        st.session_state.user = user
        st.session_state.page = "Home"
        return True, msg
    return False, "Registration failed"


def login_action(email, pwd):
    if not email or not pwd:
        return False, "Email and password required"

    user, msg = auth.login(email, pwd)
    if not user:
        return False, msg

    st.session_state.user = user
    st.session_state.page = "Home"
    return True, "Welcome back!"


def auth_page():
    form_key_suffix = st.session_state.get("auth_form_id", 0)

    st.markdown("""
        <style>
            .block-container {
                padding-top: 1rem !important;
                padding-bottom: 1rem !important;
            }
            h1 { padding-top: 0rem !important; }

            .password-requirements {
                background: #f8fafc;
                border-left: 3px solid #6366f1;
                padding: 10px 12px;
                border-radius: 6px;
                margin: 10px 0;
                font-size: 0.85rem;
            }

            .password-requirements ul {
                margin: 5px 0;
                padding-left: 20px;
            }

            .password-requirements li {
                color: #64748b;
                margin: 3px 0;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <div style="font-size: 32px; margin-bottom: 0px;">🎓</div>
            <h1 style="font-size: 2.8rem; font-weight: 800; color: #1e293b; margin: 0;">
                Study Tracker <span style="color: #6366f1;">with AI</span>
            </h1>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([5, 3], gap="large")

    with col1:
        st.markdown("""
            <div style="margin-top: 10px;">
                <h2 style="font-size: 2.5rem; font-weight: 800; line-height: 1.1; color: #1e293b; margin-bottom: 15px;">
                    Master Your <br>
                    <span style="color: #6366f1;">Learning Journey</span>
                </h2>
                <p style="font-size: 1.1rem; color: #64748b; margin-bottom: 25px; line-height: 1.4;">
                    Stop guessing what to study. Let AI organize your schedule, 
                    track your progress, and help you achieve your goals.
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="display: flex; gap: 10px; flex-direction: column;">
            <div style="background-color:#f0f9ff; padding:12px; border-radius:8px; border-left: 5px solid #0ea5e9;">
                🤖 <strong>AI Assistant</strong> answers doubts instantly
            </div>
            <div style="background-color:#f0fdf4; padding:12px; border-radius:8px; border-left: 5px solid #22c55e;">
                📊 <strong>Visual Analytics</strong> track your growth
            </div>
            <div style="background-color:#fff7ed; padding:12px; border-radius:8px; border-left: 5px solid #f97316;">
                ⚡ <strong>Smart Planner</strong> for productivity
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        mode = st.session_state.get("auth_mode", "login")

        with st.container(border=True):
            if mode == "login":
                st.subheader("Sign In")
                with st.form(key=f"login_form_{form_key_suffix}"):
                    email = st.text_input("Email", key=f"login_email_{form_key_suffix}",
                                          placeholder="user@example.com")
                    pwd = st.text_input("Password", type="password", key=f"login_pwd_{form_key_suffix}",
                                        placeholder="••••••••")
                    submitted = st.form_submit_button("Sign In", use_container_width=True)

                if submitted:
                    ok, msg = login_action(email, pwd)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

                st.markdown("---")
                c1, c2 = st.columns([1.5, 1])
                c1.markdown("<div style='padding-top: 8px; font-size: 0.9rem; color: #64748b'>New here?</div>",
                            unsafe_allow_html=True)
                if c2.button("Sign Up", type="secondary", use_container_width=True,
                             key=f"switch_signup_{form_key_suffix}"):
                    st.session_state.auth_mode = "signup"
                    st.session_state.auth_form_id = st.session_state.get("auth_form_id", 0) + 1
                    st.rerun()

            else:
                st.subheader("Create Account")

                # Password requirements info
                st.markdown("""
                    <div class="password-requirements">
                        <strong>Password Requirements:</strong>
                        <ul>
                            <li>At least 8 characters</li>
                            <li>Contains letters (a-z, A-Z)</li>
                            <li>Contains numbers (0-9)</li>
                            <li>Contains special characters (!@#$%...)</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)

                with st.form(key=f"signup_form_{form_key_suffix}"):
                    email = st.text_input("Email", key=f"signup_email_{form_key_suffix}",
                                          placeholder="user@example.com")
                    pwd = st.text_input("Password", type="password", key=f"signup_pwd_{form_key_suffix}",
                                        placeholder="Strong@Pass123")
                    pwd2 = st.text_input("Confirm Password", type="password", key=f"signup_pwd2_{form_key_suffix}",
                                         placeholder="Strong@Pass123")
                    submitted = st.form_submit_button("Register", use_container_width=True)

                if submitted:
                    ok, msg = register_action(email, pwd, pwd2)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

                st.markdown("---")
                c1, c2 = st.columns([1.5, 1])
                c1.markdown("<div style='padding-top: 8px; font-size: 0.9rem; color: #64748b'>Existing user?</div>",
                            unsafe_allow_html=True)
                if c2.button("Log In", type="secondary", use_container_width=True,
                             key=f"switch_login_{form_key_suffix}"):
                    st.session_state.auth_mode = "login"
                    st.session_state.auth_form_id = st.session_state.get("auth_form_id", 0) + 1
                    st.rerun()


def render_sidebar(user):
    with st.sidebar:
        # --- USER HEADER (compact) ---
        st.markdown(f"""
            <div style="text-align:center; margin-bottom:6px;">
                <div style="font-size:32px; margin-bottom:6px;">📚</div>
                <h3 style="margin:0; color:#0f172a;">StudyTracker</h3>
                <div style="color:#64748b; font-size:0.78rem; margin-top:6px;
                            background:#f1f5f9; padding:4px 10px; border-radius:20px; display:inline-block;">
                    {user.get("email")}
                </div>
            </div>
            <div style="height:8px; border-top:1px solid #e6e8f0; margin-bottom:8px;"></div>
        """, unsafe_allow_html=True)

        # --- MENU TITLE ---
        st.markdown('<p style="font-size:12px;color:#94a3b8;font-weight:600;margin:6px 0 6px 0;">MENU</p>', unsafe_allow_html=True)

        # --- NAV MENU ---
        menu = {
            "Home": "🏠",
            "Chatbot": "🤖",
            "Add Plan": "➕",
            "Log Hours": "⏱️",
            "Analytics": "📊"
        }

        current_page = st.session_state.get("page", "Home")

        for page_name, icon in menu.items():
            label = f"{icon}  {page_name}"
            if page_name == current_page:
                st.markdown(f"""
                <style>
                div[data-testid="stVerticalBlock"] button[kind="secondary"]:nth-of-type({list(menu.keys()).index(page_name) + 1}) {{
                    background-color:#e0e7ff !important;
                    color:#4338ca !important;
                    border-left:3px solid #4338ca !important;
                }}
                </style>
                """, unsafe_allow_html=True)
                label = f"🔹 {page_name}"

            if st.button(label, key=f"nav_{page_name}", use_container_width=True):
                st.session_state.page = page_name
                st.rerun()

        # spacer to ensure logout doesn't overlap menu
        st.markdown("<div class='menu-bottom-spacer'></div>", unsafe_allow_html=True)

        # --- LOGOUT at bottom (anchor link triggers query param logout handler) ---
        # --- LOGOUT at bottom with inline positioning ---
        st.markdown("""
            <style>
            .custom-logout-wrapper {
                position: fixed !important;
                bottom: 80px !important;
                left: 12px !important;
                width: 276px !important;
                z-index: 25000 !important;
                background: rgba(255,255,255,0.98) !important;
                backdrop-filter: blur(8px) !important;
                padding: 8px 0 !important;
            }
            </style>
            <div class="custom-logout-wrapper">
        """, unsafe_allow_html=True)

        if st.button("🚪  Logout", key="logout_btn", use_container_width=True):
            st.session_state.clear()
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


def delete_plan_callback(index):
    """Deletes a plan by index AND its associated logs."""
    # 1. READ PLANS
    plans_df = storage.read_csv("study_plans.csv")

    if plans_df is not None and index in plans_df.index:
        # Get details BEFORE deleting to find matching logs
        row = plans_df.loc[index]
        subject_to_delete = str(row.get("subject", "")).strip().lower()
        # Ensure user_id is string and cleaned
        user_id_to_delete = str(row.get("user_id", "")).replace(".0", "")
        original_name = row.get("subject", "Unknown")

        # 2. DELETE PLAN
        plans_df = plans_df.drop(index)
        storage.write_csv("study_plans.csv", plans_df)

        # 3. DELETE ASSOCIATED LOGS
        logs_df = storage.read_csv("study_logs.csv")
        if logs_df is not None and not logs_df.empty:
            # Normalize columns
            logs_df.columns = logs_df.columns.str.strip().str.lower()
            if "userid" in logs_df.columns:
                logs_df = logs_df.rename(columns={"userid": "user_id"})

            if "user_id" in logs_df.columns and "subject" in logs_df.columns:
                # Create temp columns for accurate matching
                logs_df["_temp_uid"] = logs_df["user_id"].astype(str).str.replace(r'\.0$', '', regex=True)
                logs_df["_temp_subj"] = logs_df["subject"].astype(str).str.strip().str.lower()

                # Logic: Keep rows that do NOT match (User ID AND Subject)
                # We remove rows where user_id matches AND subject matches
                mask_keep = ~(
                            (logs_df["_temp_uid"] == user_id_to_delete) & (logs_df["_temp_subj"] == subject_to_delete))

                # Apply filter and drop temp columns
                new_logs_df = logs_df[mask_keep].drop(columns=["_temp_uid", "_temp_subj"])

                # Save only if changes occurred
                if len(new_logs_df) < len(logs_df):
                    storage.write_csv("study_logs.csv", new_logs_df)

        st.toast(f"Plan and logs for '{original_name}' deleted!", icon="🗑️")


import datetime

import datetime

import datetime
import streamlit as st


def home_page(storage):
    user = st.session_state.get("user")
    if not user:
        return

    uid = str(user.get("user_id")).replace('.0', '')

    # Greeting Logic
    current_hour = datetime.datetime.now().hour
    if 5 <= current_hour < 12:
        greeting = "Good Morning"
    elif 12 <= current_hour < 18:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"

    # --- STYLES ---
    st.markdown("""
    <style>
    /* Quick Action Cards */
    .qa-card {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        padding: 20px;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        transition: transform 0.2s;
        height: 100%;
        display: flex; 
        flex-direction: column; 
        justify-content: center;
    }
    .qa-card:hover { transform: translateY(-5px); }

    /* Plan Cards */
    .plan-card-container {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        display: flex;
        align-items: center;
    }

    /* Floating Icon */
    @keyframes float { 0% {transform: translateY(0px);} 50% {transform: translateY(-8px);} 100% {transform: translateY(0px);} }
    .floating-icon { display: inline-block; animation: float 3s ease-in-out infinite; }
    </style>
    """, unsafe_allow_html=True)

    # HEADER
    email_name = user.get("email").split('@')[0].title() if user.get("email") else "User"
    st.markdown(f"<h1>{greeting}, {email_name} <span class='floating-icon'>👋</span></h1>", unsafe_allow_html=True)

    # QUICK ACTIONS
    st.markdown("### 🚀 Quick Actions")
    c1, c2, c3 = st.columns(3)

    actions = [
        ("📅", "Add Plan", "Add Plan", c1),
        ("⏱️", "Log Hours", "Log Hours", c2),
        ("🤖", "AI Tutor", "Chatbot", c3)
    ]

    for icon, title, page_name, col in actions:
        with col:
            st.markdown(f"""
            <div class="qa-card">
                <div style="font-size: 2rem; margin-bottom: 10px;">{icon}</div>
                <div style="font-weight: 600; font-size: 1.1rem;">{title}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Open {title}", key=f"btn_{title}", use_container_width=True):
                st.session_state.page = page_name
                st.rerun()

    # YOUR PLANS SECTION - FILTER OUT LOGGED PLANS
    st.markdown("### 📚 Your Active Study Plans")
    plans = storage.read_csv("study_plans.csv")
    logs = storage.read_csv("study_logs.csv")

    if plans is not None and not plans.empty and "user_id" in plans.columns:
        # Get user's plans
        u_plans = plans[plans["user_id"].astype(str).str.replace(r'\.0$', '', regex=True) == uid].copy()

        if not u_plans.empty:
            # Get logged subjects for this user
            logged_subjects = set()
            if logs is not None and not logs.empty:
                # Normalize column names
                logs.columns = logs.columns.str.strip().str.lower()
                if "userid" in logs.columns:
                    logs = logs.rename(columns={"userid": "user_id"})

                if "user_id" in logs.columns and "subject" in logs.columns:
                    # Get logs for current user
                    user_logs = logs[logs["user_id"].astype(str).str.replace(r'\.0$', '', regex=True) == uid]

                    # Extract unique subjects that have been logged
                    logged_subjects = set(user_logs["subject"].astype(str).str.strip().str.lower().unique())

            # Filter out plans that have been logged
            active_plans = u_plans[~u_plans["subject"].astype(str).str.strip().str.lower().isin(logged_subjects)]

            if not active_plans.empty:
                for idx, row in active_plans.iterrows():
                    with st.container():
                        st.markdown(f"""
                        <div class="plan-card-container">
                            <div style="flex-grow:1;">
                                <strong style="color:#4338ca; font-size:1.1rem;">{row.get('subject')}</strong><br>
                                <span style="color:#64748b;">{row.get('goal', 'No description')}</span>
                            </div>
                            <div style="text-align:right; margin-right:15px;">
                                <span style="background:#e0e7ff; color:#3730a3; padding:7px 8px; border-radius:6px; font-size:0.8rem;">
                                    ⏳ {row.get('planned_hours')}h
                                </span><br>
                                <span style="font-size:0.8rem; color:#94a3b8;">{row.get('date')}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        c_spacer, c_del = st.columns([16, 1])
                        with c_del:
                            if st.button("🗑️", key=f"del_{idx}"):
                                plans = plans.drop(idx)
                                storage.write_csv("study_plans.csv", plans)
                                st.toast("Plan Deleted!")
                                st.rerun()
            else:
                st.success("🎉 All plans have been logged! Great work!")
                st.info("Add new plans or check **Analytics** to see your progress.")
        else:
            st.info("No active plans. Click **Add Plan** to get started!")
    else:
        st.info("No plans found. Click **Add Plan** to create your first study plan!")


def main():
    # Initialize session state
    if "page" not in st.session_state:
        st.session_state.page = "Home"
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"
    if "auth_form_id" not in st.session_state:
        st.session_state.auth_form_id = 0

    user = st.session_state.get("user", None)

    # If not logged in, show auth page
    if not user:
        auth_page()
        return  # IMPORTANT: Stop here, don't continue

    # Only execute this if user is logged in
    render_sidebar(user)

    # Route to correct page
    current_page = st.session_state.page

    if current_page == "Home":
        home_page(storage)
    elif current_page == "Add Plan":
        importlib.import_module("pages.1_Add_Plan").app(storage)
    elif current_page == "Log Hours":
        importlib.import_module("pages.2_Log_Hours").app(storage)
    elif current_page == "Analytics":
        importlib.import_module("pages.3_Analytics").app(storage)
    elif current_page == "Chatbot":
        importlib.import_module("pages.4_Chatbot").app(storage)


if __name__ == "__main__":
    main()

