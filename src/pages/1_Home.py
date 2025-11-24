import streamlit as st
from components import gradient_header

with st.container():
    gradient_header("Home", "Welcome to TempoRec", page_id="home")

username = st.session_state.get("username", "guest")
role = st.session_state.get("role", "guest")

# Personalized greeting
if role == "admin":
    st.markdown(f"### Welcome back, **{username.capitalize()}** (Admin)")
elif role == "user":
    st.markdown(f"### Welcome, **{username.capitalize()}**")
else:
    st.markdown("### Welcome to TempoRec")

st.write(
    """
    TempoRec is a personalized retail recommendation system built using:
    - Pinecone Vector Search  
    - Sentence Transformers  
    - Streamlit Multi-Page UI  
    - Temporal User Behavior Modeling  
    - Role-Based Access Control  
    """
)

st.markdown("---")

st.subheader("What you can do here:")

st.markdown(
    """
    - **Explore Products** – browse the dataset  
    - **Get Recommendations** – find similar items using embeddings  
    - **User Session** – generate personalized temporal recommendations  
    - **Analytics Dashboard** – understand recommendation patterns  
    - **Admin Panel** – system tools and vector index controls  
    """
)
