import pandas as pd
import chromadb 
import uuid 
from io import StringIO
import json


class Portfolio:
    def __init__(self):
        self.chroma_client=chromadb.PersistentClient('vectorstore')
        self.collection=self.chroma_client.get_or_create_collection(name="portfolio")
        self.collection_feedback = self.chroma_client.get_or_create_collection(name="portfolio_feedback")
        
    def clear_old_data(self):
        if self.collection.count() > 0:
            try:
                if self.collection.count() > 0:
                 # Retrieve all document IDs from the collection
                    result = self.collection.get()
                    # Ensure that we get a list of IDs
                    ids_to_delete = result.get('ids', [])
                    
                    if ids_to_delete:
                        # Delete all documents by their IDs
                        self.collection.delete(ids=ids_to_delete)
                    # else:
                        # print("No document IDs found to delete.")
                # else:
                    # print("No documents in the collection.")
                
            except Exception as e:
                pass
                # print(f"Error while clearing data: {e}")

    def load_portfolio(self,data):
        self.clear_old_data()
        if not self.collection.count():
            # Check if data is a DataFrame or similar structure
            if isinstance(data, pd.DataFrame):
                for _, row in data.iterrows():
                    try:
                        # Attempt to access 'Techstack' safely
                        techstack_value = row["Techstack"]  # Adjust based on your actual data structure
                        links_value = row["Links"]  # Adjust based on your actual data structure

                        # Add documents to the collection
                        self.collection.add(documents=techstack_value,
                                            metadatas={"links": links_value},
                                            ids=[str(uuid.uuid4())])
                    except KeyError as e:
                        pass
                        # print(f"Key error: {e}. Make sure the column exists in the DataFrame.")
                    except Exception as e:
                        pass
                        # print(f"An unexpected error occurred: {e}")
            else:
                pass
                # print("Expected a DataFrame but received:", type(data))
           
    def store_feedback(self, extracted_data, original_data, feedback, detailed_feedback):
        if isinstance(extracted_data, (list, dict)):
            extracted_data = json.dumps(extracted_data)
        # Store feedback in ChromaDB
        self.collection_feedback.add(
            documents=original_data,  # Store the original portfolio data
            metadatas={"feedback": feedback, "comments": detailed_feedback, "extracted_data": extracted_data},
            ids=[str(uuid.uuid4())]
        )
    def get_all_techstack(self):
        # Retrieve all documents in the collection
        all_documents = self.collection.get()['documents']
        return all_documents

    
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

