import sys
import os
import json
import logging
import streamlit as st
current_dir = os.path.dirname(os.path.abspath(__file__))
# # Add the parent directory to sys.path
sys.path.append(os.path.join(current_dir, '..'))
from app.login_page import check_login
from app.main import ColdMailGenerator
from app.email_file import EmailApp
from app.form import contact_form
# Logging setup
logging.basicConfig(
    filename='email_generator_app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configure Streamlit page
st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")

# Constants
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'app', 'config.json')
LOGGED_IN = "logged_in"
USER_TYPE = "user_type"
USER_ROLE_KEY = "USER_ROLE"

class EmailGeneratorApp:
    def __init__(self):
        # Initialize session state variables with defaults
        st.session_state.setdefault(LOGGED_IN, False)
        st.session_state.setdefault(USER_TYPE, None)
        
        # Load configuration once
        self.config = self.load_config()
        # Navigation based on login status
        if st.session_state[LOGGED_IN]:
            self.show_navigation(logged_in=True)
            self.display_user_type_selection()
        else:
            self.show_navigation(logged_in=False)

    def show_navigation(self, logged_in):
        """Displays navigation based on login status."""
        if logged_in:
            about_page = st.Page(self.about_me,title="About Me",icon=":material/account_circle:")
            logout_page = st.Page(self.show_logout_page, title="Log out", icon=":material/logout:")
            dashboard_page = st.Page(self.show_dashboard, title="Dashboard", icon=":material/mail:",default=True)
            email_page = st.Page(self.email_app, title="Email", icon=":material/send:")
            
            st.navigation({"About Me":[about_page], "Dashboard": [dashboard_page],"Send Mail":[email_page],"Account": [logout_page]}).run()
        else:
            login_page = st.Page(self.show_login_page, title="Log in", icon=":material/login:", default=True)
            st.navigation([login_page]).run()
    
    @st.dialog("Contact Me")
    def show_contact_form(self):
        contact_form()
    
    def about_me(self):
        col1, col2 = st.columns(2,gap="small",vertical_alignment="center")
        with col1:
           st.image("src/assets/profile_image.jpg",width=400)
        with col2:
           st.title("Mandyy",anchor=False)
           st.write(
               """Data Scientist, assisting enterprises by supporting data-driven decision-making.
               https://www.linkedin.com/in/mandeeepsingh/"""
           )
           if st.button("💌 Contact Me"):
               self.show_contact_form()
        st.write("\n")
        st.subheader("Experience & Qualifications", anchor=False)

        st.write("""        
        - 4+ years of experience in developing and deploying NLP and GenAI solutions
        - Proficient in advanced Python programming, including TensorFlow, PyTorch, and SQL for data engineering and analysis
        - Deep understanding of NLP, LLMs, and model deployment on cloud platforms (AWS, Azure)
        - Strong knowledge in MLOps, including CI/CD, Docker, and Kubernetes for scalable deployments
        - Excellent team collaborator with a proactive approach to solving complex AI challenges
        """)

        # SKILLS
        st.write("\n")
        st.subheader("Core Technical Skills", anchor=False)
        st.write(
        """
        - **Programming**: Python (Scikit-learn, TensorFlow, PyTorch, Pandas), SQL, R
        - **Generative AI**: NLP, LLMs (GPT-4, BERT, Claude, Llama, Gemini)
        - **Data Engineering**: ETL pipelines, data wrangling, data cleaning, real-time/batch data processing
        - **Data Visualization**: Power BI, Tableau, Plotly, Matplotlib
        - **Modeling Techniques**: Neural networks, transformers, logistic regression, clustering
        - **Databases**: MS SQL Server, Postgres, MongoDB
        - **Deployment**: MLOps (CI/CD), Docker, Kubernetes, cloud deployment on AWS and Azure
        """
        )



    def display_user_type_selection(self):
        """Allows user type selection and updates configuration accordingly."""
        try:
            previous_user_type = st.session_state[USER_TYPE]
            user_type = st.sidebar.radio(
                "I am a...",
                options=["Company Representative", "Individual (Job Search/Freelance)"]
            )

            if user_type != previous_user_type:
                st.session_state[USER_TYPE] = user_type
                self.update_config(USER_ROLE_KEY, user_type)
                st.rerun()

            st.sidebar.text("Made With ❤ by Man")
        except Exception as e:
            st.error("An error occurred while selecting user type.")
            logging.error("Error in userType function: %s", e)

    def show_login_page(self):
        """Displays the login page and updates login status upon successful login."""
        try:
            if check_login():
                st.session_state[LOGGED_IN] = True
                st.rerun()
        except Exception as e:
            st.error("Login failed. Please try again.")
            logging.error("Error in login function: %s", e)

    def show_logout_page(self):
        """Logs the user out and clears session data."""
        if st.button("Log out"):
            st.session_state[LOGGED_IN] = False
            st.session_state[USER_TYPE] = None
            st.success("Logged out successfully.")
            logging.info("User logged out.")
            st.rerun()

    def show_dashboard(self):
        """Displays the dashboard where ColdMailGenerator can be accessed."""
        if st.session_state[LOGGED_IN]:
            try:
                app = ColdMailGenerator()
                app.run()
            except Exception as e:
                st.error("An error occurred while loading the Cold Email Generator.")
                logging.error("Error in coldEmail function: %s", e)
    
    def email_app(self):
        email = EmailApp()
        email.display_form()

    def load_config(self):
        """Loads configuration from JSON file, handling errors gracefully."""
        try:
            with open(CONFIG_PATH, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            st.error("Configuration file not found.")
            logging.error("Configuration file not found.")
            return {}
        except json.JSONDecodeError:
            st.error("Error decoding configuration file.")
            logging.error("Error decoding configuration file.")
            return {}

    def save_config(self):
        """Saves current configuration to JSON file."""
        try:
            with open(CONFIG_PATH, 'w') as file:
                json.dump(self.config, file, indent=4)
            logging.info("Configuration updated.")
        except Exception as e:
            st.error("Failed to save configuration.")
            logging.error("Error in save_config function: %s", e)

    def update_config(self, key, value):
        """Updates a specific configuration key in memory and saves it."""
        self.config[key] = value
        self.save_config()

if __name__ == "__main__":
    try:
        logging.info("Starting EmailGeneratorApp.")
        app = EmailGeneratorApp()
    except Exception as e:
        st.error("Failed to start the application.",e)
        logging.critical("Critical error on start: %s", e)