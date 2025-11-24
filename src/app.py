import streamlit as st
from auth import authenticate, set_logged_in_user, logout
from components import LOGO_PATH

st.set_page_config(page_title="TempoRec", page_icon=LOGO_PATH, layout="wide")

# -----------------------------------------------------------
# SESSION INITIALIZATION
# -----------------------------------------------------------
if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False
if "username" not in st.session_state:
    st.session_state.username = "guest"
if "role" not in st.session_state:
    st.session_state.role = "guest"


# -----------------------------------------------------------
# LOGIN PAGE (custom)
# -----------------------------------------------------------
def login_page():
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {display: none !important;}
        [data-testid="stSidebarNav"] {display: none !important;}
        .login-container {
            max-width: 450px;
            margin: 10% auto;
            padding: 2.5rem;
            border-radius: 14px;
            background: white;
            box-shadow: 0 8px 26px rgba(0,0,0,0.08);
        }
        </style>
    """, unsafe_allow_html=True)

    # st.markdown('<div class="login-container">', unsafe_allow_html=True)

    
    st.image(LOGO_PATH, width=180)
    st.markdown("##### Personalized Retail Recommendation System")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        col1, col2 = st.columns(2)
        login_btn = col1.form_submit_button("Login", type="primary")
        guest_btn = col2.form_submit_button("Continue as Guest")

    if login_btn:
        role = authenticate(username, password)
        if role:
            set_logged_in_user(username, role)
            st.rerun()
        else:
            st.error("Invalid credentials")

    if guest_btn:
        set_logged_in_user("guest", "guest")
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------------
# PROTECT ALL PAGES
# -----------------------------------------------------------
if not st.session_state.is_authenticated:
    login_page()
    st.stop()

# -----------------------------------------------------------
# NEW STREAMLIT NAVIGATION API
# -----------------------------------------------------------
home      = st.Page("pages/1_Home.py",            title="Home",             icon="🏠")
explore   = st.Page("pages/2_Explore.py",         title="Explore",          icon="🔍")
recs      = st.Page("pages/3_Recommendations.py", title="Recommendations",  icon="🎯")
session   = st.Page("pages/4_User_Session.py",    title="User Session",     icon="🧩")
analytics = st.Page("pages/5_Analytics.py",       title="Analytics",        icon="📊")
admin     = st.Page("pages/6_Admin.py",           title="Admin",            icon="🛠️")

# Role-based navigation
if st.session_state.role == "admin":
    st.navigation([home, explore, recs, session, analytics, admin]).run()

else:
    st.navigation([home, explore, recs, session, analytics]).run()
