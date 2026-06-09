import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent

# --- LLM ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = "llama-3.3-70b-versatile"

# --- Embeddings ---
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# --- Vector store ---
CHROMA_COLLECTION = "unofficial-guide-chunks"
CHROMA_PATH = str(PROJECT_ROOT / "chroma_db")

# --- Retrieval ---
N_RESULTS = 5

# --- Documents ---
DOCS_PATH = str(PROJECT_ROOT / "documents" / "ucla-dining-hall" / "ucla-cld")
