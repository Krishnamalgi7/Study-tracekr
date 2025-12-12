from dotenv import load_dotenv

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

* { font-family: 'Inter', sans-serif; }

/* 1. HIDE DEFAULT ELEMENTS */
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

/* 2. THE FLOATING SIDEBAR MAGIC */
section[data-testid="stSidebar"] {
    position: fixed !important; 
    top: 0;
    left: 0;
    height: 100vh;
    z-index: 100000;
    width: 300px !important;
    min-width: 300px !important;
    transform: translateX(-285px); 
    transition: transform 0.4s cubic-bezier(0.25, 1, 0.5, 1); 
    background-color: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-right: 1px solid #e2e8f0;
    box-shadow: 4px 0 15px rgba(0,0,0,0.05);
}

section[data-testid="stSidebar"]:hover {
    transform: translateX(0);
    box-shadow: 10px 0 30px rgba(0,0,0,0.1);
}

section[data-testid="stSidebar"]::after {
    content: "";
    position: absolute;
    right: 0;
    top: 0;
    height: 100%;
    width: 4px;
    background: linear-gradient(to bottom, transparent, #6366f1, transparent);
    opacity: 0.5;
}

[data-testid="stAppViewContainer"] {
    margin-left: 0 !important;
    width: 100% !important;
    background-color: #f8fafc;
    background-image: radial-gradient(at 0% 0%, #e0e7ff 0%, transparent 50%), 
                      radial-gradient(at 100% 100%, #f3e8ff 0%, transparent 50%);
}

/* --- 3. SPACING & ALIGNMENT CONTROLS --- */

div[data-testid="stSidebarUserContent"] {
    padding-top: 20px !important;
    padding-bottom: 10px !important; 
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* LOGOUT BUTTON CONTAINER */
.logout-container {
    margin-top: 50px; /* Standard spacing */
    width: 100%;      /* Full width */
    border-top: 1px solid #e2e8f0;  /* This creates the line */
    padding-top: 15px;              /* Space BELOW the line */
}

/* LOGOUT BUTTON STYLING (MATCHING OTHER BUTTONS) */
.logout-container button {
    width: 100% !important;        /* Full Width */
    text-align: left !important;   /* Align Text Left */
    padding-left: 0.5rem !important;
    height: auto !important;

    /* Subtle Red Styling */
    background-color: #fff1f2 !important; 
    color: #e11d48 !important; 
    border: 1px solid #fecdd3 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}

.logout-container button:hover {
    background-color: #ffe4e6 !important;
    border-color: #fda4af !important;
    color: #be123c !important;
    padding-left: 1rem !important; /* Slide effect on hover */
}

/* STANDARD MENU BUTTONS */
.stButton button {
    background-color: transparent !important;
    color: #64748b !important;
    border: none !important;
    text-align: left !important;
    padding-left: 0 !important;
    font-weight: 500 !important;
    transition: all 0.2s;
}
.stButton button:hover {
    color: #6366f1 !important;
    background-color: #f1f5f9 !important;
    padding-left: 10px !important;
}

/* OTHER STYLES */
.hero-title { font-size: 3.5rem; font-weight: 800; color: #1e293b; line-height: 1.1; margin-bottom: 0.5rem; }
.hero-gradient { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero-sub { font-size: 1.2rem; color: #64748b; margin-bottom: 2rem; line-height: 1.6; }
[data-testid="stForm"] { background-color: white; padding: 2.5rem; border-radius: 20px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); border: 1px solid #e2e8f0; }
div[data-testid="stAlert"] { border-radius: 12px; border: none; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); background-color: white; }
</style>
"""

st.markdown(css, unsafe_allow_html=True)

storage = Storage(DATA_DIR)
storage.ensure_all_files_exist()
auth = Auth(storage)


def register_action(email, pwd, pwd2):
    if not email or not pwd: return False, "Email and password required"
    if pwd != pwd2: return False, "Passwords do not match"
    ok = auth.register(email, pwd)
    if not ok: return False, "Account already exists"
    user = auth.login(email, pwd)
    if user:
        st.session_state.user = user
        st.session_state.page = "Home"
        return True, "Account created successfully!"
    return False, "Registration failed"


def login_action(email, pwd):
    if not email or not pwd: return False, "Email and password required"
    user = auth.login(email, pwd)
    if not user: return False, "Invalid credentials"
    st.session_state.user = user
    st.session_state.page = "Home"
    return True, "Welcome back!"


def auth_page():
    st.markdown("""
        <style>
            .block-container {
                padding-top: 1rem !important;
                padding-bottom: 1rem !important;
            }
            h1 { padding-top: 0rem !important; }
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
                with st.form("login_form"):
                    email = st.text_input("Email", key="login_email")
                    pwd = st.text_input("Password", type="password", key="login_pwd")
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
                if c2.button("Sign Up", type="secondary", use_container_width=True):
                    st.session_state.auth_mode = "signup"
                    st.rerun()

            else:
                st.subheader("Create Account")
                with st.form("signup_form"):
                    email = st.text_input("Email", key="signup_email")
                    pwd = st.text_input("Password", type="password", key="signup_pwd")
                    pwd2 = st.text_input("Confirm", type="password", key="signup_pwd2")
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
                if c2.button("Log In", type="secondary", use_container_width=True):
                    st.session_state.auth_mode = "login"
                    st.rerun()


def render_sidebar(user):
    with st.sidebar:
        st.markdown(f"""
            <div style="margin-bottom: 20px; text-align: center;">
                <div style="font-size: 40px; margin-bottom: 10px;">📚</div>
                <h3 style="margin:0; color:#0f172a;">StudyTracker</h3>
                <div style="color: #64748b; font-size: 0.8rem; margin-top: 5px; 
                     background: #f1f5f9; padding: 4px 12px; border-radius: 20px; display: inline-block;">
                    {user.get("email")}
                </div>
            </div>
        """, unsafe_allow_html=True)

        menu = {
            "Home": "🏠",
            "Chatbot": "🤖",
            "Add Plan": "➕",
            "Log Hours": "⏱️",
            "Analytics": "📊"
        }

        st.markdown('<p style="font-size: 12px; color: #94a3b8; font-weight: 600; margin-top: 20px;">MENU</p>',
                    unsafe_allow_html=True)
        current_page = st.session_state.get("page", "Home")

        for page_name, icon in menu.items():
            label = f"{icon}  {page_name}"
            if page_name == current_page:
                st.markdown(f"""
                <style>
                div[data-testid="stVerticalBlock"] button[kind="secondary"]:nth-of-type({list(menu.keys()).index(page_name) + 1}) {{
                    background-color: #e0e7ff !important;
                    color: #4338ca !important;
                    border-left: 3px solid #4338ca !important;
                }}
                </style>
                """, unsafe_allow_html=True)
                label = f"🔹 {page_name}"

            if st.button(label, key=f"nav_{page_name}", use_container_width=True):
                st.session_state.page = page_name
                st.rerun()

        st.markdown('<div class="logout-container">', unsafe_allow_html=True)
        if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
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


def home_page():
    user = st.session_state.get("user")
    uid = str(user.get("user_id")).replace('.0', '')  # Ensure string format matches logic

    # --- HEADER ---
    st.markdown(f"""
        <h1 style='font-size: 2.5rem; margin-bottom: 0;'>Hello, {user.get("email").split('@')[0].title()} 👋</h1>
        <p style='color: #64748b; margin-bottom: 30px;'>Here is your daily activity overview.</p>
    """, unsafe_allow_html=True)

    # --- 1. QUICK ACTIONS ---
    st.markdown("### 🚀 Quick Actions")
    act1, act2, act3 = st.columns(3)

    with act1:
        with st.container(border=True):
            st.markdown("#### ➕ Add Plan")
            st.write("Schedule a session")
            if st.button("Go to Planner", use_container_width=True):
                st.session_state.page = "Add Plan"
                st.rerun()

    with act2:
        with st.container(border=True):
            st.markdown("#### ⏱️ Log Hours")
            st.write("Track progress")
            if st.button("Log Time", use_container_width=True):
                st.session_state.page = "Log Hours"
                st.rerun()

    with act3:
        with st.container(border=True):
            st.markdown("#### 🤖 AI Tutor")
            st.write("Ask doubts")
            if st.button("Ask AI", use_container_width=True):
                st.session_state.page = "Chatbot"
                st.rerun()

    st.markdown("---")

    # --- 2. YOUR PLANS LIST (With Delete Button) ---
    st.markdown("### 📅 Your Study Plans")

    plans = storage.read_csv("study_plans.csv")

    if plans is not None and not plans.empty and "user_id" in plans.columns:
        # Filter for current user
        plans["user_id"] = plans["user_id"].astype(str).str.replace(r'\.0$', '', regex=True)
        user_plans = plans[plans["user_id"] == uid]

        if not user_plans.empty:
            # Sort by newest first
            user_plans = user_plans.sort_index(ascending=False)

            for index, row in user_plans.iterrows():
                # We use a container with a border for the card look
                with st.container(border=True):
                    # Create 3 columns: Info (Wide) | Hours (Narrow) | Delete (Narrow)
                    c_info, c_hours, c_action = st.columns([4, 2, 1])

                    with c_info:
                        st.markdown(f"**{row.get('subject', 'Untitled')}**")
                        st.caption(row.get('goal', 'No description'))

                    with c_hours:
                        # Display hours with a nice badge look
                        st.markdown(f"""
                        <div style="background-color: #e0e7ff; color: #4338ca; padding: 4px 10px; 
                                    border-radius: 15px; font-size: 0.85rem; text-align: center; font-weight: 600;">
                            {row.get('planned_hours', 0)}h
                        </div>
                        """, unsafe_allow_html=True)
                        st.caption(f"📅 {row.get('date')}")

                    with c_action:
                        # The Delete Button
                        # We use on_click so it happens BEFORE the app reloads
                        st.button(
                            "🗑️",
                            key=f"home_del_{index}",
                            help="Delete this plan",
                            on_click=delete_plan_callback,
                            args=(index,)
                        )
        else:
            st.info("You don't have any active plans.")
    else:
        st.info("No plans found. Click 'Add Plan' to get started!")


def main():
    if "page" not in st.session_state: st.session_state.page = "Home"
    if "auth_mode" not in st.session_state: st.session_state.auth_mode = "login"
    user = st.session_state.get("user", None)
    if not user: auth_page(); return
    render_sidebar(user)
    if st.session_state.page == "Home":
        home_page()
    elif st.session_state.page == "Add Plan":
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        importlib.import_module("pages.1_Add_Plan").app(storage)
        st.markdown('</div>', unsafe_allow_html=True)
    elif st.session_state.page == "Log Hours":
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        importlib.import_module("pages.2_Log_Hours").app(storage)
        st.markdown('</div>', unsafe_allow_html=True)
    elif st.session_state.page == "Analytics":
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        importlib.import_module("pages.3_Analytics").app(storage)
        st.markdown('</div>', unsafe_allow_html=True)
    elif st.session_state.page == "Chatbot":
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        importlib.import_module("pages.4_Chatbot").app(storage)
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()