__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
import re

from chains import Chain
from portfolio import Portfolio
from utils import clean_text , clean_portfolio_text
from file_handler import FileHandler
import pandas as pd


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

        self.add_instructions_input_box()
        
        # self.cover_note_option()
        self.about_us_input()
        
        # Job URL Input
        self.url_input()

        col4,col5=st.columns(2)
        # Show Submit Button if both conditions are met
        if st.session_state.url_valid and st.session_state.full_name and st.session_state.designation and st.session_state.company_name:#and st.session_state.status == "success" and st.session_state.full_name and st.session_state.designation:
            with col4:
                self.show_submit_button()
            with col5:
                self.show_cover_note_button()
               
        col6,col7=st.columns(2)
        with col6:
            self.display_generated_email()
        with col7:
            self.display_generated_cover_note()
         
        #Show Generate cover note button 
        # if st.session_state.generate_cover_note and st.session_state.company_url_valid:
            # self.show_cover_note_button()
       
    
        
        
      
    def get_user_details(self):
        # Get user details: Full Name, Designation, Company Name
        st.header("User Details")
        st.session_state.full_name = st.text_input("Enter your full name:", placeholder="Mandeep Singh")
        st.session_state.designation = st.text_input("Enter your designation:", placeholder="AI Engineer")
        st.session_state.company_name = st.text_input("Enter your company name:", placeholder="MSpace")

        if not st.session_state.company_name or not st.session_state.designation or not st.session_state.company_name:
            st.warning("Please provide your full name, designation, and company name.")
        else:
            st.success("User details collected successfully!")

    def init_session_state(self):
        if 'email' not in st.session_state:
            st.session_state.email = ""
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
        if 'generate_cover_note' not in st.session_state:
            st.session_state.generate_cover_note = False
        if 'company_url' not in st.session_state:
            st.session_state.company_url = ""
        if 'cover_note' not in st.session_state:
            st.session_state.cover_note = ""
        if "company_url_valid" not in st.session_state:
            st.session_state.company_url_valid=False
        # if "email_generated" not in st.session_state:
            # st.session_state.email_generated=False
        st.session_state.setdefault('model_choice', "")
        st.session_state.setdefault('selected_language', "")
        st.session_state.setdefault('cover_note_generated', False)
        st.session_state.setdefault('jobs','')
        st.session_state.setdefault('techstack_link','')
        st.session_state.setdefault("aboutus_url_valid",False)
        st.session_state.setdefault("special_instructions","")
    
    def select_llm(self):
        st.subheader("Select LLM Model")
        # self.model_choice=st.radio("Select the LLM model:", ("LLama", "Gemma", "Mixtral"), index=0)
        return st.radio("Select the LLM model:", ("LLama", "Gemma", "Mixtral"), index=0)

    def select_language(self):
        st.subheader("Select Language")
        # self.selected_language = st.radio("Choose the target language:", ("English", "French", "Spanish", "German"))
        return st.radio("Choose the target language:", ("English", "French", "Spanish", "German"))

    def upload_portfolio_csv(self):
        st.subheader("Upload Portfolio File")
        uploaded_file = st.file_uploader("Choose a file", type=["csv","pdf","docx","xlsx"])
        if uploaded_file:
            try:
                # st.session_state.status= self.portfolio.load_csv(uploaded_file)
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


                else:
                    st.error("Invalid file format or content. Please check the file.")
            except Exception as e:
                st.error(f"Error reading the CSV file: {e}")
        else:
            st.info("Please upload a CSV file to proceed.")

    def add_instructions_input_box(self):
        st.session_state.special_instructions = st.text_area("Enter any special instructions or notes (optional)")

    def about_us_input(self):
        st.session_state.aboutus_url= st.text_input("Enter About Us URL", placeholder="https://www.infosys.com/about.html")
        if st.session_state.aboutus_url:
            if is_valid_url(st.session_state.aboutus_url):
                st.session_state.aboutus_url_valid=True
                st.success("Valid URL")
            else:
                st.session_state.aboutus_url_valid = False
                st.error("Invalid About US URL format. Please enter a valid URL.")
        else:
           st.warning("Enter the 'About Us' URL if you want to add more information")

    def url_input(self):
        st.session_state.url_input = st.text_input("Enter A Job URL", placeholder="https://jobs.nike.com/job/R-37070?from=job%20search%20funnel")
    
        if st.session_state.url_input:
            if is_valid_url(st.session_state.url_input):
                st.session_state.url_valid = True
                st.success("Valid URL")
                
            else:
                st.session_state.url_valid = False
                st.error("Invalid Target Job URL format.")
        else:
            st.session_state.url_valid = False
            st.warning("Please enter a job URL.")

    # def cover_note_option(self):
    #     # """Allow user to opt for generating a cover note and provide company 'About Us' URL."""
    #     # st.subheader("Cover Note Option")
    #     # st.session_state.generate_cover_note = st.checkbox("Generate Cover Note")
        
    #     # if st.session_state.generate_cover_note:
    #         # st.session_state.company_url = st.text_input("Enter Company 'About Us' URL", placeholder="https://example.com/about-us")
    #         if st.session_state.company_url:
    #             if is_valid_url(st.session_state.company_url):
    #                 st.session_state.company_url_valid = True
    #                 st.success("Valid Company URL")
    #             else:
    #                 st.error("Invalid 'About Us' URL format.")
    #         else:
    #             st.warning("Please enter the 'About Us' URL if you want to generate a cover note.")

    def show_submit_button(self):
        submit_button = st.button("Generate Mail")
        if submit_button:
            st.session_state.model_choice = self.temp_model_choice  # Save model choice only when clicked
            st.session_state.selected_language = self.temp_language_choice
            self.process_submission()

    def show_cover_note_button(self):
        if st.button("Generate Cover Note"):
        # if st.session_state.generate_cover_note and st.button("Generate Cover Note") and st.session_state.company_url_valid :
            self.process_cover_note_submission()

    def process_submission(self):
        with st.spinner('Generating the cold email...'):
            try:
                loader = WebBaseLoader([st.session_state.url_input])  # Use the stored URL input value
                data = clean_text(loader.load().pop().page_content)
                if st.session_state.aboutus_url_valid:
                    about_us_loader = WebBaseLoader([st.session_state.aboutus_url])  # Use the stored URL input value
                    about_us_data = clean_text(about_us_loader.load().pop().page_content)
                    about_us_data = self.chain.summarize_and_get_links(st.session_state.model_choice,about_us_data)
                    
                else: 
                    about_us_data=[]
                special_instuction =  st.session_state.special_instructions if st.session_state.special_instructions else []
                # # Load portfolio and extract jobs
                # self.portfolio.load_portfolio()
                # Generate email for each job extracted
                st.session_state.jobs = self.chain.extract_jobs(st.session_state.model_choice, data)
                for job in st.session_state.jobs:
                    skills = job.get('skills', [])
                    
                    links = self.portfolio.query_links(skills) if st.session_state.status == "success" else []
                    st.session_state.email = self.chain.write_mail_with_translation(st.session_state.model_choice, job, links, 
                                                                                    st.session_state.selected_language,st.session_state.full_name, 
                                                                                    st.session_state.designation, st.session_state.company_name,about_us_data,special_instuction)
                    st.session_state.email_generated = True
                   
            except Exception as e:
                st.error(f"An Error Occurred: {e}")
       
    def display_generated_email(self):
        """Display the generated email if it exists in session state."""
        if st.session_state.get("email_generated", False):
            st.subheader(f"Generated Cold Email ({st.session_state.model_choice}, {st.session_state.selected_language}):")
            st.code(st.session_state.email, language="markdown")

    def process_cover_note_submission(self):
        """Process the cover note submission."""
        if st.session_state.aboutus_url_valid:
            with st.spinner('Generating the cover note...'):
                try:
                    # Load the 'About Us' page content from the provided URL
                    loader_about_us = WebBaseLoader([st.session_state.aboutus_url])
                    about_us_data = clean_text(loader_about_us.load().pop().page_content)
                    for job in st.session_state.jobs:
                        # Generate the cover note aligned with the job description
                        st.session_state.cover_note = self.chain.write_cover_note(
                            self.temp_model_choice, #st.session_state.model_choice,
                            st.session_state.full_name, 
                            st.session_state.designation, 
                            st.session_state.company_name,
                            about_us_data,
                            job,
                            self.temp_language_choice#st.session_state.selected_language

                        )
                        st.session_state.cover_note_generated = True    
                except Exception as e:
                    st.error(f"An Error Occurred: {e}")
        else:
            st.error("Enter About Us URL")

    def display_generated_cover_note(self):
        # """Display the generated cover note if it exists in session state."""
        if st.session_state.get("cover_note_generated", False):
            st.subheader(f"Generated Cover Note ({st.session_state.model_choice}, {st.session_state.selected_language}):")
            with st.expander("Cover Note"):
                st.write(st.session_state.cover_note)

if __name__ == "__main__":
    app = ColdMailGenerator()
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    app.run()