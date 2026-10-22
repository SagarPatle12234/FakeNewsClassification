import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
from datasets import load_dataset
import urllib.request
import json
from tqdm import tqdm
import os
import zipfile

def initialize_db(db_path="./chroma_db", collection_name="real_news_facts"):
    print(f"Initializing ChromaDB at '{db_path}'...")
    client = chromadb.PersistentClient(path=db_path)
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=sentence_transformer_ef
    )
    return collection

def ingest_csv_data(collection, csv_path='data/cleaned_fake_news_data.csv'):
    print(f"\n--- Ingesting CSV Data from {csv_path} ---")
    df = pd.read_csv(csv_path)
    
    # Filter for ONLY Real News
    real_news_df = df[df['label'] == 1].copy()
    
    documents = real_news_df['full_text'].astype(str).tolist()
    ids = [f"article_{i}" for i in range(len(real_news_df))]
    
    print(f"Embedding {len(documents)} core news articles into ChromaDB...")
    
    BATCH_SIZE = 250
    for i in tqdm(range(0, len(documents), BATCH_SIZE), desc="Processing News Batches"):
        batch_docs = documents[i : i + BATCH_SIZE]
        batch_ids = ids[i : i + BATCH_SIZE]
        collection.add(documents=batch_docs, ids=batch_ids)
        
    print("Core News Vector Database ingestion complete!")

def ingest_wiki_data(collection, wiki_sample_size=10000):
    print("\n--- Ingesting Official Wikipedia Data ---")
    print("Streaming data directly from Hugging Face (no massive downloads)...")
    
    # streaming=True prevents downloading the full 20GB dataset
    dataset = load_dataset("wikipedia", "20220301.en", split="train", streaming=True)
    
    wiki_data = []
    # We iterate through the stream and grab exactly what we need
    for i, row in enumerate(dataset):
        if len(wiki_data) >= wiki_sample_size:
            break
        # Keep only substantive articles (ignore tiny stubs)
        if len(row['text'].strip()) > 150:
            wiki_data.append({
                "id": f"wiki_{row['id']}",
                "text": row['text']
            })
            
    df_wiki = pd.DataFrame(wiki_data)
    print(f"Successfully streamed {len(df_wiki)} articles.")
    
    documents = df_wiki['text'].tolist()
    ids = df_wiki['id'].tolist()
    
    print(f"Embedding {len(documents)} Wikipedia articles into your existing Vector DB...")
    
    BATCH_SIZE = 250
    for i in tqdm(range(0, len(documents), BATCH_SIZE), desc="Processing Wiki Batches"):
        batch_docs = documents[i : i + BATCH_SIZE]
        batch_ids = ids[i : i + BATCH_SIZE]
        collection.add(documents=batch_docs, ids=batch_ids)
        
    print("Wikipedia expansion complete!")

if __name__ == "__main__":
    # 1. Initialize or connect to the database
    db_collection = initialize_db()
    
    # Ingest Wikipedia encyclopedic data
    ingest_wiki_data(db_collection)