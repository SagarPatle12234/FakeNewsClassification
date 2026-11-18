import os
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

def ingest_csv_data(vector_store, csv_path='data/cleaned_fake_news_data.csv'):
    print(f"\n--- Ingesting CSV Data from {csv_path} ---")
    df = pd.read_csv(csv_path)
    real_news_df = df[df['label'] == 1].copy()
    
    raw_documents = real_news_df['full_text'].astype(str).tolist()
    
    print("Chunking long articles to safely bypass Pinecone's metadata size limits...")
    
    # Initialize the text splitter (8000 chars is safely below the 40KB limit)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=8000, 
        chunk_overlap=500
    )
    
    # Slice the massive articles into manageable chunks
    chunked_documents = []
    for doc in raw_documents:
        chunked_documents.extend(text_splitter.split_text(doc))
        
    print(f"Uploading {len(chunked_documents)} chunked text segments to Pinecone Cloud...")
    
    # Upload in batches
    BATCH_SIZE = 100
    for i in tqdm(range(0, len(chunked_documents), BATCH_SIZE), desc="Processing News Batches"):
        batch_docs = chunked_documents[i : i + BATCH_SIZE]
        vector_store.add_texts(texts=batch_docs)
        
    print("Core News Vector Database ingestion complete!")

if __name__ == "__main__":
    import os
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    pinecone_api_key = os.environ.get("PINECONE_API_KEY")
    
    vector_store = PineconeVectorStore(
        index_name="real-news-facts", 
        embedding=embeddings, 
        pinecone_api_key=pinecone_api_key
    )
    
    ingest_csv_data(vector_store)