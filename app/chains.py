from langchain_groq import ChatGroq # To Call model from Groq platform
from langchain_core.prompts import PromptTemplate # To make prompt
from langchain_core.output_parsers import JsonOutputParser #To pass the Json data
from langchain_core.exceptions import OutputParserException # 
from dotenv import load_dotenv #Load Environment veriable
import os #Load the data from system
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging
import re
# Initialize a logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

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
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res,list) else [res]
    
    # def write_mail_with_translation(self, model_name, job, links, language, full_name, designation, company_name):
        # llm = self.get_model(model_name)  # Get the LLM based on the model name

        # # Unified prompt that generates the email and optionally translates it
        # prompt_email_translate = PromptTemplate.from_template(
        # """
        # ### JOB DESCRIPTION:
        # {job_description}

        # ### INSTRUCTION:
        # You are {full_name}, a {designation} at {company_name}. {company_name} is an AI & Software Consulting company dedicated to 
        # facilitating the seamless integration of business processes through automated tools. 
        # Over our experience, we have empowered numerous enterprises with tailored solutions, fostering scalability, 
        # process optimization, cost reduction, and heightened overall efficiency. 
        # Your job is to write a cold email to the client regarding the job mentioned above describing the capability of {company_name} 
        # in fulfilling their needs.
        # Also, add the most relevant ones from the following links to showcase {company_name}'s portfolio: {link_list}
        # Remember you are {full_name}, {designation} at {company_name}.
        # Do not provide a preamble.

        # After writing the email in English, translate it into {target_language}.
        # If the target language is English, no translation is needed.

        # ### EMAIL (IN ENGLISH AND THEN TRANSLATED TO {target_language} IF NEEDED):
    #     """
    # )
        
    #     # Invoke the LLM with both job and language context
    #     chain_email_translate = prompt_email_translate | llm
    #     # Invoke the chain with the dynamic inputs
    #     res = chain_email_translate.invoke({
    #         "job_description": str(job),
    #         "link_list": links,
    #         "target_language": language,
    #         "full_name": full_name,
    #         "designation": designation,
    #         "company_name": company_name
    #     })

    #     return res.content
    
    @retry(
        stop=stop_after_attempt(5),  # Retry up to 5 times
        wait=wait_exponential(multiplier=0.1, min=0.2, max=60),  # Exponential backoff starting at 200ms
        retry=retry_if_exception_type(Exception)  # Retry only on rate limit error (429)
    )
    def write_cover_note(self, model_name, full_name, designation, company_name, about_us_text, job, target_language):
        llm = self.get_model(model_name)  # Get the LLM based on the selection

        # Prompt template for generating the cover note
        prompt_cover_note = PromptTemplate.from_template(
            """
            ### ABOUT US (Service Provider):
            {about_us}

            ### JOB DESCRIPTION:
            {job_description}

            ### INSTRUCTION:
            You are {full_name}, {designation} at {company_name}. Your company specializes in providing services as described in the 'ABOUT US' section above. 
            You are writing a professional cover note to pitch your services to a potential client based on the job description provided.
            
            
            The goal is to explain how {company_name}'s expertise can help fulfill the client's needs for this job role. 
            Align {company_name}'s strengths with the requirements of the job and emphasize relevant skills, experience, and solutions.
            
            Ensure that the note is concise, relevant, and to the point. If there isn't enough data in the 'ABOUT US' section or the job description, 
            avoid adding irrelevant or fabricated information.

            After writing the cover note in English, translate it into {target_language}.
            If the target language is English, no translation is needed.

            ### COVER NOTE (IN ENGLISH AND TRANSLATED TO {target_language} IF NEEDED):
            """
        )
        try:
            # Invoke the LLM with both job and language context
            chain_cover_note = prompt_cover_note | llm
            # Invoke the chain with the dynamic inputs
            res = chain_cover_note.invoke({
                "full_name": full_name,
                "designation": designation,
                "company_name": company_name,
                "about_us": about_us_text,
                "job_description": job,
                "target_language": target_language
            })
            # Log the success for tracking
            logger.info(f"Cover note successfully generated for {company_name} targeting job: {job.get('title', 'Unknown')}")

            return res.content
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return f"An error occurred while generating the cover note: {e}"
    
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
            - "techstack": A string representing the technologies used (e.g., React, Node.js, MongoDB).
            - `links`: A valid URL showcasing the portfolio.

            Please ensure the output is a valid JSON without any additional text or commentary.

            ### VALID JSON FORMAT (NO PREAMBLE):
            
            """
        )
        # Chain the prompt with the LLM model
        chain_extract = prompt_extract | llm
        result = chain_extract.invoke(input={"portfolio_data": cleaned_text})
        # print(result.content)

        # Parse the output to JSON format
        try:
            json_parser = JsonOutputParser()
            result = json_parser.parse(result.content)
        except OutputParserException:
            raise OutputParserException("Unable to parse portfolio data.")

        return result if isinstance(result, list) else [result]
    

    def write_mail_with_translation(self, model_name, job, links, language, full_name, designation, company_name, about_us=None, comments=None):
        llm = self.get_model(model_name)  # Get the LLM based on the model name

        # Define the base company description
        company_description = f"{company_name} is a consulting company specializing in providing services tailored to meet the needs of various industries."
        
        # If 'About Us' data is available, include it in the description
        if about_us:
            company_description += f" {about_us}"
        
        # If additional comments are provided, include them as well
        if comments:
            company_description += f" {comments}"

        # Unified prompt that generates the email and optionally translates it
        prompt_email_translate = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

            ### COMPANY DESCRIPTION:
            {company_description}

            ### INSTRUCTION:
            You are {full_name}, a {designation} at {company_name}. Based on the company description provided above, write a cold email to the client regarding the job described, 
            highlighting {company_name}'s capabilities tofulfilling their needs.
            Optionally, include relevant portfolio links to showcase {company_name}'s work: {link_list}


            
            Ensure the email is professional, concise, and aligned with the job description. Avoid irrelevant or fabricated details.
            
            After writing the email in English, translate it into {target_language}. If the target language is English, no translation is needed.
            Do not provide a preamble.

            ### EMAIL (IN ENGLISH AND THEN TRANSLATED TO {target_language} IF NEEDED):
            """
        )

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
            "company_name": company_name
        })

        return res.content

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
            return f"An error occurred during summarization: {e}", []
     
        
        # # Query relevant links from the portfolio based on skills
        # summarize = prompt_summarize|llm
        # res = summarize.invoke({
        #     "about_us_text":about_us_text
        # })

