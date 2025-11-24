import streamlit as st
import pandas as pd

from components import gradient_header

with st.container():
    gradient_header("Explore Products", "Search and explore products from the retail dataset.", page_id="explore")

# -------------------------------
# 1. Load dataset (cached)
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/online_retail_cleaned_dataset.csv")
    df.dropna(subset=["Description"], inplace=True)
    df.drop_duplicates(subset=["StockCode", "Description"], inplace=True)
    df["Description"] = df["Description"].str.strip().str.lower()
    return df

df = load_data()


# -------------------------------
# 2. Sidebar filters
# -------------------------------
st.sidebar.subheader("Filters")

search_text = st.sidebar.text_input("Search description:", "")

# Number of items per page
items_per_page = st.sidebar.slider("Items per page", 5, 50, 10)


# -------------------------------
# 3. Filter dataset
# -------------------------------
if search_text:
    filtered_df = df[df["Description"].str.contains(search_text.lower())]
else:
    filtered_df = df

total_items = len(filtered_df)

st.write(f"### Found {total_items} matching products")


# -------------------------------
# 4. Pagination logic
# -------------------------------
if total_items == 0:
    st.warning("No products match your search.")
else:
    total_pages = max(1, (total_items // items_per_page) + 1)

    page = st.number_input("Page", min_value=1, max_value=total_pages, step=1)

    start = (page - 1) * items_per_page
    end = start + items_per_page
    page_df = filtered_df.iloc[start:end]

    st.write(f"Showing items {start + 1} to {min(end, total_items)} of {total_items}")

    # -------------------------------
    # 5. Display products
    # -------------------------------
    for idx, row in page_df.iterrows():
        st.markdown(f"""
        **{row['Description']}**  
        - StockCode: `{row['StockCode']}`  
        - UnitPrice: `{row.get('UnitPrice', 'N/A')}`  
        - Country: `{row.get('Country', 'N/A')}`
        """)
        st.markdown("---")
