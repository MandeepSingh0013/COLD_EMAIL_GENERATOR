import pandas as pd
import chromadb 
import uuid 
from io import StringIO
import json
# from sentence_transformers  import  SentenceTransformer

class Portfolio:
    def __init__(self):
        self.chroma_client=chromadb.PersistentClient('vectorstore')
        self.collection=self.chroma_client.get_or_create_collection(name="portfolio")
        self.collection_feedback = self.chroma_client.get_or_create_collection(name="portfolio_feedback")
        
    def clear_old_data(self):
        """
        Clears the older data in the collection before uploading the new file.
        """
        if self.collection.count():
            self.collection.delete(where={})  # This will delete all the documents in the collection.
        
    def load_portfolio(self,data):
        if not self.collection.count():
            # Load a pre-trained model
            # model = SentenceTransformer('all-MiniLM-L6-v2')
            # self.clear_old_data()
            for _, row in data.iterrows():
                # techstack_embeddings=model.encode()
                self.collection.add(documents=row["Techstack"],#techstack_embeddings,
                                    metadatas={"links": row["Links"]},
                                    ids=[str(uuid.uuid4())])
    
    def store_feedback(self, extracted_data, original_data, feedback, detailed_feedback):
        if isinstance(extracted_data, (list, dict)):
            extracted_data = json.dumps(extracted_data)
        # Store feedback in ChromaDB
        self.collection_feedback.add(
            documents=original_data,  # Store the original portfolio data
            metadatas={"feedback": feedback, "comments": detailed_feedback, "extracted_data": extracted_data},
            ids=[str(uuid.uuid4())]
        )
    
    def query_links(self,skills):
        return self.collection.query(query_texts=skills,n_results=2).get('metadatas',[])
    
    # Fetch feedback data for fine-tuning
    
    def collect_feedback_for_rlhf(self):
        # Query ChromaDB to fetch all negative feedback for fine-tuning
        feedback_data = self.collection_feedback.get()  # Fetch all records
        negative_feedback = [item for item in feedback_data if item['feedback'] == "👎"]
        
        if negative_feedback:
            return True, negative_feedback
        else:
            return False, "No negative feedback available for fine-tuning."



# import streamlit as st
# import chain_smith as cs

# class Portfolio:
#     def __init__(self):
#         self.chroma_client = chromadb.PersistentClient('vectorstore')
#         self.collection = self.chroma_client.get_or_create_collection(name="portfolio")
#         self.rl_model = cs.RLHFModel("LLama", "groq_api_key")  # Assuming you use RLHF with LLama

#     def load_portfolio(self, data):
#         if not self.collection.count():
#             for _, row in data.iterrows():
#                 self.collection.add(
#                     documents=row["Techstack"],
#                     metadatas={"links": row["Links"]},
#                     ids=[str(uuid.uuid4())]
#                 )

#     def query_links(self, skills):
#         return self.collection.query(query_texts=skills, n_results=2).get('metadatas', [])
    
#     def feedback_portfolio(self):
#         st.session_state.feedback_portfolio = st.selectbox("Was the extracted data accurate?", ("👍", "👎"))
    
#     def button_feedback(self):
#         if st.button("Submit Feedback"):
#             feedback = st.session_state.feedback_portfolio
#             if feedback == "👍":
#                 st.success("Thanks for the positive feedback!")
#             elif feedback == "👎":
#                 st.warning("Feedback noted! We'll fine-tune the model.")

#                 # Collect feedback to improve model
#                 self.collect_feedback_for_rlhf()
#             else:
#                 st.error("Please provide feedback.")

#     def collect_feedback_for_rlhf(self):
#         # Use ChainSmith's RLHF for fine-tuning based on feedback
#         # Gather incorrect extractions and retrain
#         try:
#             incorrect_extractions = self.get_incorrect_extractions()  # Custom method to gather inaccurate data
#             # Use ChainSmith to fine-tune the model based on the feedback
#             self.rl_model.fine_tune(incorrect_extractions)
#             st.success("Model fine-tuning complete based on feedback.")
#         except Exception as e:
#             st.error(f"An error occurred while fine-tuning: {e}")

#     def get_incorrect_extractions(self):
#         # Implement logic to collect incorrect data based on user feedback
#         # You could store the incorrect data for the RLHF process
#         pass

# # Inside Streamlit app
# def upload_portfolio_csv(self):
#     st.subheader("Upload Your Portfolio File")
#     uploaded_file = st.file_uploader("Choose a file", type=["csv", "pdf", "docx", "xlsx"])
#     if uploaded_file:
#         try:
#             st.session_state.status, portfolio_data = self.file_handler.process_file(uploaded_file)
#             if st.session_state.status == "success":
#                 st.success("File Uploaded and Validated Successfully!")
#                 with st.spinner("Processing the portfolio data..."):
#                     cleaned_data = clean_portfolio_text(portfolio_data)
#                     st.session_state.techstack_link = self.chain.extract_portfolio_data(self.temp_model_choice, cleaned_data)
#                     df = pd.DataFrame(st.session_state.techstack_link)
#                     self.portfolio.load_portfolio(df)
#                     st.dataframe(df)
#             else:
#                 st.error("Invalid file format or content. Please check the file.")
#         except Exception as e:
#             st.error(f"Error reading the file: {e}")
#     else:
#         st.info("Please upload a file to proceed.")

# # Collect feedback after showing extracted portfolio data
# def handle_feedback(self):
#     self.portfolio.feedback_portfolio()
#     self.portfolio.button_feedback()

# # Initialize and run
# portfolio = Portfolio()
# upload_portfolio_csv(portfolio)
# handle_feedback(portfolio)

# # # whisper model transcription, llm model summerize theaudio transcript get sentiment detailed  topics dicussed , major keywords include in the conversation