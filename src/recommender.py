import os
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import streamlit as st


# ------------------------------------------------------------
# 1. Load environment + model (cached)
# ------------------------------------------------------------
@st.cache_resource
def load_model():
    """Load the embedding model only once."""
    load_dotenv()
    model = SentenceTransformer("all-MiniLM-L6-v2")
    return model


# ------------------------------------------------------------
# 2. Load Pinecone index (cached)
# ------------------------------------------------------------
@st.cache_resource
def load_pinecone_index():
    """Initialize Pinecone and return an index object."""
    load_dotenv()

    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME")

    if not api_key:
        raise ValueError("Missing PINECONE_API_KEY in environment variables or .env file")

    if not index_name:
        raise ValueError("Missing PINECONE_INDEX_NAME in environment variables or .env file")

    pc = Pinecone(api_key=api_key)

    try:
        index = pc.Index(index_name)
        return index
    except Exception as e:
        raise RuntimeError(
            f"Failed to load Pinecone index '{index_name}'. "
            f"Error: {str(e)}. Did you run vector_store.py to build the index?"
        )


# ------------------------------------------------------------
# 3. Embed query text
# ------------------------------------------------------------
def embed_query(text: str, model) -> list:
    """Convert text query into a 384-dim embedding."""
    if not text or len(text.strip()) == 0:
        raise ValueError("Query text cannot be empty")

    vector = model.encode([text]).tolist()[0]
    return vector


# ------------------------------------------------------------
# 4. Search Pinecone for similar items
# ------------------------------------------------------------
def search_vectors(vector: list, index, top_k: int = 5):
    """Query Pinecone index using the embedding."""
    try:
        results = index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True
        )
        return results.matches
    except Exception as e:
        raise RuntimeError(f"Pinecone query failed: {str(e)}")


# ------------------------------------------------------------
# 5. High-level recommendation function
# ------------------------------------------------------------
def recommend(query: str, top_k: int = 5):
    """
    Main entry point for Streamlit.
    Encodes text → queries Pinecone → returns structured results.
    """
    model = load_model()
    index = load_pinecone_index()

    vector = embed_query(query, model)
    matches = search_vectors(vector, index, top_k)

    # format the output
    formatted = []
    for m in matches:
        formatted.append({
            "score": m.score,
            "description": m.metadata.get("description", ""),
            "stockcode": m.metadata.get("stockcode", "")
        })

    return formatted


# ------------------------------------------------------------
# 6. Optional helper: recommend from user embedding
# ------------------------------------------------------------
def recommend_from_embedding(embedding: np.ndarray, top_k: int = 5):
    """
    Used later for temporal user-based recommendations.
    """
    index = load_pinecone_index()

    results = index.query(
        vector=embedding.tolist(),
        top_k=top_k,
        include_metadata=True
    )

    formatted = []
    for m in results.matches:
        formatted.append({
            "score": m.score,
            "description": m.metadata.get("description", ""),
            "stockcode": m.metadata.get("stockcode", "")
        })

    return formatted
