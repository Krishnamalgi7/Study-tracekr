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


def home_page():
    user = st.session_state.get("user")
    uid = str(user.get("user_id")).replace('.0', '')

    # Modern glassmorphism and particle animations
    st.markdown("""
    <style>
    /* Animated particles background */
    @keyframes particle-float {
        0%, 100% { 
            transform: translate(0, 0) rotate(0deg);
            opacity: 0.3;
        }
        33% { 
            transform: translate(30px, -30px) rotate(120deg);
            opacity: 0.6;
        }
        66% { 
            transform: translate(-20px, 20px) rotate(240deg);
            opacity: 0.4;
        }
    }

    /* Fade in up animation */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Scale pop animation */
    @keyframes scalePop {
        0% {
            transform: scale(0.8);
            opacity: 0;
        }
        50% {
            transform: scale(1.05);
        }
        100% {
            transform: scale(1);
            opacity: 1;
        }
    }

    /* Floating particles */
    .particle {
        position: fixed;
        width: 10px;
        height: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        pointer-events: none;
        z-index: 0;
        animation: particle-float 8s ease-in-out infinite;
    }

    .particle:nth-child(1) { top: 10%; left: 10%; animation-delay: 0s; }
    .particle:nth-child(2) { top: 20%; left: 80%; animation-delay: 1s; }
    .particle:nth-child(3) { top: 60%; left: 15%; animation-delay: 2s; }
    .particle:nth-child(4) { top: 80%; left: 70%; animation-delay: 3s; }
    .particle:nth-child(5) { top: 40%; left: 90%; animation-delay: 1.5s; }

    /* Glassmorphism cards - UPDATED BACKGROUND FOR WHITE TEXT */
    [data-testid="stVerticalBlock"] > div[data-testid="element-container"] > div[data-testid="stVerticalBlock"] {
        backdrop-filter: blur(20px) !important;
        /* Changed to dark gradient so white text is visible */
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.9), rgba(118, 75, 162, 0.9)) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.15) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        overflow: hidden !important;
        border-radius: 16px !important;
    }

    [data-testid="stVerticalBlock"] > div[data-testid="element-container"] > div[data-testid="stVerticalBlock"]:hover {
        transform: translateY(-8px) scale(1.02) !important;
        box-shadow: 0 20px 60px rgba(99, 102, 241, 0.3) !important;
    }

    /* Header animations */
    .modern-header {
        animation: fadeInUp 0.8s ease-out;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800 !important;
        letter-spacing: -1px;
    }

    .subtitle {
        animation: fadeInUp 1s ease-out 0.2s backwards;
        font-size: 1.1rem;
        color: #64748b;
    }

    /* Quick actions animations */
    .action-card-1 { animation: scalePop 0.5s ease-out 0.3s backwards; }
    .action-card-2 { animation: scalePop 0.5s ease-out 0.5s backwards; }
    .action-card-3 { animation: scalePop 0.5s ease-out 0.7s backwards; }

    /* Modern buttons - UPDATED TO WHITE/TRANSPARENT STYLE */
    .stButton > button {
        background: rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.5) !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        background: white !important;
        color: #667eea !important;
        transform: translateY(-2px) scale(1.05) !important;
    }

    /* Section title - UPDATED TO BLACK */
    .section-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #000000 !important; /* Changed from Gradient to Black */
        margin-bottom: 20px;
        animation: fadeInUp 0.6s ease-out;
    }

    /* Plan cards */
    .plan-card {
        background: white !important; /* Keep plan cards white */
        border: 2px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 20px !important;
        transition: all 0.4s ease !important;
        animation: fadeInUp 0.5s ease-out;
        color: black !important;
    }

    .plan-card:hover {
        transform: translateX(10px) scale(1.02) !important;
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.15) !important;
        border-color: #667eea !important;
    }

    /* Badge style */
    .hours-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 700;
        display: inline-block;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }

    /* Icon animations */
    .icon-bounce {
        display: inline-block;
        animation: iconBounce 2s ease-in-out infinite;
    }

    @keyframes iconBounce {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        25% { transform: translateY(-5px) rotate(-10deg); }
        75% { transform: translateY(-3px) rotate(10deg); }
    }

    /* Smooth divider */
    .fancy-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 30px 0;
        animation: fadeInUp 0.8s ease-out;
    }
    </style>

    <div class="particle"></div>
    <div class="particle"></div>
    <div class="particle"></div>
    <div class="particle"></div>
    <div class="particle"></div>
    """, unsafe_allow_html=True)

    # --- MODERN HEADER ---
    st.markdown(f"""
        <h1 class="modern-header" style='font-size: 2.8rem; margin-bottom: 10px;'>
            Hello, {user.get("email").split('@')[0].title()} <span class="icon-bounce">👋</span>
        </h1>
        <p class="subtitle">Here is your daily activity overview.</p>
    """, unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)

    # --- QUICK ACTIONS ---
    # UPDATED: Replaced emoji with BLACK text styling class
    st.markdown('<h3 class="section-title"><span class="icon-bounce">🚀</span> Quick Actions</h3>',
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    cols = [col1, col2, col3]
    actions = [
        ("➕", "Add Plan", "Schedule a session", "Add Plan", "home_planner"),
        ("⏱️", "Log Hours", "Track progress", "Log Hours", "home_log"),
        ("🤖", "AI Tutor", "Ask doubts", "Chatbot", "home_ai")
    ]

    for idx, (col, (icon, title, desc, page, key)) in enumerate(zip(cols, actions)):
        with col:
            st.markdown(f'<div class="action-card-{idx + 1}">', unsafe_allow_html=True)
            with st.container(border=True):
                # UPDATED: Added color: white !important to text
                st.markdown(f"<h4 style='margin:0; font-size:1.3rem; color: white !important;'>{icon} {title}</h4>", unsafe_allow_html=True)
                st.markdown(f"<p style='color: white !important; margin:10px 0; opacity: 0.9;'>{desc}</p>", unsafe_allow_html=True)
                if st.button(f"Go to {title}", use_container_width=True, key=key):
                    st.session_state.page = page
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)

    # --- YOUR PLANS ---
    # UPDATED: Replaced emoji with BLACK text styling class
    st.markdown('<h3 class="section-title"><span class="icon-bounce">📅</span> Your Study Plans</h3>',
                unsafe_allow_html=True)

    plans = storage.read_csv("study_plans.csv")

    if plans is not None and not plans.empty and "user_id" in plans.columns:
        plans["user_id"] = plans["user_id"].astype(str).str.replace(r'\.0$', '', regex=True)
        user_plans = plans[plans["user_id"] == uid]

        if not user_plans.empty:
            user_plans = user_plans.sort_index(ascending=False)

            for index, row in user_plans.iterrows():
                st.markdown('<div class="plan-card">', unsafe_allow_html=True)
                with st.container(border=True):
                    c_info, c_hours, c_action = st.columns([4, 2, 1])

                    with c_info:
                        # Black text inside the white plan cards
                        st.markdown(f"**📚 {row.get('subject', 'Untitled')}**")
                        st.caption(row.get('goal', 'No description'))

                    with c_hours:
                        st.markdown(f"""
                        <div class="hours-badge">
                            ⏰ {row.get('planned_hours', 0)}h
                        </div>
                        """, unsafe_allow_html=True)
                        st.caption(f"📅 {row.get('date')}")

                    with c_action:
                        st.button(
                            "🗑️",
                            key=f"home_del_{index}",
                            help="Delete this plan",
                            on_click=delete_plan_callback,
                            args=(index,)
                        )
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("✨ You don't have any active plans. Click 'Add Plan' to get started!")
    else:
        st.info("✨ No plans found. Click 'Add Plan' to create your first study plan!")


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
