import pandas as pd
import chromadb 
import uuid 
from sentence_transformers  import  SentenceTransformer

class Portfolio:
    def __init__(self,file_path="app/resource/my_portfolio.csv"):
        self.file_path= file_path
        self.data=pd.read_csv(self.file_path)

        self.chroma_client=chromadb.PersistentClient('vectorstore')
        self.collection=self.chroma_client.get_or_create_collection(name="portfolio")
    
    def load_portfolio(self):
        if not self.collection.count():
            # Load a pre-trained model
            model = SentenceTransformer('all-MiniLM-L6-v2')
            for _, row in self.data.iterrows():
                techstack_embeddings=model.encode(row["Techstack"])
                self.collection.add(documents=techstack_embeddings,
                                    metadatas={"links": row["Links"]},
                                    ids=[str(uuid.uuid4())])
    def query_links(self,skills):
        return self.collection.query(query_texts=skills,n_results=2).get('metadatas',[])
