import os
import re
import openai
import streamlit as st
# from langchain_community.llms import OpenAI
from langchain_community.chat_models.openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()

class EmailRefinerApp:
    def __init__(self):

        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=os.getenv("OPENAI_KEY"),  # if you prefer to pass api key in directly instaed of using env vars
        )

    def refine_email(self, generated_email, feedback,target_language):
        # Use regular expressions to separate the English and translated sections
        english_match = re.search(r"### EMAIL \(IN ENGLISH\)(.*?)(?=### EMAIL \(TRANSLATED)", generated_email, re.DOTALL)
        translated_match = re.search(r"### EMAIL \(TRANSLATED TO .*?\)(.*)", generated_email, re.DOTALL)

        # Get the content if matches are found
        generated_email_english = english_match.group(1).strip() if english_match else ""
        generated_email_translated = translated_match.group(1).strip() if translated_match else ""

        prompt = ChatPromptTemplate.from_messages([
                    f"""
            The following email introduces your expertise and professional background, specifically highlighting your company’s strengths and relevant experience.

            ### Original Email (in English):
            {generated_email_english}

            ### Translated Email (in {target_language}) (if applicable):
            {generated_email_translated}

            Feedback provided by the user for improvement:
            {feedback}

            Using the feedback, refine the existing email to enhance clarity, relevance, and impact while preserving the original structure, tone, and key points. Avoid adding new information unless explicitly requested in the feedback. Focus on emphasizing your company’s expertise, aligning your message more closely with the client's needs, and making improvements to any areas specifically noted in the feedback.

            Maintain Quality.

            ### Improved Email (in English and {target_language}):
            """])

        chain = prompt| self.llm
        res=chain.invoke(
            {
                "generated_email_english": generated_email, "feedback": feedback,"target_language":target_language,
                "generated_email": generated_email_english, "generated_email_translated": generated_email_translated
            }
        )
        # print(res.content)
        return res.content
    
    def refine_cover_note(self, generated_cover_note, feedback,target_language):
        # Use regular expressions to separate the English and translated sections
        english_match = re.search(r"### COVER NOTE \(IN ENGLISH\)(.*?)(?=### COVER NOTE \(TRANSLATED)", generated_cover_note, re.DOTALL)
        translated_match = re.search(r"### COVER NOTE \(TRANSLATED TO .*?\)(.*)", generated_cover_note, re.DOTALL)
        # Get the content if matches are found
        generated_cover_letter_english = english_match.group(1).strip() if english_match else ""
        generated_cover_letter_translated = translated_match.group(1).strip() if translated_match else ""
        prompt = ChatPromptTemplate.from_messages([
          """
            The following cover note introduces your expertise and professional background, with an emphasis on relevant skills and experience for the role.

            ### Original Cover Note (in English):
            {generated_cover_note_english}

            ### Translated Cover Note (in {target_language}) (if applicable):
            {generated_cover_note_translated}

            Feedback provided by the user for improvement:
            {feedback}

            Using the feedback, refine the existing cover note to enhance clarity, relevance, 
            and impact while maintaining the original structure, tone, and information. 
            Avoid introducing new content unless explicitly required by the feedback. 
            Focus on emphasizing expertise, aligning your qualifications more closely with the client's needs, 
            and improving any sections highlighted in the feedback.

            Maintain Quality.

            ### Improved Cover Note (in English and {target_language}):
            """ ])

        chain = prompt| self.llm
        res=chain.invoke(
            {
                "generated_cover_note_english": generated_cover_letter_english,
                "generated_cover_note_translated": generated_cover_letter_translated,
                "feedback": feedback,
                "target_language":target_language
            }
        )
        # print(res.content)
        return res.content