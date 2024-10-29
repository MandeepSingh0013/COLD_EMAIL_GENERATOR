from langchain_groq import ChatGroq # To Call model from Groq platform
from langchain_core.prompts import PromptTemplate # To make prompt
from langchain_core.output_parsers import JsonOutputParser #To pass the Json data
from langchain_core.exceptions import OutputParserException # 
from dotenv import load_dotenv #Load Environment veriable
import os #Load the data from system
import time
import logging
import re
import json
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


# Path to the current directory and the config file
current_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(current_dir,'config.json')
load_dotenv()

# Set up logging
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.log')
logging.basicConfig(level=logging.INFO, filename=log_file_path, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

class Chain:
    #Invoking LLAma model from GROQ
    def __init__(self):
        self.llm_llama = ChatGroq(
        model="llama-3.1-70b-versatile",
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2
        )

        self.llm_gemma = ChatGroq(
            model="gemma2-9b-it", 
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2
        )
        self.llm_Mixtral = ChatGroq(
            model="mixtral-8x7b-32768", 
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2
        )
    # Load the config from the JSON file
    def load_config(self):
        with open(config_file_path, 'r') as file:
            return json.load(file)
        
    # Select which model to use
    def get_model(self, model_name):
        if model_name == "LLama":
            return self.llm_llama
        elif model_name == "Gemma":
            return self.llm_gemma
        elif model_name == "Mixtral":
            return self.llm_Mixtral
        else:
            raise ValueError("Unknown model name")

    #Extracting JD in JSON form using LLM
    def extract_jobs(self,model_name,cleaned_text):
        llm = self.get_model(model_name)
        prompt_extract= PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of website.
            your job is to extract the job posting and return them in JSON format containing the following keys:`role`, `experience`, `skills` and `description`.
            only return the valid JSON
            ### VALID JSON (NO PREAMBLE):
            """)
        
        chain_extract = prompt_extract | llm
        res=  chain_extract.invoke(input={"page_data":cleaned_text})

        try:
            json_parser = JsonOutputParser()
            res= json_parser.parse(res.content)
        except OutputParserException as e:
            logging.error(f"Job extraction error: {e}")
            raise OutputParserException("Job extraction failed. The context may be too large. Please try a smaller input.")
        return res if isinstance(res,list) else [res]
    
    
    @retry(
        stop=stop_after_attempt(5),  # Retry up to 5 times
        wait=wait_exponential(multiplier=0.1, min=0.2, max=60),  # Exponential backoff starting at 200ms
        retry=retry_if_exception_type(Exception)  # Retry only on rate limit error (429)
    )
    def write_cover_note(self, model_name, full_name, designation, company_name, about_us_text,target_language,tone,job=None):
        llm = self.get_model(model_name)  # Get the LLM based on the selection
        cover_note_prompt=self.load_config()
        if cover_note_prompt["USER_ROLE"]=="Company Representative":
            cover_note_prompt=cover_note_prompt["users"]["user1"]["cover_note_prompt"]
        else: 
            cover_note_prompt=cover_note_prompt["users"]["user2"]["cover_note_prompt"]
        
        # Prepare the job description section if provided
        # Prepare the job description section if provided
        
        if job:
            job_role = job.get("role", "")
            job_experience = job.get("experience", "")
            job_skills = ", ".join(job.get("skills", []))
            job_description = job.get("description", "")
            
            job = f"""
            ### JOB ROLE:
            {job_role}

            ### REQUIRED EXPERIENCE:
            {job_experience}

            ### REQUIRED SKILLS:
            {job_skills}

            ### JOB DESCRIPTION:
            {job_description}
            """
        
        # Prompt template for generating the cover note
        prompt_cover_note = PromptTemplate.from_template(
        cover_note_prompt)

        try:
            # Invoke the LLM with both job and language context
            chain_cover_note = prompt_cover_note | llm
            # Invoke the chain with the dynamic inputs
            res = chain_cover_note.invoke({
                "full_name": full_name,
                "designation": designation,
                "company_name": company_name,
                "about_us_text": about_us_text,
                "job_description_section": job,
                "target_language": target_language,
                "tone": tone
            
            })
            logging.info("Cover note generated successfully.")
            return res.content
        except Exception as e:
            logging.error(f"An error occurred while generating the cover note: {e}")
            return "An error occurred while generating the cover note. Please check your input or try again later."
    
    def extract_portfolio_data(self, model_name, cleaned_text):
        # Get the LLM model
        llm = self.get_model(model_name) 
            # Define the prompt for extracting tech stacks and links
        prompt_extract = PromptTemplate.from_template(
            """
            ### USER'S PORTFOLIO DATA:
            {portfolio_data}
            ### INSTRUCTION:
            The given data contains tech stacks and their respective portfolio links. Your task is to extract this information 
            and return it in a structured JSON format containing two keys: `techstack` and `links`. If a link is not available, return "N/A". 
            The portfolio could be from an individual or a company. It may be related to applying for a job or offering services. Ensure that your output is accurate and concise.

            Ensure the data is structured as an array of objects, where each object has the following keys:
            - "Techstack": A string representing the technologies used (e.g., React, Node.js, MongoDB).
            - `Links`: A valid URL showcasing the portfolio.

            Please ensure the output is a valid JSON without any additional text or commentary.

            ### VALID JSON FORMAT (NO PREAMBLE):
            
            """
        )
        # Chain the prompt with the LLM model
        chain_extract = prompt_extract | llm
        result = chain_extract.invoke(input={"portfolio_data": cleaned_text})
        # Parse the output to JSON format
        try:
            json_parser = JsonOutputParser()
            result = json_parser.parse(result.content)
            
        except OutputParserException as e:
            logging.error(f"Portfolio extraction failed. The input may be too large or improperly formatted. {e}")
            raise OutputParserException("Portfolio extraction failed. The input may be too large or improperly formatted.")
        return result if isinstance(result, list) else [result]

        
    
    def write_mail_with_translation(self, model_name, job, links, language, full_name, designation, company_name,tone, about_us=None, comments=None):
        llm = self.get_model(model_name)  # Get the LLM based on the model name
        mail_prompt=self.load_config()
        # Define the base company description
        company_description = f"{company_name} is a consulting company specializing in providing services tailored to meet the needs of various industries."
        
        # If 'About Us' data is available, include it in the description
        if about_us:
            company_description += f" {about_us}"
        
        # If additional comments are provided, include them as well
        if comments:
            company_description += f" {comments}"
        if mail_prompt["USER_ROLE"]=="Company Representative":
            mail_prompt=mail_prompt["users"]["user1"]["mail_prompt"]
        else: 
            mail_prompt=mail_prompt["users"]["user2"]["mail_prompt"]

        # Unified prompt that generates the email and optionally translates it
        prompt_email_translate = PromptTemplate.from_template(
            mail_prompt)

        try:
            # Invoke the LLM with both job and language context
            chain_email_translate = prompt_email_translate | llm

            # Invoke the chain with the dynamic inputs
            res = chain_email_translate.invoke({
                "job_description": str(job),
                "company_description": company_description,
                "link_list": links if links else "No links provided.",
                "target_language": language,
                "full_name": full_name,
                "designation": designation,
                "company_name": company_name,
                "tone": tone 
            })
            return res.content
        except Exception as e:
            logging.error(f"Email Generation error:{e}")
            return "An error occurred while generating the email. Please verify your inputs and try again."

    def summarize_and_get_links(self, model_name,about_us_text):
       
        # Get the LLM model for summarizing
        llm = self.get_model(model_name)  # You can replace "LLama" with any other model you're using
        
        # Summarize the 'About Us' text using the LLM
        prompt_summarize = """
        ### ABOUT US TEXT:
        {about_us_text}
        
        ### INSTRUCTION:
        Provide a concise summary of the key points about this company and its offerings. Focus on relevant services, core competencies, and industry expertise.
        
        Additionally, extract any portfolio links or references to projects, if mentioned in the text.
        
        ### SUMMARY:
        """
        # Invoke the LLM to generate the summary
        try:
            summary_chain = PromptTemplate.from_template(prompt_summarize) | llm
            result = summary_chain.invoke({"about_us_text": about_us_text})
            
            summary = result.content.strip()
            
            # Use regex to extract links from the 'About Us' text
            links = re.findall(r'(https?://[^\s]+)', about_us_text)
            
            return {"About us":summary,"links": links}
        
        except Exception as e:
            logging.error(f"Summarization error: {e}")
            return "An error occurred during summarization. Please try again later.", []
    