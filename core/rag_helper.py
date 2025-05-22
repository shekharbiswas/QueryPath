# querypath_app/core/rag_helper.py
import streamlit as st
from sentence_transformers import SentenceTransformer
import chromadb

# --- Configuration (same as before) ---
CHROMA_DB_PATH = "./chroma_db_sql_hints"
COLLECTION_NAME = "sql_hints_knowledge_base"
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'

# --- Initialize Embedding Model and Vector DB Client (same as before) ---
@st.cache_resource(show_spinner="Loading hint system...") # Combined spinner
def load_embedding_model_and_collection():
    embedding_model = None
    hints_collection = None
    try:
        embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        print("INFO: RAG Embedding model loaded.")
    except Exception as e:
        print(f"ERROR: Failed to load RAG embedding model: {e}")
        st.error(f"Hint system (embedding model) error: {e}")

    try:
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        # Try to get collection, if it fails, it means it likely wasn't created by populate_chroma_kb.py
        hints_collection = client.get_collection(name=COLLECTION_NAME)
        print(f"INFO: Connected to ChromaDB collection '{COLLECTION_NAME}' with {hints_collection.count()} items.")
    except Exception as e:
        print(f"ERROR: Failed to connect/get ChromaDB collection '{COLLECTION_NAME}': {e}")
        st.error(f"Hint Knowledge Base error: {e}. Please ensure 'populate_chroma_kb.py' has been run successfully.")
    
    return embedding_model, hints_collection

embedding_model, hints_collection = load_embedding_model_and_collection()


@st.cache_data(show_spinner="🧠 Searching for relevant hints...", ttl=300)
def get_vector_db_hints(user_query: str, challenge_prompt: str, sql_error: str = None, top_k=2): # Can retrieve more than 1
    if not embedding_model or not hints_collection:
        return ["Hint system not initialized. Cannot provide hints."] # Return a list

    # 1. Construct a query string for embedding
    query_for_embedding = f"User query: {user_query}\nProblem: {challenge_prompt}"
    if sql_error:
        query_for_embedding += f"\nSQL Error: {sql_error}"
    
    # 2. Embed the query
    try:
        query_vector = embedding_model.encode(query_for_embedding).tolist()
    except Exception as e:
        st.error(f"Error embedding user query: {e}")
        return ["Could not process your query for hinting."]

    # 3. Query Vector DB
    retrieved_hints_texts = []
    try:
        results = hints_collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            include=['documents'] # We only need the document text
        )
        if results and results.get('documents') and results['documents'][0]:
            retrieved_hints_texts.extend(results['documents'][0])
        
        if not retrieved_hints_texts:
            return ["No specific pre-written hint found for this issue. Try rephrasing your query or focusing on the SQL error message if one was provided."]
        
        return retrieved_hints_texts

    except Exception as e:
        st.error(f"Error querying vector database: {e}")
        return ["Error retrieving hints from the knowledge base."]

# The `index_knowledge_base_into_chroma` and `populate_chroma_kb.py` script remain essential.
# The `format_schema_for_llm` is no longer needed in this helper if no LLM is called.