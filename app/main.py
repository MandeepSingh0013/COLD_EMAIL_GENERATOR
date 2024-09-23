import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
import re

from chains import Chain
from portfolio import Portfolio
from utils import clean_text 



# Function to validate URL
def is_valid_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # or ip
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # or ipv6
        r'(?::\d+)?'  # port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

class ColdMailGenerator:
    def __init__(self):
        self.portfolio = Portfolio()
        self.chain = Chain()

    def run(self):
        self.create_streamlit_app()

    def create_streamlit_app(self):
        st.title("📧 Cold Mail Generator")
        
        # Initialize session state
        self.init_session_state()

        
        
        # Get user details: Full Name, Designation, Company Name
        st.header("User Details")
        st.session_state.full_name = st.text_input("Enter your full name:", placeholder="Mandeep Singh")
        st.session_state.designation = st.text_input("Enter your designation:", placeholder="AI Engineer")
        st.session_state.company_name = st.text_input("Enter your company name:", placeholder="MSpace")

        if not st.session_state.company_name or not st.session_state.designation or not st.session_state.company_name:
            st.warning("Please provide your full name, designation, and company name.")
        else:
            st.success("User details collected successfully!")

        col1, col2, col3 = st.columns(3)
        
        # Column 1: LLM Selection Radio Button
        with col1:
            self.select_llm()

        # Column 2: Language Selection
        with col2:
            self.select_language()

        # Column 3: Portfolio CSV Upload
        with col3:
            self.upload_portfolio_csv()

        # Job URL Input
        self.url_input()

        # Show Submit Button if both conditions are met
        if st.session_state.url_valid and st.session_state.status == "success":
            self.show_submit_button()
            


    def init_session_state(self):
        if 'email' not in st.session_state:
            st.session_state.email = ""
            # st.session_state.language_translate = True
        if 'status' not in st.session_state:
            st.session_state.status = ""
        if 'url_valid' not in st.session_state:
            st.session_state.url_valid = False
        
        if 'full_name' not in st.session_state:
            st.session_state.full_name=""
        if  'designation' not in st.session_state:
            st.session_state.designation=""
        if 'company_name' not in st.session_state:
            st.session_state.company_name=""
        

    def select_llm(self):
        st.subheader("Select LLM Model")
        self.model_choice=st.radio("Select the LLM model:", ("LLama", "Gemma", "Mixtral"), index=0)

    def select_language(self):
        st.subheader("Select Language")
        self.selected_language = st.radio("Choose the target language:", ("English", "French", "Spanish", "German"))

    def upload_portfolio_csv(self):
        st.subheader("Upload Portfolio CSV")
        st.write("Please upload a CSV with the following structure:")
        st.code('''"Techstack","Links"\n"React, Node.js, MongoDB","https://example.com/react-portfolio"\n...''')

        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file:
            try:
                st.session_state.status = self.portfolio.load_csv(uploaded_file)
                if st.session_state.status == "success":
                    st.success("CSV Uploaded and Validated Successfully!")
                else:
                    st.error("Invalid CSV format. Please ensure the file contains 'Techstack' and 'Links' columns.")
            except Exception as e:
                st.error(f"Error reading the CSV file: {e}")
        else:
            st.info("Please upload a CSV file to proceed.")

    def url_input(self):
        st.session_state.url_input = st.text_input("Enter a Job URL", placeholder="https://jobs.nike.com/job/R-37070?from=job%20search%20funnel")
        st.session_state.company_url = st.text_input("Enter Company 'About Us' URL", placeholder="https://example.com/about-us")
    
        if st.session_state.url_input and st.session_state.company_url :
            if is_valid_url(st.session_state.url_input) and is_valid_url(st.session_state.company_url):
                st.session_state.url_valid = True
                st.success("Valid URL")
            else:
                st.session_state.url_valid = False
                st.error("Invalid URL format. Please enter a valid URL.")
        else:
            st.session_state.url_valid = False
            st.warning("Please enter a job URL.")

    def show_submit_button(self):
        submit_button = st.button("Submit")
        if submit_button:
            self.process_submission()

    def process_submission(self):
        with st.spinner('Generating the cold email...'):
            try:
                loader = WebBaseLoader([st.session_state.url_input])  # Use the stored URL input value
                data = clean_text(loader.load().pop().page_content)
                self.portfolio.load_portfolio()
            
                jobs = self.chain.extract_jobs(self.model_choice, data)
                for job in jobs:
                    skills = job.get('skills', [])
                    links = self.portfolio.query_links(skills)
                    st.session_state.email = self.chain.write_mail_with_translation(self.model_choice, job, links, 
                                                                                    self.selected_language,st.session_state.full_name, st.session_state.designation, st.session_state.company_name)
                    st.subheader(f"Email Generated in ({self.selected_language}) by ({self.model_choice}) model")
                    st.code(st.session_state.email, language="markdown")
                    
            except Exception as e:
                st.error(f"An Error Occurred: {e}")

if __name__ == "__main__":
    app = ColdMailGenerator()
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    app.run()