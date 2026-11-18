# Ai NEWS Detector 🕵️‍♂️📰

A lightweight, high-performance Fake News Classification web application powered by **Corrective Retrieval-Augmented Generation (CRAG)**. 

This system evaluates the authenticity of news claims using a two-tier fact-checking architecture, optimized specifically to run efficiently on free-tier cloud hosting (under 512MB RAM) without sacrificing AI accuracy.

## ✨ Key Features
* **Tier 1 (Database Fact-Checking):** Cross-references user claims against a curated vector database of 36,000+ verified news articles. Powered by **Gemini 3.5 Flash-Lite**.
* **Tier 2 (Live Web Fallback):** If the database lacks sufficient context for breaking news, the CRAG router automatically triggers a live web search to verify the claim in real-time.
* **Ultra-Low Memory Footprint:** Bypasses heavy PyTorch dependencies by utilizing **FastEmbed (ONNX runtime)** to run the `all-MiniLM-L6-v2` embedding model locally in under 100MB of RAM.
* **Serverless Vector Storage:** Utilizes **Pinecone** for lightning-fast semantic retrieval without local memory overhead.

## 🛠️ Tech Stack
* **Backend Framework:** Flask, Gunicorn
* **Frontend:** Custom HTML, CSS, Vanilla JavaScript
* **AI & Orchestration:** LangChain, Google GenAI (Gemini)
* **Embeddings:** FastEmbed (`sentence-transformers/all-MiniLM-L6-v2`)
* **Vector Database:** Pinecone
* **Live Web Search:** Tavily Search API
* **Deployment:** Render

## 🚀 Local Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/SagarPatle12234/FakeNewsClassification.git](https://github.com/SagarPatle12234/FakeNewsClassification.git)
   cd FakeNewsClassification

2. **Install dependencies:
    Ensure you are using Python 3.11.0.**
    ```bash
    pip install -r requirements.txt

3. **Set up Environment Variables:
    Create a .env file in the root directory and add your API keys:**
    ```code snippet
    PINECONE_API_KEY=your_pinecone_api_key
    GOOGLE_API_KEY=your_gemini_api_key
    TAVILY_API_KEY=your_tavily_api_key

4. **Run the application:**
    ```bash
    python app.py
Open your browser and navigate to http://127.0.0.1:5000.

👨‍💻 Author
Sagar Patle

AI/ML Engineering & Data Science