import streamlit as st
from sentence_transformers import SentenceTransformer
import chromadb
import chromadb.config
import pandas as pd

# --- Cached setup functions ---
@st.cache_data
def load_data():
    df = pd.read_csv("data/online_retail_cleaned_dataset.csv")
    df.dropna(subset=["Description"], inplace=True)
    df.drop_duplicates(subset=["StockCode", "Description"], inplace=True)
    df["Description"] = df["Description"].str.strip().str.lower()
    return df

@st.cache_resource
def get_chroma_collection():
    client = chromadb.Client(settings=chromadb.config.Settings(persist_directory="chroma_data"))
    return client.get_or_create_collection("products_collection")

@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

# --- Recommendation logic ---
def get_recommendations(query, model, collection, n_results=5):
    results = collection.query(query_texts=[query], n_results=n_results)
    return results["documents"][0]

# --- Streamlit UI ---
st.set_page_config(page_title="TempoRec", page_icon="🧠")
st.title("🧠 TempoRec – Real-Time Product Recommendations")
st.markdown("Select or enter a product/category keyword to see similar recommendations.")

df = load_data()
model = load_model()
collection = get_chroma_collection()

# Dropdown + text input
sample_items = sorted(df["Description"].dropna().sample(50).unique())
query = st.selectbox("Choose a product or type a keyword:", sample_items)

if st.button("Get Recommendations"):
    with st.spinner("Finding similar items..."):
        recs = get_recommendations(query, model, collection)
        st.subheader("🔍 Recommended Products:")
        for i, item in enumerate(recs, start=1):
            st.write(f"{i}. {item}")
