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
    # def write_mail(self,model_name,job,links):
    #     llm = self.get_model(model_name)
    #     prompt_email = PromptTemplate.from_template(
    #         """
    #         ### JOB DESCRIPTION:
    #         {job_description}

    #         ### INSTRUCTION:
    #         You are Mandeep, a business development executive at MSpace. MSpace is an AI & Software Consulting company dedicated to facilitating
    #         the seamless integration of business processes through automated tools. 
    #         Over our experience, we have empowered numerous enterprises with tailored solutions, fostering scalability, 
    #         process optimization, cost reduction, and heightened overall efficiency. 
    #         Your job is to write a cold email to the client regarding the job mentioned above describing the capability of MSpace 
    #         in fulfilling their needs.
    #         Also add the most relevant ones from the following links to showcase MSpace's portfolio: {link_list}
    #         Remember you are Mandeep, BDE at MSpace. 
    #         Do not provide a preamble.
    #         ### EMAIL (NO PREAMBLE):
    #         """
    #     )
    #     chain_email= prompt_email | llm
    #     res = chain_email.invoke({"job_description":str(job),"link_list":links})
    #     return res.content
    

    def write_mail_with_translation(self, model_name, job, links, language, full_name, designation, company_name):
        llm = self.get_model(model_name)  # Get the LLM based on the model name

        # Unified prompt that generates the email and optionally translates it
        prompt_email_translate = PromptTemplate.from_template(
        """
        ### JOB DESCRIPTION:
        {job_description}

        ### INSTRUCTION:
        You are {full_name}, a {designation} at {company_name}. {company_name} is an AI & Software Consulting company dedicated to 
        facilitating the seamless integration of business processes through automated tools. 
        Over our experience, we have empowered numerous enterprises with tailored solutions, fostering scalability, 
        process optimization, cost reduction, and heightened overall efficiency. 
        Your job is to write a cold email to the client regarding the job mentioned above describing the capability of {company_name} 
        in fulfilling their needs.
        Also, add the most relevant ones from the following links to showcase {company_name}'s portfolio: {link_list}
        Remember you are {full_name}, {designation} at {company_name}.
        Do not provide a preamble.

        After writing the email in English, translate it into {target_language}.
        If the target language is English, no translation is needed.

        ### EMAIL (IN ENGLISH AND THEN TRANSLATED TO {target_language} IF NEEDED):
        """
    )
        
        # Invoke the LLM with both job and language context
        chain_email_translate = prompt_email_translate | llm
        # Invoke the chain with the dynamic inputs
        res = chain_email_translate.invoke({
            "job_description": str(job),
            "link_list": links,
            "target_language": language,
            "full_name": full_name,
            "designation": designation,
            "company_name": company_name
        })

        return res.content

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
            return res.content
        except Exception as e:
                
            return f"An error occurred while generating the cover note: {e}"


    # #Creating Translation using LLM
    # def translate_text(self, model_name, email, language):
    #     llm = self.get_model(model_name)  # Get the LLM based on the model name
    #     prompt_translate = PromptTemplate.from_template(
    #         """
    #         ### EMAIL TO TRANSLATE:
    #         {email_content}

    #         ### INSTRUCTION:
    #         You are a multilingual language expert. Your job is to translate the email content provided above into {target_language}.
    #         Ensure the tone and context remain professional and formal.
            
    #         ### TRANSLATED EMAIL (NO PREAMBLE):
    #         """
    #     )
    #     # Creating the prompt with target language
    #     chain_translate = prompt_translate | llm
    #     res = chain_translate.invoke({"email_content": str(email), "target_language": language})
    #     return res.content