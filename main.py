import streamlit as st
import importlib
import pathlib
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # Load .env on startup

BASE_DIR = pathlib.Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

from auth import Auth
from storage import Storage

st.set_page_config(page_title="Study Plan Tracker", page_icon="📚", layout="wide", initial_sidebar_state="expanded")

css = """
<style>
:root{
  --bg:#0f1724;
  --card:#0b1220;
  --accent:#7c3aed;
  --muted:#94a3b8;
  --glass: rgba(255,255,255,0.03);
}
html,body,#root{
  background: linear-gradient(180deg,#02111a 0%, #041426 50%, #02111a 100%) !important;
  color: #e6eef8;
}
header {display:none}
.section-card{
  background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
  border-radius:18px;
  padding:18px;
  box-shadow: 0 6px 18px rgba(2,6,23,0.6);
  border: 1px solid rgba(255,255,255,0.03);
}
.brand{
  display:flex;
  gap:12px;
  align-items:center;
}
.brand .logo{
  width:54px;height:54px;border-radius:12px;
  background:linear-gradient(135deg, var(--accent), #60a5fa);
  display:flex;align-items:center;justify-content:center;font-weight:800;font-size:22px;color:white;
  box-shadow:0 6px 30px rgba(124,58,237,0.24);
}
.menu-card{padding:14px;border-radius:12px;background:linear-gradient(180deg, rgba(255,255,255,0.01), rgba(255,255,255,0.02));}
.small{font-size:13px;color:var(--muted)}
.huge{font-size:28px;font-weight:700}
.btn-primary{
  background: linear-gradient(90deg,var(--accent), #60a5fa) !important;
  border-radius:10px !important;
  color:white !important;
  padding:8px 14px !important;
  box-shadow:0 6px 18px rgba(96,165,250,0.12) !important;
}
.footer{color:var(--muted);font-size:13px;padding-top:18px}
.badge{
  background:rgba(255,255,255,0.04);
  padding:6px 10px;border-radius:999px;font-weight:600;color:#cbd5e1;font-size:13px;
  border:1px solid rgba(255,255,255,0.02)
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

storage = Storage(DATA_DIR)
storage.ensure_all_files_exist()
auth = Auth(storage)

def render_header():
    col1, col2 = st.columns([1,3])
    with col1:
        st.markdown(
            """
            <div class="brand">
              <div class="logo">SP</div>
              <div>
                <div style="font-size:18px;font-weight:700">StudyPlanTracker</div>
                <div class="small">Focus • Track • Improve</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

def login_view():
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Login")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        user = auth.login(email, password)
        if user:
            st.session_state.user = user
            st.success("Login successful.")
            st.rerun()
        else:
            st.error("Invalid email or password.")
    st.markdown("</div>", unsafe_allow_html=True)

def register_view():
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Create Account")

    with st.form("reg_form"):
        email = st.text_input("Email")
        pass1 = st.text_input("Password", type="password")
        pass2 = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Register")

    if submit:
        if pass1 != pass2:
            st.error("Passwords do not match.")
        else:
            ok = auth.register(email, pass1)
            if ok:
                st.success("Account created. Please login.")
            else:
                st.error("Email already registered.")
    st.markdown("</div>", unsafe_allow_html=True)

def sidebar_menu():
    st.sidebar.markdown("<div class='menu-card'>", unsafe_allow_html=True)
    if "user" in st.session_state:
        st.sidebar.write(f"Logged in as: **{st.session_state.user['email']}**")
        page = st.sidebar.radio("Navigation", ["Add Plan", "Log Hours", "Analytics", "Chatbot", "Logout"])
    else:
        page = st.sidebar.radio("Navigation", ["Home", "Login", "Register"])
    st.sidebar.markdown("</div>", unsafe_allow_html=True)
    return page

def logout():
    if "user" in st.session_state:
        del st.session_state["user"]
    st.rerun()

def load_page(name):
    try:
        module_name = {
            "Add Plan": "pages.1_Add_Plan",
            "Log Hours": "pages.2_Log_Hours",
            "Analytics": "pages.3_Analytics",
            "Chatbot": "pages.4_Chatbot"
        }.get(name)
        if module_name:
            mod = importlib.import_module(module_name)
            mod.app(storage)
    except Exception as e:
        st.error("Error loading page.")
        st.exception(e)

def home_view():
    st.markdown("<div class='section-card'><h2>Welcome to StudyPlanTracker</h2>Track your learning journey effectively.</div>", unsafe_allow_html=True)

def main():
    render_header()
    page = sidebar_menu()

    if page == "Home":
        home_view()
    elif page == "Login":
        login_view()
    elif page == "Register":
        register_view()
    elif page == "Logout":
        logout()
    else:
        if "user" not in st.session_state:
            st.warning("Please login first.")
            login_view()
            return
        load_page(page)

if __name__ == "__main__":
    main()
