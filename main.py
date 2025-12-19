from dotenv import load_dotenv
import datetime
load_dotenv()
import streamlit as st
import importlib
import pathlib
from utils.auth import Auth
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
    """Premium enhanced authentication page with stunning animations"""
    form_key_suffix = st.session_state.get("auth_form_id", 0)

    st.markdown("""
        <style>
            /* Remove default padding and make scrollable */
            .block-container {
                padding-top: 0rem !important;
                padding-bottom: 0rem !important;
                max-width: 100% !important;
            }
            
            /* Neon glow + tilt on hover */
@keyframes neonGlow {
    0%, 100% { box-shadow: 0 0 10px #667eea, 0 0 20px #667eea; }
    50% { box-shadow: 0 0 20px #f093fb, 0 0 40px #f093fb; }
}
.feature-box:hover {
    animation: neonGlow 2s ease-in-out infinite;
    transform: perspective(800px) rotateX(8deg) rotateY(8deg) scale(1.05);
    transition: transform 0.6s ease;
}

/* Bubble trail animation */
@keyframes bubbleTrail {
    0% { transform: translateY(0) scale(0.8); opacity: 0.7; }
    50% { transform: translateY(-15px) scale(1); opacity: 1; }
    100% { transform: translateY(-30px) scale(0.8); opacity: 0; }
}

/* Shimmer sweep animation */
@keyframes shimmerSweep {
    0% { left: -100%; }
    100% { left: 100%; }
}

/* Icon spin animation */
@keyframes iconSpin {
    0% { transform: scale(1) rotate(0deg); }
    50% { transform: scale(1.3) rotate(15deg); }
    100% { transform: scale(1) rotate(0deg); }
}
.feature-icon:hover {
    animation: iconSpin 0.8s ease forwards;
}


            .main {
                overflow-y: auto !important;
                height: 100vh !important;
            }

            /* Animated gradient background */
            @keyframes gradientFlow {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }

            body, .stApp {
                background: linear-gradient(-45deg, #f0f9ff, #e0f2fe, #ddd6fe, #fae8ff) !important;
                background-size: 400% 400% !important;
                animation: gradientFlow 15s ease infinite !important;
            }

            /* Header styling with gradient text */
            .main-header {
                text-align: center;
                margin-top: -20px;
                margin-bottom: 2rem;
                animation: fadeInDown 0.8s ease-out;
            }

            @keyframes fadeInDown {
                from {
                    opacity: 0;
                    transform: translateY(-30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .logo-icon {
                font-size: 48px;
                margin-bottom: 10px;
                display: inline-block;
                animation: bounce 2s ease-in-out infinite;
            }

            @keyframes bounce {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-10px); }
            }

            .gradient-text {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                animation: shimmer 3s linear infinite;
                background-size: 200% auto;
            }

            @keyframes shimmer {
                to { background-position: 200% center; }
            }

            /* Password requirements styling */
            .password-requirements {
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                border-left: 4px solid #6366f1;
                padding: 12px 15px;
                border-radius: 10px;
                margin: 12px 0;
                font-size: 0.85rem;
                box-shadow: 0 2px 8px rgba(99, 102, 241, 0.1);
            }

            .password-requirements ul {
                margin: 8px 0;
                padding-left: 22px;
            }

            .password-requirements li {
                color: #64748b;
                margin: 5px 0;
                position: relative;
            }

            .password-requirements li::marker {
                color: #6366f1;
            }

            /* Feature cards animations */
            @keyframes slideIn {
                from { 
                    opacity: 0; 
                    transform: translateX(-30px) scale(0.95);
                }
                to { 
                    opacity: 1; 
                    transform: translateX(0) scale(1);
                }
            }

            @keyframes float {
                0%, 100% { transform: translateY(0px) rotate(0deg); }
                50% { transform: translateY(-10px) rotate(5deg); }
            }

            .feature-box {
                padding: 14px 18px;
                border-radius: 16px;
                margin-bottom: 20px;
                box-shadow: 0 8px 20px rgba(0,0,0,0.08);
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                cursor: pointer;
                position: relative;
                overflow: hidden;
                animation: slideIn 0.7s ease-out backwards;
                border: 1px solid rgba(255,255,255,0.5);
                min-height: 75px;
            }

            .feature-box:nth-child(1) { animation-delay: 0.1s; }
            .feature-box:nth-child(2) { animation-delay: 0.3s; }
            .feature-box:nth-child(3) { animation-delay: 0.5s; }

            .feature-box::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 6px;
                height: 100%;
                transition: width 0.4s ease;
                border-radius: 18px 0 0 18px;
            }

            .feature-box::after {
                content: '→';
                position: absolute;
                right: 20px;
                top: 50%;
                transform: translateY(-50%) translateX(-10px);
                opacity: 0;
                transition: all 0.3s ease;
                font-size: 1.5rem;
                font-weight: bold;
            }

            .feature-box:hover {
                transform: translateX(12px) translateY(-4px) scale(1.03);
                box-shadow: 0 15px 40px rgba(0,0,0,0.15);
            }

            .feature-box:hover::before {
                width: 100%;
                opacity: 0.15;
            }

            .feature-box:hover::after {
                opacity: 0.7;
                transform: translateY(-50%) translateX(0);
            }

            .feature-icon {
                font-size: 1.7rem;
                display: inline-block;
                margin-right: 12px;
                animation: float 3s ease-in-out infinite;
                filter: drop-shadow(0 2px 5px rgba(0,0,0,0.12));
            }

            .feature-title {
                font-size: 1rem;
                font-weight: 800;
                margin-bottom: 3px;
                display: flex;
                align-items: center;
                letter-spacing: -0.3px;
            }

            .feature-desc {
                font-size: 0.82rem;
                opacity: 0.9;
                margin-left: 48px;
                line-height: 1.3;
                font-weight: 500;
            }

            .feature-box-1 {
                background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 50%, #93c5fd 100%);
                color: #1e3a8a;
            }
            .feature-box-1::before { background: linear-gradient(180deg, #3b82f6, #2563eb); }
            .feature-box-1:hover { background: linear-gradient(135deg, #bfdbfe 0%, #93c5fd 50%, #60a5fa 100%); }
            .feature-box-1::after { color: #1e3a8a; }

            .feature-box-2 {
                background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 50%, #6ee7b7 100%);
                color: #065f46;
            }
            .feature-box-2::before { background: linear-gradient(180deg, #10b981, #059669); }
            .feature-box-2:hover { background: linear-gradient(135deg, #a7f3d0 0%, #6ee7b7 50%, #34d399 100%); }
            .feature-box-2::after { color: #065f46; }

            .feature-box-3 {
                background: linear-gradient(135deg, #fed7aa 0%, #fdba74 50%, #fb923c 100%);
                color: #7c2d12;
            }
            .feature-box-3::before { background: linear-gradient(180deg, #f97316, #ea580c); }
            .feature-box-3:hover { background: linear-gradient(135deg, #fdba74 0%, #fb923c 50%, #f97316 100%); }
            .feature-box-3::after { color: #7c2d12; }

            .shine {
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
                transition: left 0.6s;
            }

            .feature-box:hover .shine {
                left: 100%;
            }

            /* Auth container styling */
            .stContainer > div {
                background: rgba(255, 255, 255, 0.95) !important;
                backdrop-filter: blur(10px) !important;
                border-radius: 20px !important;
                box-shadow: 0 20px 60px rgba(0,0,0,0.15) !important;
                border: 1px solid rgba(255, 255, 255, 0.8) !important;
            }

            /* Form button styling */
            .stButton > button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                color: white !important;
                border: none !important;
                border-radius: 12px !important;
                padding: 12px 24px !important;
                font-weight: 600 !important;
                transition: all 0.3s ease !important;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
            }

            .stButton > button:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6) !important;
            }
            
        </style>
    """, unsafe_allow_html=True)

    # Header with reduced margin
    st.markdown("""
        <div class="main-header" style="padding-top: 0.5rem; margin-bottom: 15px;">
            <div class="logo-icon">🎓</div>
            <h1 style="font-size: 2.2rem; font-weight: 900; color: #1e293b; margin: 5px 0;">
                Study Tracker <span class="gradient-text">with AI</span>
            </h1>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 1], gap="large")

    with col1:
        st.markdown("""
            <div style="margin-top: 5px;">
                <h2 style="font-size: 2.4rem; font-weight: 900; line-height: 1.1; color: #1e293b; margin-bottom: 18px; letter-spacing: -1px;">
                    Master Your<br>
                    <span style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Learning Journey</span>
                </h2>
                <p style="font-size: 1.05rem; color: #475569; margin-bottom: 22px; line-height: 1.6; font-weight: 500;">
                    Stop guessing what to study. Let AI organize your schedule, 
                    track your progress, and achieve your goals faster.
                </p>
            </div>
        """, unsafe_allow_html=True)

        # Feature cards
        st.markdown('<div style="display: flex; gap: 10px; flex-direction: column; margin-top: 15px;">',
                    unsafe_allow_html=True)

        st.markdown("""
            <div class="feature-box feature-box-1">
                <div class="shine"></div>
                <div class="feature-title">
                    <span class="feature-icon">🤖</span>
                    <span>AI Assistant</span>
                </div>
                <div class="feature-desc">Get instant, accurate answers to all your questions</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="feature-box feature-box-2">
                <div class="shine"></div>
                <div class="feature-title">
                    <span class="feature-icon">📊</span>
                    <span>Visual Analytics</span>
                </div>
                <div class="feature-desc">Track your progress with stunning chart</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="feature-box feature-box-3">
                <div class="shine"></div>
                <div class="feature-title">
                    <span class="feature-icon">⚡</span>
                    <span>Smart Planner</span>
                </div>
                <div class="feature-desc">Organize your study schedule with AI-powered insights</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div style="margin-top: 5px;"></div>', unsafe_allow_html=True)

        mode = st.session_state.get("auth_mode", "login")

        with st.container(border=True):
            if mode == "login":
                st.markdown(
                    "<h2 style='text-align: center; color: #1e293b; margin-bottom: 20px; font-weight: 800;'>Welcome Back! 👋</h2>",
                    unsafe_allow_html=True)

                with st.form(key=f"login_form_{form_key_suffix}"):
                    email = st.text_input("📧 Email", key=f"login_email_{form_key_suffix}",
                                          placeholder="eg: your@gmail.com")
                    pwd = st.text_input("🔒 Password", type="password", key=f"login_pwd_{form_key_suffix}",
                                        placeholder="Enter your password")
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    submitted = st.form_submit_button("🚀 Sign In", use_container_width=True, type="primary")

                if submitted:
                    ok, msg = login_action(email, pwd)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

                st.markdown("<hr style='margin: 20px 0; border: none; border-top: 1px solid #e2e8f0;'>",
                            unsafe_allow_html=True)

                c1, c2 = st.columns([1.4, 1])
                with c1:
                    st.markdown(
                        "<div style='padding-top: 8px; font-size: 0.95rem; color: #64748b; text-align: center;'>New here?</div>",
                        unsafe_allow_html=True)
                with c2:
                    if st.button("✨ Sign Up", type="secondary", use_container_width=True,
                                 key=f"switch_signup_{form_key_suffix}"):
                        st.session_state.auth_mode = "signup"
                        st.session_state.auth_form_id = st.session_state.get("auth_form_id", 0) + 1
                        st.rerun()

            else:
                st.markdown(
                    "<h2 style='text-align: center; color: #1e293b; margin-bottom: 20px; font-weight: 800;'>Create Account ✨</h2>",
                    unsafe_allow_html=True)

                st.markdown("""
                    <div class="password-requirements">
                        <strong style="color: #4338ca; font-size: 0.9rem;">🔐 Password Requirements:</strong>
                        <ul>
                            <li>Minimum 8 characters long</li>
                            <li>Include letters (A-Z, a-z)</li>
                            <li>Include numbers (0-9)</li>
                            <li>Include special characters (!@#$%...)</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)

                with st.form(key=f"signup_form_{form_key_suffix}"):
                    email = st.text_input("📧 Email", key=f"signup_email_{form_key_suffix}",
                                          placeholder="eg: your@gmail.com")
                    pwd = st.text_input("🔒 Password", type="password", key=f"signup_pwd_{form_key_suffix}",
                                        placeholder="eg: Strong@Pass123")
                    pwd2 = st.text_input("🔒 Confirm Password", type="password", key=f"signup_pwd2_{form_key_suffix}",
                                         placeholder="eg: Strong@Pass123")
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    submitted = st.form_submit_button("🎉 Create Account", use_container_width=True, type="primary")

                if submitted:
                    ok, msg = register_action(email, pwd, pwd2)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

                st.markdown("<hr style='margin: 20px 0; border: none; border-top: 1px solid #e2e8f0;'>",
                            unsafe_allow_html=True)

                c1, c2 = st.columns([1.4, 1])
                with c1:
                    st.markdown(
                        "<div style='padding-top: 8px; font-size: 0.95rem; color: #64748b; text-align: center;'>Have an account?</div>",
                        unsafe_allow_html=True)
                with c2:
                    if st.button("👋 Sign In", type="secondary", use_container_width=True,
                                 key=f"switch_login_{form_key_suffix}"):
                        st.session_state.auth_mode = "login"
                        st.session_state.auth_form_id = st.session_state.get("auth_form_id", 0) + 1
                        st.rerun()

        # Footer info
        st.markdown("""
            <div style="margin-top: 20px; text-align: center; padding: 15px; background: rgba(255,255,255,0.7); border-radius: 12px;">
                <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 8px;">
                    🔒 Your data is secure and encrypted
                </div>
                <div style="font-size: 0.75rem; color: #94a3b8;">
                    Note: To permanently delete your account contact krishnamalgi7@gmail.com from your registered email address.
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Workflow ladder section BELOW the columns
    st.markdown(
        '<div style="margin-top: 60px; padding-top: 20px; border-top: 2px solid rgba(99, 102, 241, 0.1);"></div>',
        unsafe_allow_html=True)

    st.markdown("""
        <style>
            @keyframes float {
                0%, 100% { transform: translateY(0px); }
                50% { transform: translateY(-15px); }
            }

            @keyframes shine {
                0% { left: -100%; }
                100% { left: 100%; }
            }

            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }

            @keyframes glow {
                0%, 100% { box-shadow: 0 8px 25px rgba(0,0,0,0.1); }
                50% { box-shadow: 0 12px 35px rgba(99, 102, 241, 0.3); }
            }

            .workflow-card {
                animation: float 4s ease-in-out infinite;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }

            .workflow-card:nth-child(1) { animation-delay: 0s; }
            .workflow-card:nth-child(2) { animation-delay: 0.5s; }
            .workflow-card:nth-child(3) { animation-delay: 1s; }
            .workflow-card:nth-child(4) { animation-delay: 1.5s; }

            .workflow-card:hover {
                transform: translateY(-20px) scale(1.05) !important;
                box-shadow: 0 20px 50px rgba(0,0,0,0.2) !important;
            }

            .workflow-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent);
                animation: shine 3s infinite;
            }

            .workflow-badge {
                animation: pulse 2s ease-in-out infinite;
                position: relative;
            }

            .workflow-icon {
                animation: float 3s ease-in-out infinite;
                display: inline-block;
            }

            .success-badge {
                animation: pulse 2.5s ease-in-out infinite, glow 2s ease-in-out infinite;
            }
        </style>

        <div style="max-width: 1400px; margin: 0 auto; text-align: center; padding: 0 20px;">
            <h3 style="font-size: 2rem; font-weight: 900; color: #1e293b; margin-bottom: 40px; letter-spacing: -1px;">
                🎯 Your Learning Workflow
            </h3>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 25px; max-width: 1200px; margin: 0 auto; padding: 0 20px;">
            <div class="workflow-card" style="text-align: center; padding: 30px 20px; background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); border-radius: 20px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); min-height: 300px;">
                <div class="workflow-badge" style="background: #3b82f6; color: white; width: 60px; height: 60px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: 900; font-size: 2rem; margin-bottom: 15px; box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);">1</div>
                <div class="workflow-icon" style="font-size: 3.5rem; margin-bottom: 15px;">📝</div>
                <div style="font-weight: 900; color: #1e3a8a; font-size: 1.3rem; margin-bottom: 10px; letter-spacing: -0.5px; position: relative; z-index: 1;">Create Plan</div>
                <div style="font-size: 0.95rem; color: #1e40af; line-height: 1.4; font-weight: 500; position: relative; z-index: 1;">Define subjects, study hours and date</div>
            </div>
            <div class="workflow-card" style="text-align: center; padding: 30px 20px; background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); border-radius: 20px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); min-height: 300px;">
                <div class="workflow-badge" style="background: #10b981; color: white; width: 60px; height: 60px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: 900; font-size: 2rem; margin-bottom: 15px; box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);">2</div>
                <div class="workflow-icon" style="font-size: 3.5rem; margin-bottom: 15px;">⏱️</div>
                <div style="font-weight: 900; color: #065f46; font-size: 1.3rem; margin-bottom: 10px; letter-spacing: -0.5px; position: relative; z-index: 1;">Log Hours</div>
                <div style="font-size: 0.95rem; color: #047857; line-height: 1.4; font-weight: 500; position: relative; z-index: 1;">Record completed study sessions</div>
            </div>
            <div class="workflow-card" style="text-align: center; padding: 30px 20px; background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-radius: 20px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); min-height: 300px;">
                <div class="workflow-badge" style="background: #f59e0b; color: white; width: 60px; height: 60px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: 900; font-size: 2rem; margin-bottom: 15px; box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);">3</div>
                <div class="workflow-icon" style="font-size: 3.5rem; margin-bottom: 15px;">🤖</div>
                <div style="font-weight: 900; color: #78350f; font-size: 1.3rem; margin-bottom: 10px; letter-spacing: -0.5px; position: relative; z-index: 1;">Ask AI</div>
                <div style="font-size: 0.95rem; color: #92400e; line-height: 1.4; font-weight: 500; position: relative; z-index: 1;">Get instant explanations & practice support</div>
            </div>
            <div class="workflow-card" style="text-align: center; padding: 30px 20px; background: linear-gradient(135deg, #e9d5ff 0%, #d8b4fe 100%); border-radius: 20px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); min-height: 300px;">
                <div class="workflow-badge" style="background: #a855f7; color: white; width: 60px; height: 60px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: 900; font-size: 2rem; margin-bottom: 15px; box-shadow: 0 6px 20px rgba(168, 85, 247, 0.4);">4</div>
                <div class="workflow-icon" style="font-size: 3.5rem; margin-bottom: 15px;">📊</div>
                <div style="font-weight: 900; color: #581c87; font-size: 1.3rem; margin-bottom: 10px; letter-spacing: -0.5px; position: relative; z-index: 1;">View Analytics</div>
                <div style="font-size: 0.95rem; color: #6b21a8; line-height: 1.4; font-weight: 500; position: relative; z-index: 1;">Compare planned vs. logged progress</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="text-align: center; margin-top: 50px; margin-bottom: 40px;">
            <div class="success-badge" style="display: inline-block; padding: 18px 40px; background: linear-gradient(135deg, #fbbf24, #f59e0b); border-radius: 50px; color: white; font-weight: 900; font-size: 1.3rem; box-shadow: 0 10px 30px rgba(251, 191, 36, 0.5); border: 3px solid white;">
                🎉 Achieve Your Goals!
            </div>
        </div>
    """, unsafe_allow_html=True)


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

    # --- ENHANCED STYLES ---
    st.markdown("""
    <style>
    /* Page Background Gradient */
    .stApp {
        background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 25%, #fae8ff 50%, #f3e8ff 75%, #f5f3ff 100%);
        background-size: 400% 400%;
        animation: gradientBackground 15s ease infinite;
    }

    @keyframes gradientBackground {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Gradient Background Animation */
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Quick Action Cards with Gradient Animation */
    .qa-card {
        background: linear-gradient(-45deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-size: 200% 200%;
        animation: gradientShift 6s ease infinite;
        padding: 25px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        display: flex; 
        flex-direction: column; 
        justify-content: center;
        position: relative;
        overflow: hidden;
    }

    .qa-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: shimmer 3s ease-in-out infinite;
    }

    @keyframes shimmer {
        0%, 100% { transform: translate(-25%, -25%) rotate(0deg); }
        50% { transform: translate(25%, 25%) rotate(180deg); }
    }

    .qa-card:hover { 
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.6);
    }

    /* Plan Cards with Hover Effects */
    .plan-card-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        border: 2px solid transparent;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        display: flex;
        align-items: center;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }

    .plan-card-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.1), transparent);
        transition: left 0.5s ease;
    }

    .plan-card-container:hover::before {
        left: 100%;
    }

    .plan-card-container:hover {
        border-color: #8b5cf6;
        box-shadow: 0 8px 25px rgba(139, 92, 246, 0.2);
        transform: translateX(5px);
    }

    /* Floating Icon Animation */
    @keyframes float { 
        0%, 100% {transform: translateY(0px) rotate(0deg);} 
        25% {transform: translateY(-10px) rotate(5deg);} 
        75% {transform: translateY(-5px) rotate(-5deg);} 
    }
    .floating-icon { 
        display: inline-block; 
        animation: float 3s ease-in-out infinite;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
    }

    /* Pulse Animation for Icons */
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }

    .qa-card-icon {
        display: inline-block;
        animation: pulse 2s ease-in-out infinite;
        font-size: 2.5rem;
        margin-bottom: 12px;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));
    }

    /* Header Gradient Text */
    .gradient-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientShift 4s ease infinite;
        font-weight: 800;
        margin-bottom: 30px;
    }

    /* Section Headers */
    .section-header {
        color: #4338ca;
        font-weight: 700;
        margin-top: 40px;
        margin-bottom: 20px;
        position: relative;
        display: inline-block;
    }

    .section-header::after {
        content: '';
        position: absolute;
        bottom: -5px;
        left: 0;
        width: 60%;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 2px;
        animation: expandLine 2s ease-in-out infinite;
    }

    @keyframes expandLine {
        0%, 100% { width: 60%; }
        50% { width: 80%; }
    }

    /* Badge Animation */
    .plan-badge {
        background: linear-gradient(135deg, #e0e7ff 0%, #ddd6fe 100%);
        color: #3730a3;
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        animation: fadeInScale 0.5s ease-out;
    }

    @keyframes fadeInScale {
        from {
            opacity: 0;
            transform: scale(0.8);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }

    /* Subject Title Glow */
    .subject-title {
        color: #4338ca;
        font-size: 1.15rem;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(67, 56, 202, 0.3);
        transition: all 0.3s ease;
    }

    .plan-card-container:hover .subject-title {
        text-shadow: 0 0 15px rgba(67, 56, 202, 0.5);
    }

    /* Fade In Animation for Cards */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .plan-card-container {
        animation: fadeInUp 0.6s ease-out backwards;
    }

    .plan-card-container:nth-child(1) { animation-delay: 0.1s; }
    .plan-card-container:nth-child(2) { animation-delay: 0.2s; }
    .plan-card-container:nth-child(3) { animation-delay: 0.3s; }
    .plan-card-container:nth-child(4) { animation-delay: 0.4s; }

    /* Success/Info Box Enhancement */
    .stSuccess, .stInfo {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border-left: 5px solid #10b981;
        border-radius: 12px;
        animation: slideIn 0.5s ease-out;
    }

    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # HEADER WITH GRADIENT
    email_name = user.get("email").split('@')[0].title() if user.get("email") else "User"
    st.markdown(f"<h1 class='gradient-header'>{greeting}, {email_name} <span class='floating-icon'>👋</span></h1>",
                unsafe_allow_html=True)

    # QUICK ACTIONS
    st.markdown("<div class='section-header'>🚀 Quick Actions</div>", unsafe_allow_html=True)
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
                <div class="qa-card-icon">{icon}</div>
                <div style="font-weight: 700; font-size: 1.15rem; letter-spacing: 0.5px; position: relative; z-index: 1;">{title}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Open {title}", key=f"btn_{title}", use_container_width=True):
                st.session_state.page = page_name
                st.rerun()

    # YOUR PLANS SECTION - FILTER OUT LOGGED PLANS
    st.markdown("<div class='section-header'>📚 Your Active Study Plans</div>", unsafe_allow_html=True)
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
                                <div class="subject-title">{row.get('subject')}</div>
                                <span style="color:#64748b; font-size: 0.95rem;">{row.get('goal', 'No description')}</span>
                            </div>
                            <div style="text-align:right; margin-right:15px;">
                                <span class="plan-badge">
                                    ⏳ {row.get('planned_hours')}h
                                </span><br>
                                <span style="font-size:0.85rem; color:#94a3b8; margin-top: 5px; display: inline-block;">📅 {row.get('date')}</span>
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

