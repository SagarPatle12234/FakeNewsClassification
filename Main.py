import os
import json
from dotenv import load_dotenv

# Load the keys from your .env file FIRST
load_dotenv()

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_tavily import TavilySearch

# --- 1. Connect to Existing ChromaDB ---
# Must match the "all-MiniLM-L6-v2" model you used in build_news_db.py
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

vector_store = Chroma(
    collection_name="real_news_facts",
    persist_directory="./chroma_db",
    embedding_function=embeddings
)
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

# --- 2. Initialize the Free Tier Gemini Model ---
# Retrieve the key explicitly from the environment
google_api_key = os.environ.get("GOOGLE_API_KEY")

if not google_api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment. Please check your .env file.")

# New (Correct) Model Initialization
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite", 
    temperature=0,
    api_key=google_api_key
)

# --- 3. Tier 1: Local LLM Judge Chain ---
local_judge_prompt = PromptTemplate(
    template="""You are an expert fact-checking AI judge. Evaluate the user's news claim STRICTLY against the provided local evidence.

    [LOCAL EVIDENCE]
    {context}

    [USER CLAIM]
    {claim}

    Output a JSON object with two fields:
    1. "verdict": Must be exactly one of ["SUPPORTS", "REFUTES", "UNVERIFIABLE"].
       - SUPPORTS: Evidence proves the claim is real.
       - REFUTES: Evidence proves the claim is fake.
       - UNVERIFIABLE: Evidence is missing, unrelated, or lacks specific details to make a firm judgment.
    2. "rationale": A single sentence explaining why you chose this verdict.
    """,
    input_variables=["context", "claim"]
)

# LCEL Chain: Prompt -> LLM -> JSON Parser
tier_1_chain = local_judge_prompt | llm | JsonOutputParser()

# --- 4. Tier 2: Live Web Search Chain ---
# Using the updated non-deprecated Tavily package
tavily_tool = TavilySearch(max_results=5, include_raw_content=True)

live_search_prompt = PromptTemplate(
    template="""You are an investigative fact-checker. Evaluate the user's news claim against the provided live web evidence.

    [USER CLAIM]
    {claim}

    [LIVE WEB EVIDENCE]
    {web_evidence}

    Output a JSON object with three fields:
    1. "verdict": ["REAL", "FAKE", "UNVERIFIABLE"].
    2. "explanation": A detailed paragraph explaining the verdict based on the web evidence.
    3. "summary": A 1-2 sentence truth summary.
    """,
    input_variables=["claim", "web_evidence"]
)

tier_2_chain = live_search_prompt | llm | JsonOutputParser()

# --- 5. The Routing Logic ---
def fact_check_pipeline(claim: str):
    print(f"\n[Tier 1] Querying Local Database for: '{claim}'")
    
    # Retrieve local documents
    docs = retriever.invoke(claim)
    local_context = "\n\n".join([doc.page_content for doc in docs])
    
    # Run the Tier 1 Judge
    local_result = tier_1_chain.invoke({"context": local_context, "claim": claim})
    print(f"Local Verdict: {local_result['verdict']}")
    print(f"Rationale: {local_result['rationale']}")
    
    # Routing Condition
    if local_result["verdict"] == "UNVERIFIABLE":
        print("\n[Router] Local database lacked sufficient evidence. Escalating to Tier 2 (Live Web Search)...")
        
        # Execute Tavily Search via LangChain tool
        web_results = tavily_tool.invoke({"query": claim})

       #Add ["results"] to properly access the list of search sources
        web_context = "\n\n".join([f"Source: {res['url']}\nContent: {res['content']}" for res in web_results["results"]])
        
        # Run the Tier 2 Judge
        final_result = tier_2_chain.invoke({"claim": claim, "web_evidence": web_context})
        
        # Attach the live sources for transparency
        final_result["sources"] = [res['url'] for res in web_results["results"]]
        final_result["tier_used"] = "Tier 2 (Live Web)"
        
        return final_result
        
    else:
        print("\n[Router] Fact confirmed locally. Halting pipeline.")
        # Format the local result to match the expected final output structure
        return {
            "verdict": "REAL" if local_result["verdict"] == "SUPPORTS" else "FAKE",
            "explanation": local_result["rationale"],
            "summary": "Verified against local database.",
            "sources": ["Local Database"],
            "tier_used": "Tier 1 (Local)"
        }

if __name__ == "__main__":
    test_claim = "Murder Happened in jaitala area of Nagpur today on 22-10-2026"
    
    print("=== Initiating Fact-Check Pipeline ===")
    report = fact_check_pipeline(test_claim)
    
    print("\n=== Final Fact-Check Report ===")
    print(json.dumps(report, indent=4))