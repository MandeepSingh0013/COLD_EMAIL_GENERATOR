from langchain_groq import ChatGroq # To Call model from Groq platform
from langchain_core.prompts import PromptTemplate # To make prompt
from langchain_core.output_parsers import JsonOutputParser #To pass the Json data
from langchain_core.exceptions import OutputParserException # 
from dotenv import load_dotenv #Load Environment veriable
import os #Load the data from system

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
        max_retries=2)

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
    
    #Creating MAIL using LLM
    def write_mail(self,model_name,job,links):
        llm = self.get_model(model_name)
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

            ### INSTRUCTION:
            You are Mandeep, a business development executive at MSpace. MSpace is an AI & Software Consulting company dedicated to facilitating
            the seamless integration of business processes through automated tools. 
            Over our experience, we have empowered numerous enterprises with tailored solutions, fostering scalability, 
            process optimization, cost reduction, and heightened overall efficiency. 
            Your job is to write a cold email to the client regarding the job mentioned above describing the capability of AtliQ 
            in fulfilling their needs.
            Also add the most relevant ones from the following links to showcase MSpace's portfolio: {link_list}
            Remember you are Mandeep, BDE at MSpace. 
            Do not provide a preamble.
            ### EMAIL (NO PREAMBLE):
            """
        )
        chain_email= prompt_email | llm
        res = chain_email.invoke({"job_description":str(job),"link_list":links})
        return res.content