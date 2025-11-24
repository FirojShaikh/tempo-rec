import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

from session_manager import load_session

from components import gradient_header

with st.container():
    gradient_header("Analytics Dashboard", "This dashboard summarizes **dataset statistics** and **user session behavior** "
    "to help explain how TempoRec makes recommendations.", page_id="analytics")

if not st.session_state.get("is_authenticated"):
    st.warning("Please log in to view Analytics.")
    st.stop()

if st.session_state.get("role") == "guest":
    st.warning("Login required to view Analytics.")
    st.stop()

# ---------------------------------------------------------
# 1. Determine current user (simple placeholder for now)
# ---------------------------------------------------------
user = st.session_state.get("username", "guest")
st.caption(f"Current user: `{user}`")


# ---------------------------------------------------------
# 2. Load dataset (cached)
# ---------------------------------------------------------
@st.cache_data
def load_dataset():
    df = pd.read_csv("data/online_retail_cleaned_dataset.csv")
    df.dropna(subset=["Description"], inplace=True)
    df.drop_duplicates(subset=["StockCode", "Description"], inplace=True)
    df["Description"] = df["Description"].str.strip().str.lower()
    return df


df = load_dataset()


# ---------------------------------------------------------
# 3. Dataset-level analytics
# ---------------------------------------------------------
st.markdown("## Dataset Overview")

num_products = len(df)
num_stockcodes = df["StockCode"].nunique()
avg_desc_len = df["Description"].str.len().mean()

col1, col2, col3 = st.columns(3)
col1.metric("Unique Products", f"{num_products:,}")
col2.metric("Unique StockCodes", f"{num_stockcodes:,}")
col3.metric("Avg. Description Length", f"{avg_desc_len:.1f} chars")

# Description length distribution
st.markdown("### Description Length Distribution")

desc_lengths = df["Description"].str.len()
length_bins = pd.cut(desc_lengths, bins=[0, 20, 40, 60, 80, 100, 200, 500])
length_counts = length_bins.value_counts().sort_index()
length_df = pd.DataFrame({"length_range": length_counts.index.astype(str), "count": length_counts.values})
length_df = length_df.set_index("length_range")

st.bar_chart(length_df)

with st.expander("Sample of dataset rows"):
    st.dataframe(df.head(20))


# ---------------------------------------------------------
# 4. User session analytics
# ---------------------------------------------------------
st.markdown("---")
st.markdown("## User Session Analytics")

events = load_session(user)

if not events:
    st.info(
        "No session events found for this user yet. "
        "Visit the **User Session** page to add some interests or viewed products."
    )
else:
    # Convert to DataFrame for easier analysis
    events_df = pd.DataFrame(events)

    # Parse timestamps
    events_df["timestamp_dt"] = pd.to_datetime(events_df["timestamp"], errors="coerce")

    event_count = len(events_df)
    event_types = events_df["type"].value_counts()
    unique_values = events_df["value"].nunique()
    last_event_time = events_df["timestamp_dt"].max()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Events", event_count)
    c2.metric("Event Types", event_types.shape[0])
    c3.metric("Unique Values", unique_values)
    if pd.notnull(last_event_time):
        c4.metric("Last Activity", last_event_time.strftime("%Y-%m-%d %H:%M:%S"))
    else:
        c4.metric("Last Activity", "N/A")

    # ---- Events by type ----
    st.markdown("### Events by Type")
    event_type_df = event_types.rename_axis("event_type").reset_index(name="count")
    st.bar_chart(event_type_df.set_index("event_type"))

    # ---- Timeline of events ----
    st.markdown("### Event Timeline")

    # Group by minute for a simple time series
    if events_df["timestamp_dt"].notna().any():
        timeline_df = (
            events_df
            .set_index("timestamp_dt")
            .resample("1T")
            .size()
            .rename("event_count")
            .to_frame()
        )
        st.line_chart(timeline_df)
    else:
        st.write("No valid timestamps available to build a timeline.")

    # ---- Top values / interests ----
    st.markdown("### Top Interests / Values")

    top_values = events_df["value"].value_counts().head(10)
    top_values_df = top_values.rename_axis("value").reset_index(name="count")
    st.table(top_values_df)

    # ---- Raw event log (for debugging) ----
    with st.expander("Raw Session Events"):
        st.dataframe(events_df[["timestamp", "type", "value"]])