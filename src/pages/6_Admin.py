import streamlit as st
import os
import json
import glob
import pandas as pd
from pathlib import Path

from dotenv import load_dotenv
from recommender import (
    load_model,
    load_pinecone_index,
    embed_query,
    search_vectors
)
from session_manager import load_session, clear_session
from vector_store import rebuild_index

import streamlit as st

from components import gradient_header

with st.container():
    gradient_header("Admin Panel", "Administrative controls for managing the TempoRec system.", page_id="admin")

if st.session_state.get("role") != "admin":
    st.error("⛔ Access denied. Admins only.")
    st.stop()

load_dotenv()

# -----------------------------------------------------
# Helper: Mask API Keys
# -----------------------------------------------------
def mask_value(v):
    if v is None:
        return "None"
    if len(v) < 4:
        return "***"
    return v[:3] + "****" + v[-3:]


# -----------------------------------------------------
# Section 1: Pinecone Operations
# -----------------------------------------------------
st.header("Pinecone Vector Index Management")

# --- Rebuild Index ---
if st.button("Rebuild Pinecone Vector Index"):
    st.warning("This may take several minutes. Please wait...")
    with st.spinner("Rebuilding index..."):
        try:
            rebuild_index()
            st.success("Vector index rebuild completed successfully!")
        except Exception as e:
            st.error(f"Rebuild failed: {e}")

# --- Show Index Stats ---
if st.button("Show Index Stats"):
    with st.spinner("Loading Pinecone index stats..."):
        try:
            index = load_pinecone_index()
            stats = index.describe_index_stats()
            st.json(stats)
        except Exception as e:
            st.error(f"Failed to load index stats: {e}")

# --- Test Query ---
st.subheader("Test a Query")
test_query = st.text_input("Enter a test query:", value="red mug")
if st.button("Run Test Query"):
    try:
        model = load_model()
        index = load_pinecone_index()
        vector = embed_query(test_query, model)
        matches = search_vectors(vector, index, top_k=5)

        st.write("### 🔍 Results")
        for m in matches:
            st.markdown(
                f"""
                **{m.metadata.get('description', '')}**  
                - Score: `{m.score:.4f}`  
                - StockCode: `{m.metadata.get('stockcode', '')}`
                """
            )
            st.markdown("---")
    except Exception as e:
        st.error(f"Query failed: {e}")


# -----------------------------------------------------
# Section 2: Session Management
# -----------------------------------------------------
st.header("User Session Management")

# --- Clear All Sessions ---
if st.button("Clear All Sessions"):
    try:
        for file in glob.glob("session_data/*.json"):
            os.remove(file)
        st.success("All user sessions cleared.")
    except Exception as e:
        st.error(f"Error clearing sessions: {e}")

# --- Inspect Sessions ---
session_files = glob.glob("session_data/*.json")
users = [Path(f).stem for f in session_files]

if users:
    st.subheader("Inspect a User Session")
    selected_user = st.selectbox("Select user:", users)

    session_events = load_session(selected_user)
    if not session_events:
        st.info("No session events found.")
    else:
        df = pd.DataFrame(session_events)
        st.write(f"### Session Events for `{selected_user}`")
        st.dataframe(df)

        if st.button(f"Clear {selected_user}'s session"):
            clear_session(selected_user)
            st.success(f"Cleared session for `{selected_user}`.")
            st.rerun()


# -----------------------------------------------------
# Section 3: System Health Check
# -----------------------------------------------------
st.header("System Health Check")

if st.button("Run Health Check"):
    results = {}

    # — Model health
    try:
        _ = load_model()
        results["Embedding Model"] = "✔ Loaded successfully"
    except Exception as e:
        results["Embedding Model"] = f"{e}"

    # — Pinecone connection
    try:
        index = load_pinecone_index()
        results["Pinecone Connection"] = "✔ Connected"
    except Exception as e:
        results["Pinecone Connection"] = f"{e}"

    # — Pinecone query test
    try:
        vector = [0] * 384  # dummy vector
        _ = index.query(vector=vector, top_k=1)
        results["Sample Query"] = "✔ Query executed"
    except Exception as e:
        results["Sample Query"] = f"{e}"

    st.write("### Health Check Results")
    st.json(results)


# -----------------------------------------------------
# Section 4: Environment Variables
# -----------------------------------------------------
st.header("Environment Info (Masked)")

env_info = {
    "PINECONE_INDEX_NAME": os.getenv("PINECONE_INDEX_NAME"),
    "PINECONE_ENVIRONMENT": os.getenv("PINECONE_ENVIRONMENT"),
    "PINECONE_API_KEY": mask_value(os.getenv("PINECONE_API_KEY")),
}

st.json(env_info)