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

    /* ADD THESE 2 LINES: */
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
    # --- CSS: REMOVE PADDING & ADJUST LAYOUT ---
    st.markdown("""
        <style>
            /* Remove default top padding to prevent scrolling */
            .block-container {
                padding-top: 1rem !important;
                padding-bottom: 1rem !important;
            }
            /* Ensure the title is tight against the top */
            h1 { padding-top: 0rem !important; }
        </style>
    """, unsafe_allow_html=True)

    # --- HEADER ---
    st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <div style="font-size: 32px; margin-bottom: 0px;">🎓</div>
            <h1 style="font-size: 2.8rem; font-weight: 800; color: #1e293b; margin: 0;">
                Study Tracker <span style="color: #6366f1;">with AI</span>
            </h1>
        </div>
    """, unsafe_allow_html=True)

    # --- MAIN COLUMNS ---
    # Changed ratio: Left side (5) is now much wider than Right side (3)
    # Added gap="large" for better visual separation without using a spacer column
    col1, col2 = st.columns([5, 3], gap="large")

    with col1:
        # Increased font size back to 2.8rem (bigger) since we have more width now
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

        # Feature Highlights (Compact but readable)
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

        # Added a card-like effect for the login form
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
                        st.success(msg);
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
                        st.success(msg);
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

        menu = {"Home": "🏠", "Add Plan": "➕", "Log Hours": "⏱️", "Analytics": "📊", "Chatbot": "🤖"}
        st.markdown('<p style="font-size: 12px; color: #94a3b8; font-weight: 600; margin-top: 20px;">MENU</p>',
                    unsafe_allow_html=True)
        current_page = st.session_state.get("page", "Home")

        for page_name, icon in menu.items():
            label = f"{icon}  {page_name}"
            if page_name == current_page: label = f"🔵  {page_name}"
            if st.button(label, key=f"nav_{page_name}", use_container_width=True):
                st.session_state.page = page_name
                st.rerun()

        # LOGOUT BUTTON - Full Width & Left Aligned
        st.markdown('<div class="logout-container">', unsafe_allow_html=True)
        # Added use_container_width=True to fix alignment
        if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


def home_page():
    user = st.session_state.get("user")
    st.markdown(f"""
        <h1 style='font-size: 2.5rem; margin-bottom: 0;'>Hello, {user.get("email").split('@')[0].title()} 👋</h1>
        <p style='color: #64748b; margin-bottom: 40px;'>Here is your daily activity overview.</p>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
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
    st.markdown("### 📅 Recent Study Plans", unsafe_allow_html=True)
    plans = storage.read_csv("study_plans.csv")
    if plans is not None and not plans.empty:
        user_plans = plans[plans["user_id"] == uid].tail(3)
        for index, row in user_plans.iterrows():
            with st.container():
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