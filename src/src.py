import sys
import os

# Get the directory containing src.py
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory to sys.path
sys.path.append(os.path.join(current_dir, '..'))
import streamlit as st
from app.login_page import check_login
from app.main import ColdMailGenerator

if "logged_in" not in st.session_state:
    st.session_state.logged_in= False

def login():
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    if check_login():
        st.session_state.logged_in = True
        st.rerun()

def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()

def coldEmail():
    if st.session_state.logged_in:
        pass
        # app=ColdMailGenerator()
        # app.run()

login_page = st.Page(login, title="Log in", icon=":material/login:",default=True)
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
dashboard = st.Page(
    coldEmail, title="Dashboard", icon=":material/mail:", default=True
)

if st.session_state.logged_in:
    pg = st.navigation(
            {
                "Account": [logout_page],
                "Reports": [dashboard],
                # "Tools": [search, history],
            }
        )
else:
    pg = st.navigation([login_page])



pg.run()

st.sidebar.text("Made With ❤ by Man")