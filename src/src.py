import sys
import os
import json
# Get the directory containing src.py
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add the parent directory to sys.path
sys.path.append(os.path.join(current_dir, '..'))
# Path to your config file
# config_file_path = os.path.join(os.path.dirname(__file__), './app/config.json')

import streamlit as st
from app.login_page import check_login
from app.main import ColdMailGenerator

current_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(current_dir, '..', 'app', 'config.json')

st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")

class EmailGeneratorApp:

    def __init__(self):
        

        if "logged_in" not in st.session_state:
            st.session_state.logged_in = False

        if "user_type" not in st.session_state:
            st.session_state.user_type = None
        
        # Define the login, logout, and dashboard pages
        login_page = st.Page(self.login, title="Log in", icon=":material/login:", default=True)
        logout_page = st.Page(self.logout, title="Log out", icon=":material/logout:")
        dashboard = st.Page(self.coldEmail, title="Dashboard", icon=":material/mail:", default=True)
        # Manage navigation based on login status
        if st.session_state.logged_in:
            
            pg = st.navigation(
                    {
                        "Account": [logout_page],
                        "Dashboard": [dashboard],
                        
                    }
                )
            self.userType()
            
        else:
            pg = st.navigation([login_page])

        
        pg.run()

        
    def userType(self):
        # Store the previous user type to detect changes
        prev_user_type = st.session_state.user_type

        user_type = st.sidebar.radio(
            "I am a...",
            options=["Company Representative", "Individual (Job Search/Freelance)"]#, "Researcher"]
        )
        # If the user type has changed, update and rerun the app
        if user_type != prev_user_type:
            st.session_state.user_type = user_type
            self.update_config("USER_ROLE", user_type)
            st.rerun()  # Rerun the app to reflect changes

        # Save the user type in the session state
        # st.session_state.user_type = user_type
        st.sidebar.text("Made With ❤ by Man")
        self.update_config("USER_ROLE",user_type)
       

    def login(self):
        user = check_login()  # Check login credentials
        if user:
            st.session_state.logged_in = True
            st.rerun()
    
    def logout(self):
        if st.button("Log out"):
            st.session_state.logged_in = False
            st.session_state.user_type = None  # Clear user type on logout
            st.rerun()

    def coldEmail(self):
        if st.session_state.logged_in:
            app = ColdMailGenerator()#user_type=st.session_state.user_type)  # Pass user_type to the app
            app.run()
    
    # Load the config from the JSON file
    def load_config(self):
        with open(config_file_path, 'r') as file:
            return json.load(file)

    # Save the updated config back to the JSON file
    def save_config(self,config):
        with open(config_file_path, 'w') as file:
            json.dump(config, file, indent=4)

    # Function to update a specific config value (like USER_ROLE)
    def update_config(self,key, value):
        config = self.load_config()
        config[key] = value
        self.save_config(config)
        

if __name__=="__main__":
    mail=EmailGeneratorApp()
    

