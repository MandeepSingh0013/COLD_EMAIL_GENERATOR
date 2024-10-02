import pandas as pd
import chromadb 
import uuid 
from io import StringIO
# from sentence_transformers  import  SentenceTransformer

class Portfolio:
    def __init__(self):
        self.chroma_client=chromadb.PersistentClient('vectorstore')
        self.collection=self.chroma_client.get_or_create_collection(name="portfolio")

    # def load_csv(self,file_path):
            
        # self.file_path=file_path #StringIO(file_path.getvalue().decode("utf-8")) #file_path
        # self.data=pd.read_csv(self.file_path)
        # #Validate the columns
        # if "Techstack" in self.data.columns and "Links" in self.data:
        #     return "success"
        # else:
        #     return "error"
        
    def load_portfolio(self,data):
        if not self.collection.count():
            # Load a pre-trained model
            # model = SentenceTransformer('all-MiniLM-L6-v2')
            for _, row in data.iterrows():
                # techstack_embeddings=model.encode()
                self.collection.add(documents=row["Techstack"],#techstack_embeddings,
                                    metadatas={"links": row["Links"]},
                                    ids=[str(uuid.uuid4())])
    def query_links(self,skills):
        return self.collection.query(query_texts=skills,n_results=2).get('metadatas',[])
