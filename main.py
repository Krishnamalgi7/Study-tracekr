from dotenv import load_dotenv

load_dotenv()
import streamlit as st
import importlib
import pathlib
from auth import Auth
from storage import Storage

BASE_DIR = pathlib.Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

st.set_page_config(page_title="StudyPlanTracker", page_icon="📚", layout="wide", initial_sidebar_state="collapsed")

css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }

/* 1. HIDE DEFAULT STREAMLIT NAV */
[data-testid="stSidebarNav"] { display: none !important; }

/* 2. STYLE THE SIDEBAR */
[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e2e8f0;
}

/* 3. STYLE THE MAIN AREA */
[data-testid="stAppViewContainer"] {
    background-color: #f8fafc;
}

/* 4. CUSTOM BUTTONS IN SIDEBAR */
/* This makes the sidebar buttons look like menu items */
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

/* 5. METRIC CARDS FOR HOME */
div[data-testid="metric-container"] {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

div[data-testid="metric-container"] label {
    color: #64748b;
}

div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    color: #0f172a;
    font-weight: 700;
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
    ok = auth.register(email, pwd)
    if not ok:
        return False, "Account already exists"
    user = auth.login(email, pwd)
    if user:
        st.session_state.user = user
        st.session_state.page = "Home"
        return True, "Account created successfully!"
    return False, "Registration failed"


def login_action(email, pwd):
    if not email or not pwd:
        return False, "Email and password required"
    user = auth.login(email, pwd)
    if not user:
        return False, "Invalid credentials"
    st.session_state.user = user
    st.session_state.page = "Home"
    return True, "Welcome back!"


def auth_page():
    mode = st.session_state.get("auth_mode", "login")

    # Create 3 columns to center the content
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Spacer to push content down slightly
        st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

        # Header Section
        if mode == "login":
            st.markdown('<div class="auth-header">Welcome Back</div>', unsafe_allow_html=True)
            st.markdown('<div class="auth-sub">Enter your details to access your study plan</div>',
                        unsafe_allow_html=True)

            with st.form("login_form"):
                email = st.text_input("Email", key="login_email", placeholder="student@example.com")
                pwd = st.text_input("Password", type="password", key="login_pwd", placeholder="••••••••")

                # Checkbox and Forgot Password Link
                c1, c2 = st.columns([1, 1])
                with c1:
                    remember = st.checkbox("Remember me")

                submitted = st.form_submit_button("Sign In")

            if submitted:
                ok, msg = login_action(email, pwd)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

            # Switcher
            st.markdown('<div class="auth-toggle-text">New here?</div>', unsafe_allow_html=True)
            if st.button("Create an Account", type="secondary", use_container_width=True):
                st.session_state.auth_mode = "signup"
                st.rerun()

        else:  # Signup Mode
            st.markdown('<div class="auth-header">Create Account</div>', unsafe_allow_html=True)
            st.markdown('<div class="auth-sub">Start tracking your productivity today</div>', unsafe_allow_html=True)

            with st.form("signup_form"):
                email = st.text_input("Email", key="signup_email", placeholder="name@example.com")
                pwd = st.text_input("Password", type="password", key="signup_pwd", placeholder="Min 8 chars")
                pwd2 = st.text_input("Confirm Password", type="password", key="signup_pwd2",
                                     placeholder="Repeat password")

                agree = st.checkbox("I agree to the Terms & Privacy")
                submitted = st.form_submit_button("Create Account")

            if submitted:
                if not agree:
                    st.error("Please agree to the terms")
                else:
                    ok, msg = register_action(email, pwd, pwd2)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

            # Switcher
            st.markdown('<div class="auth-toggle-text">Already have an account?</div>', unsafe_allow_html=True)
            if st.button("Log In Instead", type="secondary", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()


def render_sidebar(user):
    with st.sidebar:
        # --- Logo & User Info ---
        st.markdown(f"""
            <div style="margin-bottom: 30px; text-align: center;">
                <div style="font-size: 40px; margin-bottom: 10px;">📚</div>
                <h3 style="margin:0; color:#0f172a;">StudyTracker</h3>
                <div style="color: #64748b; font-size: 0.8rem; margin-top: 5px; 
                     background: #f1f5f9; padding: 4px 12px; border-radius: 20px; display: inline-block;">
                    {user.get("email")}
                </div>
            </div>
        """, unsafe_allow_html=True)

        # --- Navigation ---
        # We use a standard dictionary for menu items
        menu = {
            "Home": "🏠",
            "Add Plan": "➕",
            "Log Hours": "⏱️",
            "Analytics": "📊",
            "Chatbot": "🤖"
        }

        st.markdown('<p style="font-size: 12px; color: #94a3b8; font-weight: 600; margin-top: 20px;">MENU</p>',
                    unsafe_allow_html=True)

        current_page = st.session_state.get("page", "Home")

        for page_name, icon in menu.items():
            # If the button is clicked, update state and rerun
            # We highlight the button if it's the current page (simulated via formatting)
            label = f"{icon}  {page_name}"
            if page_name == current_page:
                label = f"🔵  {page_name}"  # active indicator

            if st.button(label, key=f"nav_{page_name}", use_container_width=True):
                st.session_state.page = page_name
                st.rerun()

        # --- Logout Section ---
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()


def home_page():
    user = st.session_state.get("user")

    # 1. Header Section
    st.markdown(f"""
        <h1 style='font-size: 2.5rem; margin-bottom: 0;'>Hello, {user.get("email").split('@')[0].title()} 👋</h1>
        <p style='color: #64748b; margin-bottom: 40px;'>Here is your daily activity overview.</p>
    """, unsafe_allow_html=True)

    # 2. Stats Grid using Native Columns
    col1, col2, col3 = st.columns(3)

    # Calculate stats (mock data or real)
    logs = storage.read_csv("study_logs.csv")
    uid = user.get("user_id")

    total_hours = 0.0
    if logs is not None and not logs.empty:
        user_logs = logs[logs["user_id"] == uid]
        total_hours = user_logs["hours_studied"].sum() if not user_logs.empty else 0.0

    with col1:
        st.metric("Total Hours", f"{total_hours:.1f} h", delta="This Month")
    with col2:
        st.metric("Study Streak", "3 Days", delta="🔥 On Fire")
    with col3:
        st.metric("Pending Plans", "2", delta="-1 from yesterday", delta_color="inverse")

    # 3. Recent Activity Section
    st.markdown("### 📅 Recent Study Plans", unsafe_allow_html=True)

    plans = storage.read_csv("study_plans.csv")
    if plans is not None and not plans.empty:
        user_plans = plans[plans["user_id"] == uid].tail(3)  # Get last 3

        # Create a clean DataFrame view or custom cards
        for index, row in user_plans.iterrows():
            with st.container():
                # Styled Card for each plan
                st.markdown(f"""
                <div style="background: white; padding: 16px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 600; color: #0f172a; font-size: 1.1rem;">{row['subject']}</div>
                        <div style="color: #64748b; font-size: 0.9rem;">{row['goal']}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="background: #e0e7ff; color: #4338ca; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">
                            {row['planned_hours']}h Planned
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No plans yet. Click 'Add Plan' to get started!")


def main():
    if "page" not in st.session_state:
        st.session_state.page = "Home"
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    user = st.session_state.get("user", None)

    if not user:
        auth_page()
        return

    render_sidebar(user)

    if st.session_state.page == "Home":
        home_page()
    elif st.session_state.page == "Add Plan":
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        mod = importlib.import_module("pages.1_Add_Plan")
        mod.app(storage)
        st.markdown('</div>', unsafe_allow_html=True)
    elif st.session_state.page == "Log Hours":
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        mod = importlib.import_module("pages.2_Log_Hours")
        mod.app(storage)
        st.markdown('</div>', unsafe_allow_html=True)
    elif st.session_state.page == "Analytics":
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        mod = importlib.import_module("pages.3_Analytics")
        mod.app(storage)
        st.markdown('</div>', unsafe_allow_html=True)
    elif st.session_state.page == "Chatbot":
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        mod = importlib.import_module("pages.4_Chatbot")
        mod.app(storage)
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()