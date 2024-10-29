import streamlit as st
import pyrebase
import webbrowser
import logging
import re
import os
import time
import requests
import json
from dotenv import load_dotenv
# Initialize logging
logging.basicConfig(filename="app.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
load_dotenv()
# Firebase configuration
firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
}
# Initialize Firebase
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()

# Session timeout configuration (e.g., 30 minutes)
SESSION_TIMEOUT = 30 * 60  # 30 minutes in seconds

# Password strength validation
def is_password_strong(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

# Authentication class for handling user authentication
class Authentication:
    def __init__(self):
        self.user = None

    def login(self):
        """Display the login form and handle email/password authentication."""
        st.title("Login to Cold Email Generator 📧")
        login_method = st.selectbox("Choose Login Method", ["Email/Password"])  # Expandable for future OAuth options

        if login_method == "Email/Password":
            email = st.text_input("Enter Email")
            password = st.text_input("Enter Password", type="password")
            
            if st.button("Login"):
                try:
                    self.user = auth.sign_in_with_email_and_password(email, password)
                    st.session_state['user'] = self.user
                    # st.session_state['token'] = self.user['idToken']
                    st.session_state['logged_in'] = True
                    st.session_state['session_start'] = time.time()  # Track session start time
                    st.success(f"User {email} logged in successfully.")
                    logging.info(f"User {email} logged in successfully.")
                    
                except requests.exceptions.HTTPError as http_err:
                    # Check if there is a response attached to the exception
                    if http_err.response is not None:
                        error_message = http_err.response.json().get("error", {}).get("message", "")
                    else:
                        error_message = "No response received from the server."

                    # Display appropriate error message based on error content
                    if "EMAIL_NOT_FOUND" in error_message:
                        st.error("Email not found. Please sign up first.")
                    elif "INVALID_PASSWORD" in error_message:
                        st.error("Incorrect password. Please try again.")
                    elif "USER_DISABLED" in error_message:
                        st.error("Account disabled. Contact support.")
                    else:
                        st.error("Login failed. Please try again.")

                    # Log the error for troubleshooting
                    logging.error(f"Login failed for {email}: {error_message}")
        
        elif login_method == "Google":
            self.google_login()

    def google_login(self):
        """Initiate Google OAuth login (to be implemented in deployment)."""
        st.write("Google OAuth Login initiated...")
        auth_url = f"https://coldmailgenerator.firebaseapp.com/__/auth/handler"
        webbrowser.open(auth_url)
        st.write("Redirecting to Google OAuth...")

    def sign_up(self):
        """Display the sign-up form and create a new user."""
        st.title("Sign up for Cold Email Generator")
        email = st.text_input("Enter Email for Signup")
        password = st.text_input("Enter Password for Signup", type="password")
        
        if st.button("Sign Up"):
            if is_password_strong(password):
                try:
                    auth.create_user_with_email_and_password(email, password)
                    st.success("Account created successfully! Please login.")
                    logging.info(f"New user account created: {email}")
                except Exception as e:
                    st.error("Error creating account. Please try a different email.")
                    logging.error(f"Sign-up failed for {email}: {str(e)}")
            else:
                st.warning("Password must be at least 8 characters and include numbers and special characters.")

    def is_logged_in(self):
        """Check if a user is currently logged in and manage session timeout."""
        if st.session_state.get('logged_in', False):
            # Check for session timeout
            if time.time() - st.session_state.get('session_start', 0) > SESSION_TIMEOUT:
                st.warning("Session timed out. Please log in again.")
                st.session_state['logged_in'] = False
                st.session_state['user'] = None
                st.session_state['token'] = None  # Clear token
                st.session_state['session_start'] = None
                logging.info("Session timed out.")
                st.rerun()
            return True
        return False

# Main function to manage login state
def check_login():
    st.sidebar.title("Cold Email Generator 📧")
    
    # Initialize session state for login
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['user'] = None
        st.session_state['session_start'] = None

    auth_instance = Authentication()
    user_action = st.sidebar.radio("Menu", ["Login", "Sign Up"])

    if user_action == "Login":
        auth_instance.login()
    elif user_action == "Sign Up":
        auth_instance.sign_up()

    # # Display logout button if logged in
    # if st.session_state['logged_in']:
    #     if st.sidebar.button("Logout"):
    #         st.session_state['logged_in'] = False
    #         st.session_state['user'] = None
    #         st.session_state['token'] = None
    #         st.session_state['session_start'] = None
    #         st.sidebar.success("Logged out successfully.")
    #         logging.info("User logged out.")
    #         st.rerun()

    # Return True if logged in, otherwise None
    return auth_instance.is_logged_in()

if __name__ == "__main__":
    check_login()