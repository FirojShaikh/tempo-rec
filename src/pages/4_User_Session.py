import streamlit as st
import pandas as pd
import numpy as np

from session_manager import (
    load_session,
    add_event,
    clear_session,
    get_recent_events,
)
from recommender import load_model, recommend_from_embedding
from components import gradient_header

with st.container():
    gradient_header("User Session - Temporal Recommendations", "This page simulates a user's browsing behavior and generates **personalized "
    "recommendations** based on recent activity using temporal weighting.", page_id="session")

if not st.session_state.get("is_authenticated"):
    st.warning("Please log in to use the User Session feature.")
    st.stop()

if st.session_state.get("role") == "guest":
    st.warning("Login required to access User Session features.")
    st.stop()

# ---------------------------------------------------------
# 1. Determine current user (simple placeholder for now)
#    Later this can be wired to real auth.
# ---------------------------------------------------------
user = st.session_state.get("username", "guest")


# ---------------------------------------------------------
# 2. Load dataset for sample items
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
# 3. Helper to compute temporal user embedding
# ---------------------------------------------------------
def compute_user_embedding(events, model):
    """
    Compute a user embedding from session events with temporal weights:

    embedding =
        0.7 * last_event +
        0.2 * second_last_event +
        0.1 * mean(older_events)
    """
    if not events:
        return None

    texts = [e["value"] for e in events if e.get("value")]
    if not texts:
        return None

    # Encode all event texts at once
    embeddings = model.encode(texts)
    embeddings = np.array(embeddings)

    n = len(embeddings)
    if n == 1:
        # Only one event – just use that
        return embeddings[-1]

    if n == 2:
        last = embeddings[-1]
        second_last = embeddings[-2]
        return 0.7 * last + 0.3 * second_last

    # n >= 3
    last = embeddings[-1]
    second_last = embeddings[-2]
    older = embeddings[:-2]
    older_mean = older.mean(axis=0)

    user_embedding = 0.7 * last + 0.2 * second_last + 0.1 * older_mean
    return user_embedding


# ---------------------------------------------------------
# 4. Display session history
# ---------------------------------------------------------
st.subheader(f"Session Activity for user: `{user}`")

events = get_recent_events(user, limit=50)

if not events:
    st.info("No events yet. Add some interests or product views below to build a session.")
else:
    for e in reversed(events):  # show newest first
        st.markdown(
            f"- **{e['type']}** – `{e['value']}` _(at {e['timestamp']})_"
        )


# ---------------------------------------------------------
# 5. Controls to add events to the session
# ---------------------------------------------------------
st.markdown("---")
st.subheader("Add Activity to Session")

col1, col2 = st.columns(2)

with col1:
    text_interest = st.text_input(
        "Type an interest or product you viewed:",
        placeholder="e.g., red mug, christmas candle, gift bag",
    )
    if st.button("Add typed interest to session"):
        if not text_interest.strip():
            st.error("Please type something before adding.")
        else:
            add_event(user, "typed_interest", text_interest)
            st.success(f"Added interest: `{text_interest}` to session.")
            st.rerun()

with col2:
    selected_product = st.selectbox(
        "Pick a product to add as a 'viewed' event:",
        sample_products[:300],
    )
    if st.button("Add selected product to session"):
        add_event(user, "view_product", selected_product)
        st.success(f"Added viewed product: `{selected_product}` to session.")
        st.rerun()

# Clear session button
if st.button("Clear Session"):
    clear_session(user)
    st.success("Session cleared.")
    st.rerun()


# ---------------------------------------------------------
# 6. Personalized recommendations based on session
# ---------------------------------------------------------
st.markdown("---")
st.subheader("Personalized Recommendations from Session")

events = load_session(user)
if not events:
    st.info("No events in session. Add some interests or views above first.")
else:
    model = load_model()
    user_embedding = compute_user_embedding(events, model)

    if user_embedding is None:
        st.warning("Could not compute a user embedding from current events.")
    else:
        st.write(
            "These recommendations are based on your **recent activity**, "
            "with more recent actions weighted more heavily."
        )

        with st.spinner("Computing personalized recommendations..."):
            recs = recommend_from_embedding(user_embedding, top_k=5)

        # Show last few distinct event values as context
        unique_recent_values = []
        for e in reversed(events):
            v = e.get("value")
            if v and v not in unique_recent_values:
                unique_recent_values.append(v)
            if len(unique_recent_values) >= 3:
                break

        if unique_recent_values:
            st.markdown(
                f"**Recent interests considered:** "
                + ", ".join(f"`{v}`" for v in unique_recent_values)
            )

        st.markdown("### Recommended for you:")

        for item in recs:
            st.markdown(
                f"""
                **{item['description']}**  
                - Score: `{item['score']:.4f}`  
                - StockCode: `{item['stockcode']}`
                """
            )
            st.markdown("---")
