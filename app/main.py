__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
import re
from .chains import Chain
from .portfolio import Portfolio
from .utils import clean_text , clean_portfolio_text
from .file_handler import FileHandler
import pandas as pd
from .email_file import EmailApp
import json
import os
import logging

# Set up logging
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.log')
logging.basicConfig(level=logging.INFO, filename=log_file_path, 
                    format='%(asctime)s:%(levelname)s:%(message)s')
# Load configuration
current_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(current_dir, 'config.json')

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
        self.file_handler = FileHandler()

    def run(self):

        """ Main method to run the Streamlit app """
        logging.info("Starting Cold Mail Generator application.")
        self.create_streamlit_app()

    def create_streamlit_app(self):
        st.title("📧 Cold Mail Generator")
        # Initialize session state
        self.init_session_state()
        # Capture user input details: Full Name, Designation, and Company Name
        self.get_user_details()
        col1, col2, col3 = st.columns(3)
        # Column 1: LLM Selection Radio Button
        with col1:
             self.temp_model_choice = self.select_llm()
        # Column 2: Language Selection
        with col2:
            self.temp_language_choice = self.select_language()
        # Column 3: Portfolio CSV Upload
        with col3:
            self.upload_portfolio_csv()
        self.about_us_input()
        # Job URL Input
        self.url_input()
        #Added Text Area
        self.add_instructions_input_box()
        col4,col5=st.columns(2)
        with col4:
            self.show_submit_button()
        with col5:
            self.show_cover_note_button()
        col6,col7=st.columns(2)
        with col6:
            self.display_generated_email()
        with col7:
            self.display_generated_cover_note()
        self.email_app()

    def init_session_state(self):
        st.session_state.setdefault("email","")
        st.session_state.setdefault("status","")
        st.session_state.setdefault("url_valid",False)
        st.session_state.setdefault("full_name","")
        st.session_state.setdefault("designation","")
        st.session_state.setdefault("company_name","")
        st.session_state.setdefault("generate_cover_note",False)
        st.session_state.setdefault('company_url',"")
        st.session_state.setdefault('cover_note',"")
        st.session_state.setdefault('company_url_valid',False)
        st.session_state.setdefault('model_choice', "")
        st.session_state.setdefault('selected_language', "")
        st.session_state.setdefault('cover_note_generated', False)
        st.session_state.setdefault('jobs','')
        st.session_state.setdefault('techstack_link','')
        st.session_state.setdefault("aboutus_url_valid",False)
        st.session_state.setdefault("special_instructions","")
        st.session_state.setdefault("feedback_portfolio","")
        st.session_state.setdefault("detailed_feedback","")
        st.session_state.setdefault("feedback",None)
    
    def get_user_details(self):
        # Get user details: Full Name, Designation, Company Name
        st.header("User Details")
        st.session_state.full_name = st.text_input("Enter Your Full Name:*", placeholder="Mandyy")
        st.session_state.designation = st.text_input("Enter Your Designation:*", placeholder="Bussiness Analyst")
        st.session_state.company_name = st.text_input("Enter Your company name:*", placeholder="MSpace")
        st.session_state.tone = st.selectbox("Select Tone:",("Professional","Formal","Friendly"))

        if not st.session_state.company_name or not st.session_state.designation or not st.session_state.company_name:
            st.warning("Please provide your full name, designation, and company name.")
        else:
            st.success("User details collected successfully!")
            logging.info("User details collected: %s, %s, %s", st.session_state.full_name, st.session_state.designation, st.session_state.company_name)

    def select_llm(self):
        """Allow user to select LLM model based on their role."""
        config=self.load_config()
        st.subheader("Select LLM Model")
        if config["USER_ROLE"]=="Researcher":
            return st.radio("Select the LLM model:", ("LLama", "Gemma", "Mixtral"), index=0)
        else:
            return st.radio("Select the LLM model:", ("LLama","Gemma"), index=0)
    
    def select_language(self):
        st.subheader("Select Language")
        # self.selected_language = st.radio("Choose the target language:", ("English", "French", "Spanish", "German"))
        return st.radio("Choose the target language:", ("English", "French", "Spanish", "German"))
    
    def upload_portfolio_csv(self):
        st.subheader("Upload Your Portfolio File")
        uploaded_file = st.file_uploader("Choose a file", type=["csv","pdf","docx","xlsx"])
        if uploaded_file:
            try:
                st.session_state.status, portfolio_data= self.file_handler.process_file(uploaded_file)
                if st.session_state.status == "success":
                    st.success("File Uploaded and Validated Successfully!")
                    with st.spinner("Processing the portfolio data..."):
                        cleaned_data=clean_portfolio_text(portfolio_data)
                        st.session_state.techstack_link=self.chain.extract_portfolio_data(self.temp_model_choice, cleaned_data)
                        df = pd.DataFrame(st.session_state.techstack_link)
                        # Load portfolio and extract jobs
                        self.portfolio.load_portfolio(df)
                        st.dataframe(df)
                    self.feedback_portfolio_icon(st.session_state.techstack_link, cleaned_data)
                else:
                    st.error("Invalid file format or content. Please check the file.")
                    logging.warning("File upload failed: Invalid format or content.")
            except Exception as e:
                logging.error("Error reading the file: %s", e)
                st.error(f"Error reading the file: {e}")
        else:
            st.info("Please upload a file to proceed.")
    
    # Load the config from the JSON file
    def load_config(self):
        try:
            with open(config_file_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            logging.error("Error loading config: %s", e)
            st.error(f"Error loading config: {e}")
            return {}


    def feedback_portfolio_icon(self, extracted_data, original_data):
        if 'submitted' not in st.session_state:
            st.session_state.submitted = False
        # Reset the form state after submission
        if st.session_state.submitted:
            st.session_state.detailed_feedback = ""
            st.session_state.feedback = None
            st.session_state.submitted = False
        # Create feedback section with thumbs-up or thumbs-down
        st.write("Is the extracted portfolio data accurate?")

         # Initialize session state for feedback if not present
        st.session_state.feedback = st.radio("Provide feedback:", ["👍", "👎"], index=0 if st.session_state.feedback is None else ["👍", "👎"].index(st.session_state.feedback))
        # Collect detailed feedback if thumbs-down is selected
        if st.session_state.feedback == "👎":
            st.warning("Please provide details on what is incorrect or missing:")
            st.session_state.detailed_feedback = st.text_area("Your Feedback", max_chars=250, value=st.session_state.detailed_feedback)
            self.button_feedback(extracted_data, original_data, "👎", st.session_state.detailed_feedback, False)
        
        elif st.session_state.feedback == "👍":
            self.button_feedback(extracted_data, original_data, "👍", "", False)
            

    
    def button_feedback(self, extracted_data, original_data, feedback, detailed_feedback, visibility):
        button_feedback = st.button("Submit Feedback", disabled=visibility)
        if button_feedback:
            # Only store feedback if detailed feedback is provided (in case of thumbs-down)
            if feedback == "👎" and detailed_feedback:
                # Persist feedback data (input data, feedback, user comments)
                self.portfolio.store_feedback(extracted_data, original_data, feedback, detailed_feedback)
                st.success("Thanks! We'll fine-tune the model.")
            elif feedback == "👍":
                # Store positive feedback without detailed comments
                self.portfolio.store_feedback(extracted_data, original_data, feedback, "")
                st.success("Thanks for the positive feedback!")
            st.session_state.submitted = True
            
        
    def add_instructions_input_box(self):
        st.subheader("Additional Instructions (Optional)")
        st.session_state.special_instructions = st.text_area("Provide any additional instructions what you are offering or key skills.",max_chars=250)

    def about_us_input(self):
        st.subheader("About URL Input")
        st.session_state.aboutus_url= st.text_input("Enter Your URL ", placeholder="Your About Us/Linkdin URL To Generate Cover Letter")#"https://www.infosys.com/about.html")
        if st.session_state.aboutus_url:
            if is_valid_url(st.session_state.aboutus_url):
                st.session_state.aboutus_url_valid=True
                st.success("Valid URL")
            else:
                st.session_state.aboutus_url_valid = False
                st.error("Invalid About US URL format. Please Enter A Valid URL.")
                logging.warning("Invalid 'About Us' URL format entered.")
        else:
           st.warning("Enter the 'About Us' URL if you want to add more information")
           logging.info("'About Us' URL is empty.")

    def url_input(self):
        st.subheader("Job URL Input")
        st.session_state.company_url = st.text_input("Enter A Job URL")#, placeholder="https://jobs.nike.com/job/R-37070?from=job%20search%20funnel")    
        if st.session_state.company_url and is_valid_url(st.session_state.company_url):
            st.session_state.company_url_valid = True
            st.success("URL is valid!")
            logging.info("Valid job URL provided.")
        else:
            st.session_state.company_url_valid = False
            if st.session_state.company_url:
                st.warning("Invalid URL format. Please enter a valid URL.")
                logging.warning("Invalid job URL format entered.")

    # def show_submit_button(self):
    #     submit_button = st.button("Generate Mail")
    #     if submit_button:
    #         if st.session_state.url_valid and st.session_state.full_name and st.session_state.designation and st.session_state.company_name:
    #             st.session_state.model_choice = self.temp_model_choice  # Save model choice only when clicked
    #             st.session_state.selected_language = self.temp_language_choice
    #             self.process_submission()
    #         else:
    #             st.error("Please Provide Company URL, Full Name, Designation and Company Name")
    def show_submit_button(self):
        if st.button("Generate Mail"):
            if all([st.session_state.company_url_valid, st.session_state.full_name, st.session_state.designation, st.session_state.company_name]):
                st.session_state.model_choice = self.temp_model_choice
                st.session_state.selected_language = self.temp_language_choice
                self.process_submission()
            else:
                st.error("Provide Company URL, Full Name, Designation, and Company Name.")
                logging.error("Missing required fields for email generation.")

    def show_cover_note_button(self):
        if st.button("Generate Cover Note"):
            self.process_cover_note_submission()
    #Generating Mail
    def process_submission(self):
        with st.spinner("Generating the cold email..."):
            try:
                # Load data using WebBaseLoader
                loader = WebBaseLoader([st.session_state.company_url])
                scraped_data = loader.load().pop() if loader else None
                
                # Check for page_content or fallback to description/title in metadata
                data = None
                if scraped_data:
                    data = clean_text(scraped_data.page_content) if hasattr(scraped_data, 'page_content') and scraped_data.page_content else None
                    if not data:
                        # Attempt to get data from metadata fields
                        metadata = scraped_data.metadata
                        data = metadata.get("description", "") or metadata.get("title", "")
                        
                    if data:
                        about_us_data = self.fetch_about_us_data()
                        about_us_data = self.chain.summarize_and_get_links(st.session_state.model_choice, about_us_data)
                        special_instructions = st.session_state.special_instructions or []

                        # Extract job data and generate email
                        st.session_state.jobs = self.chain.extract_jobs(st.session_state.model_choice, data)
                        for job in st.session_state.jobs:
                            skills = job.get('skills', [])
                            links = self.portfolio.query_links(skills)
                            st.session_state.email = self.chain.write_mail_with_translation(
                                st.session_state.model_choice, job, links, st.session_state.selected_language,
                                st.session_state.full_name, st.session_state.designation, st.session_state.company_name,
                                about_us_data, special_instructions, st.session_state.tone
                            )
                            st.session_state.email_generated = True
                            logging.info("Email generated successfully for job.")
                    else:
                        st.error("No relevant content found in the scraped data.")
                        logging.warning("Scraped data is empty or does not contain relevant content.")
                else:
                    st.error("Failed to load data. Try another URL.")
                    logging.warning("Data loader returned empty content.")
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")
                logging.error(f"Error during email generation: {e}")
        
    def fetch_about_us_data(self):
        """Fetches and returns the About Us data if a valid URL is provided."""
        if st.session_state.aboutus_url_valid:
            loader_about_us = WebBaseLoader([st.session_state.aboutus_url])
            return clean_text(loader_about_us.load().pop().page_content)
        return [] 
    
    
    def display_generated_email(self):
        """Display the generated email if it exists in session state."""
        if st.session_state.get("email_generated", False):
            st.subheader(f"Generated Cold Email ({st.session_state.model_choice}, {st.session_state.selected_language}):")
            st.code(st.session_state.email, language="markdown")
    
    def process_cover_note_submission(self):
        config = self.load_config()
        user_role = config.get("USER_ROLE")

        if user_role == "Individual (Job Search/Freelance)" and not (st.session_state.aboutus_url_valid or st.session_state.special_instructions):
            st.error("Provide a valid 'About You' URL or Instruction Text.")
            logging.error("Missing 'About You' URL or instruction text for individual user.")
            return

        if user_role != "Individual (Job Search/Freelance)" and not st.session_state.aboutus_url_valid:
            st.error("Provide a valid URL for the 'About Us' section.")
            logging.error("Missing 'About Us' URL for non-individual user.")
            return

        if not (st.session_state.full_name and st.session_state.designation):
            st.error("Provide your full name and designation.")
            logging.error("Missing full name or designation.")
            return

        with st.spinner("Generating the cover note..."):
            try:
                about_us_data = self.fetch_about_us_data() + st.session_state.special_instructions
                about_us_data = self.chain.summarize_and_get_links(st.session_state.model_choice,about_us_data)

                if st.session_state.jobs:
                    for job in st.session_state.jobs:
                        st.session_state.cover_note = self.chain.write_cover_note(
                            self.temp_model_choice, st.session_state.full_name, st.session_state.designation,
                            st.session_state.company_name, about_us_data, self.temp_language_choice, st.session_state.tone, job
                        )
                else:
                    st.session_state.cover_note = self.chain.write_cover_note(
                        self.temp_model_choice, st.session_state.full_name, st.session_state.designation,
                        st.session_state.company_name, about_us_data, self.temp_language_choice, st.session_state.tone
                    )
                st.session_state.cover_note_generated = True
                logging.info("Cover note generated successfully.")

            except Exception as e:
                st.error(f"An error occurred: {e}")
                logging.error(f"Error during cover note generation: {e}")


    def display_generated_cover_note(self):
        # """Display the generated cover note if it exists in session state."""
        if st.session_state.get("cover_note_generated", False):
            st.subheader(f"Generated Cover Note ")#({st.session_state.model_choice}, {st.session_state.selected_language}):")
            with st.expander("Cover Note"):
                st.write(st.session_state.cover_note)

    def email_app(self):
        email = EmailApp()
        email.display_form()



if __name__ == "__main__":
    app = ColdMailGenerator()
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    app.run()