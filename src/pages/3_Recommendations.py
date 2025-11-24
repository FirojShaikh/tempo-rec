import streamlit as st
import pandas as pd
from recommender import recommend
import streamlit as st
from components import gradient_header

with st.container():
    gradient_header("Recommendations", "Get real-time product recommendations using Pinecone vector search.", page_id="recs")

if not st.session_state.get("is_authenticated"):
    st.warning("Please log in to use the Recommendations feature.")
    st.stop()

if st.session_state.get("role") == "guest":
    st.warning("Login required to access Recommendations.")
    st.stop()

# ---------------------------------------------------------
# 1. Load dataset for sample dropdown
# ---------------------------------------------------------
@st.cache_data
def load_sample_products():
    df = pd.read_csv("data/online_retail_cleaned_dataset.csv")
    df.dropna(subset=["Description"], inplace=True)
    df.drop_duplicates(subset=["StockCode", "Description"], inplace=True)
    df["Description"] = df["Description"].str.strip().str.lower()
    return sorted(df["Description"].unique().tolist())

sample_products = load_sample_products()


# ---------------------------------------------------------
# 2. UI Inputs
# ---------------------------------------------------------
st.subheader("Enter a product or choose one from the list")

col1, col2 = st.columns(2)

with col1:
    custom_query = st.text_input("Type your own query", placeholder="e.g., red mug, glass bottle, gift bag")

with col2:
    selected_query = st.selectbox("Or pick a product", sample_products[:300])

# Which query to use?
query = custom_query if custom_query.strip() else selected_query


# ---------------------------------------------------------
# 3. Get Recommendations
# ---------------------------------------------------------
if st.button("Get Recommendations"):
    if not query or len(query.strip()) == 0:
        st.error("Please enter a query or select a product.")
    else:
        st.info(f"Searching for items similar to: **{query}**")

        with st.spinner("Finding matches using Pinecone..."):
            results = recommend(query, top_k=5)

        st.subheader("Top Recommendations")

        for item in results:
            st.markdown(f"""
            **{item['description']}**  
            - Score: `{item['score']:.4f}`  
            - StockCode: `{item['stockcode']}`
            """)
            st.markdown("---")
