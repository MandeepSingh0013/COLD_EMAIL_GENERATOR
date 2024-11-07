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
            You’re a skilled email editor with a strong background in crafting effective cold emails. You have successfully enhanced countless cold emails, ensuring they remain true to the original message while making them more engaging and persuasive. Your expertise lies in maintaining the core details and intent of the user while improving the overall effectiveness of the email.
            Your task is to edit and enhance a cold email based on user feedback
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
            You are a skilled cover note specialist with extensive experience in crafting compelling and effective cover notes based on user feedback. Your expertise lies in maintaining the integrity of previously provided user details while enhancing the overall quality and effectiveness of the cover note.

            Your task is to enhancing a cover note using the feedback provided by the user, ensuring that all original user details remain unchanged.

            ### Original Cover Note (in English):
            {generated_cover_note_english}

            ### Translated Cover Note (in {target_language}) (if applicable):
            {generated_cover_note_translated}

            Feedback provided by the user for improvement:
            {feedback}

            Maintain Quality. Please ensure that the final cover note retains all the original details while incorporating the necessary improvements based on the feedback provided. Make the cover note compelling and professional.

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