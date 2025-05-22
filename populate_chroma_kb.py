# populate_chroma_kb.py
import chromadb
from sentence_transformers import SentenceTransformer
import os
import uuid # To generate unique IDs for documents

# --- Configuration ---
CHROMA_DB_PATH = "./chroma_db_sql_hints" # Directory where ChromaDB will store its data
COLLECTION_NAME = "sql_hints_knowledge_base"
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2' # A good, relatively small model

# --- Sample Knowledge Base Documents ---
KNOWLEDGE_BASE_DOCUMENTS = [
    # Existing Good Hints
    {
        "id": str(uuid.uuid4()),
        "text": "When using a WHERE clause to filter on string values, make sure the string is enclosed in single quotes. For example: WHERE country = 'Germany'.",
        "metadata": {"topic": "WHERE clause", "type": "syntax_strings"}
    },
    {
        "id": str(uuid.uuid4()),
        "text": "To filter records based on a date, you can use comparison operators like > (greater than) or < (less than) with date strings in 'YYYY-MM-DD' format. Example: WHERE signup_date > '2023-01-01'.",
        "metadata": {"topic": "Date filtering", "type": "syntax_dates"}
    },
    {
        "id": str(uuid.uuid4()),
        "text": "The JOIN clause is used to combine rows from two or more tables, based on a related column between them. Ensure your ON condition correctly specifies how the tables are related.",
        "metadata": {"topic": "JOIN clause", "type": "concept_joins"}
    },
    {
        "id": str(uuid.uuid4()),
        "text": "A common mistake with JOINs is forgetting the ON condition, which can lead to a Cartesian product (all possible combinations of rows), usually not what's intended. Always include an ON clause specifying the join criteria.",
        "metadata": {"topic": "JOIN clause", "type": "common_mistake_joins_on"}
    },
    {
        "id": str(uuid.uuid4()),
        "text": "When using aggregate functions like COUNT(), SUM(), AVG(), you often need a GROUP BY clause to group rows that have the same values in specified columns into summary rows.",
        "metadata": {"topic": "GROUP BY clause", "type": "concept_aggregation"}
    },
    {
        "id": str(uuid.uuid4()),
        "text": "If you select non-aggregated columns along with an aggregate function (like COUNT() or SUM()), those non-aggregated columns must typically appear in the GROUP BY clause.",
        "metadata": {"topic": "GROUP BY clause", "type": "syntax_rule_aggregation"}
    },
    {
        "id": str(uuid.uuid4()),
        "text": "The error 'no such column' often means you have misspelled a column name or are referring to a column that does not exist in the tables specified in your FROM clause (or accessible in the current scope of the query). Double-check your table schemas and spelling carefully.",
        "metadata": {"topic": "SQL errors", "type": "troubleshooting", "error_type": "no such column"}
    },
    {
        "id": str(uuid.uuid4()),
        "text": "The error 'no such table' indicates that the table name you used in your FROM or JOIN clause is either misspelled or does not exist in the database. Verify the table names against the provided schema.",
        "metadata": {"topic": "SQL errors", "type": "troubleshooting", "error_type": "no such table"}
    },
    {
        "id": str(uuid.uuid4()),
        "text": "To combine multiple conditions in a WHERE clause, use the AND operator (if all conditions must be true) or the OR operator (if at least one condition must be true).",
        "metadata": {"topic": "WHERE clause", "type": "logic_and_or"}
    },
    {
        "id": str(uuid.uuid4()),
        "text": "For filtering on boolean (TRUE/FALSE) values, you can use conditions like 'is_premium = TRUE', 'is_premium = FALSE'. Some databases also allow '= 1' for true and '= 0' for false.",
        "metadata": {"topic": "Boolean filtering", "type": "syntax_boolean"}
    },

    # ----- NEW HINTS ADDED TO ADDRESS INCOMPLETE WHERE / SYNTAX ERRORS -----
    {
        "id": str(uuid.uuid4()),
        "text": "A 'syntax error' often means a part of your SQL query is incomplete or incorrectly structured. Review the area mentioned in the error message. For example, a WHERE clause needs a complete condition after it (e.g., `WHERE column_name = 'value`).",
        "metadata": {"topic": "SQL errors", "type": "syntax_error_general", "keyword": "syntax error", "symptom": "incomplete_clause"}
    },
    {
        "id": str(uuid.uuid4()),
        "text": "If your query includes placeholders like '...' or instructions like 'your_condition_here', these must be replaced with actual SQL logic or values before the query can run successfully. Placeholders are not valid SQL.",
        "metadata": {"topic": "SQL syntax", "type": "common_mistake_placeholders", "keyword": "placeholder"}
    },
    {
        "id": str(uuid.uuid4()),
        "text": "It looks like your WHERE clause might be incomplete or missing its condition. A WHERE clause must be followed by a valid condition to filter rows, such as `column_name = 'some_value'` or `column_name > 100`.",
        "metadata": {"topic": "WHERE clause", "type": "syntax_error_where", "symptom": "incomplete_where"}
    },
    {
        "id": str(uuid.uuid4()),
        "text": "A 'syntax error near \".\" or \";\"' can indicate that the statement immediately before that punctuation is not a complete or valid SQL construct. Check for missing keywords, values, or an incorrect structure in the preceding part of your query.",
        "metadata": {"topic": "SQL errors", "type": "syntax_error_punctuation", "symptom": "error_near_semicolon"}
    },
    {
        "id": str(uuid.uuid4()),
        "text": "The SQL error message often points to the part of the query where the problem lies ('near \"...\"'). Carefully examine that section for typos, missing elements, or incorrect SQL grammar.",
        "metadata": {"topic": "SQL errors", "type": "troubleshooting_general_syntax", "keyword": "syntax error"}
    }
    # ------------------------------------------------------------------------
]

def initialize_and_populate_vectordb():
    print(f"Initializing embedding model: {EMBEDDING_MODEL_NAME}...")
    try:
        embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        print("Embedding model loaded.")
    except Exception as e:
        print(f"ERROR: Could not load embedding model '{EMBEDDING_MODEL_NAME}': {e}")
        return

    print(f"Initializing ChromaDB client at path: {CHROMA_DB_PATH}...")
    if not os.path.exists(CHROMA_DB_PATH):
        print(f"ChromaDB path {CHROMA_DB_PATH} does not exist. It will be created.")
    
    try:
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        print("ChromaDB client initialized.")
    except Exception as e:
        print(f"ERROR: Could not initialize ChromaDB client: {e}")
        return

    print(f"Getting or creating collection: {COLLECTION_NAME}...")
    try:
        # --- MODIFIED DELETION HANDLING from previous response ---
        existing_collections_names = [c.name for c in client.list_collections()] # Get names
        collection_exists = COLLECTION_NAME in existing_collections_names

        if collection_exists:
            try:
                print(f"INFO: Collection '{COLLECTION_NAME}' exists. Attempting to delete for a fresh start.")
                client.delete_collection(name=COLLECTION_NAME)
                print(f"INFO: Existing collection '{COLLECTION_NAME}' deleted successfully.")
            except Exception as delete_e:
                print(f"WARNING: Could not delete existing collection '{COLLECTION_NAME}': {delete_e}. Attempting to get/create anyway.")
        else:
            print(f"INFO: Collection '{COLLECTION_NAME}' does not exist. Will be created.")
        # --- END MODIFIED DELETION HANDLING ---

        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"} # Using cosine similarity
        )
        print(f"Collection '{COLLECTION_NAME}' ready. Current count before adding: {collection.count()}")
    except Exception as e:
        print(f"ERROR: Could not get or create ChromaDB collection '{COLLECTION_NAME}': {e}")
        return

    if not KNOWLEDGE_BASE_DOCUMENTS:
        print("No documents found in KNOWLEDGE_BASE_DOCUMENTS. Nothing to index.")
        return

    print(f"\nEmbedding {len(KNOWLEDGE_BASE_DOCUMENTS)} documents...")
    try:
        texts_to_embed = [doc['text'] for doc in KNOWLEDGE_BASE_DOCUMENTS]
        embeddings = embedding_model.encode(texts_to_embed, show_progress_bar=True).tolist()
        print("Documents embedded successfully.")
    except Exception as e:
        print(f"ERROR: Failed to embed documents: {e}")
        return

    doc_ids = [doc['id'] for doc in KNOWLEDGE_BASE_DOCUMENTS]
    doc_metadatas = [doc['metadata'] for doc in KNOWLEDGE_BASE_DOCUMENTS]
    doc_contents = [doc['text'] for doc in KNOWLEDGE_BASE_DOCUMENTS]

    print(f"\nAdding {len(doc_ids)} documents to collection '{COLLECTION_NAME}'...")
    try:
        collection.add(
            embeddings=embeddings,
            documents=doc_contents,
            metadatas=doc_metadatas,
            ids=doc_ids
        )
        print("SUCCESS: Documents added to ChromaDB successfully!")
        print(f"New collection count: {collection.count()}")
    except Exception as e:
        print(f"ERROR: Failed to add documents to ChromaDB: {e}")

if __name__ == "__main__":
    print("--- Starting Knowledge Base Population Script ---")
    initialize_and_populate_vectordb()
    print("\n--- Knowledge Base Population Script Finished ---")