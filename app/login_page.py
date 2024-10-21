import streamlit as st
import pyrebase

# Firebase configuration
firebase_config = {
    "apiKey": "AIzaSyDdSxH3qIrd9mGQy1CTKRrVQhXm5HKeJQM",
    "authDomain": "coldmailgenerator.firebaseapp.com",
    "projectId": "coldmailgenerator",
    "storageBucket": "coldmailgenerator.appspot.com",
    "messagingSenderId": "907661725680",
    "appId": "1:907661725680:web:88b2d2f24bbc733b1cd735",
    "databaseURL": "https://coldmailgenerator-default-rtdb.firebaseio.com"
}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()

# Authentication class
class Authentication:
    def __init__(self):
        self.user = None

    def login(self):
        """Login form for users"""
        st.title("Login to Cold Email Generator")
        login_option = st.selectbox("Login Method", ("Email/Password", "Google", "Facebook", "Microsoft"))

        if login_option == "Email/Password":
            email = st.text_input("Enter Email")
            password = st.text_input("Enter Password", type="password")
            
            if st.button("Login"):
                try:
                    self.user = auth.sign_in_with_email_and_password(email, password)
                    st.session_state['user'] = self.user
                    st.session_state['logged_in'] = True
                    st.success(f"Welcome, {email}!")
                    
                except Exception as e:
                    st.error(f"Error: {e}")
                    
        elif login_option in ["Google", "Facebook", "Microsoft"]:
            st.write(f"{login_option} login is only available on deployment (OAuth).")

    def sign_up(self):
        """Sign up form for new users"""
        st.title("Sign up for Cold Email Generator")
        email = st.text_input("Enter Email for Signup")
        password = st.text_input("Enter Password for Signup", type="password")
        
        if st.button("Sign Up"):
            try:
                auth.create_user_with_email_and_password(email, password)
                st.success("User created successfully! Please login.")
            except Exception as e:
                st.error(f"Error: {e}")

    def logout(self):
        """Logout the current user"""
        st.session_state['logged_in'] = False
        st.session_state['user'] = None
        st.sidebar.info("Logged out successfully.")
    
    def is_logged_in(self):
        """Check if a user is logged in"""
        return st.session_state.get('logged_in', False)

# Cold Email Generator App class
class ColdEmailGeneratorApp:
    def __init__(self, user):
        self.user = user

    def show_user_options(self):
        """Show options based on user type (Company, Individual, Research)"""
        st.title("Welcome to Cold Email Generator")
        st.subheader("Choose your user type")
        
        user_type = st.radio("I am...", ["Company Representative", "Individual (Job search/Freelance)", "Researcher"])

        if user_type == "Company Representative":
            st.write("You are approaching another company for business opportunities.")
            # Add business cold email generation features here

        elif user_type == "Individual (Job search/Freelance)":
            st.write("You are searching for a job or freelance opportunities.")
            # Add job search cold email generation features here

        elif user_type == "Researcher":
            st.write("You are contacting for research purposes.")
            # Add research cold email generation features here

    def store_user_info(self, user_type):
        """Store user information in the Firebase database"""
        user_data = {
            "email": self.user['email'],
            "user_type": user_type,
            "uid": self.user['localId']
        }
        db.child("users").child(self.user['localId']).set(user_data)

# Main function
def check_login():
    st.sidebar.title("Cold Email Generator")
    
    # Initialize session state variables for login
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['user'] = None

    # Initialize Authentication
    auth_instance = Authentication()

    # Show login or signup forms
    # if st.session_state['logged_in']:
    #     if st.sidebar.button("Logout"):
    #         auth_instance.logout()

    # else:
    user_choice = st.sidebar.radio("Menu", ["Login", "Sign up"])

    if user_choice == "Login":
        auth_instance.login()
    elif user_choice == "Sign up":
        auth_instance.sign_up()

    # # If logged in, show the main app
    if auth_instance.is_logged_in():
        return True
        # cold_email_app = ColdEmailGeneratorApp(st.session_state['user'])
        # cold_email_app.show_user_options()

# if __name__ == "__main__":
#     check_login()
