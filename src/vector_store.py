import os
import time
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec


# -------------------------------
# 1. Load dataset
# -------------------------------
def load_data(path="data/online_retail_cleaned_dataset.csv"):
    df = pd.read_csv(path)

    # Clean text, remove duplicates
    df.dropna(subset=["Description"], inplace=True)
    df.drop_duplicates(subset=["StockCode", "Description"], inplace=True)
    df["Description"] = df["Description"].str.strip().str.lower()

    print(f"Loaded dataset with {len(df)} unique products")
    return df


# -------------------------------
# 2. Initialize Pinecone client
# -------------------------------
def init_pinecone():
    load_dotenv()  # Load .env file

    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME")
    environment = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")  # default

    if not api_key:
        raise ValueError("Missing PINECONE_API_KEY in .env file")

    pc = Pinecone(api_key=api_key)

    print(f"Connected to Pinecone environment: {environment}")
    return pc, index_name


# -------------------------------
# 3. Create index if needed
# -------------------------------
def create_index_if_needed(pc, index_name, dimension=384):
    existing = pc.list_indexes().names()

    if index_name not in existing:
        print(f"Creating new index '{index_name}'...")
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
    else:
        print(f"Index '{index_name}' already exists")

    index = pc.Index(index_name)
    return index


# -------------------------------
# 4. Embed all product descriptions
# -------------------------------
def embed_products(df, model_name="all-MiniLM-L6-v2"):
    print("Loading embedding model...")
    model = SentenceTransformer(model_name)

    descriptions = df["Description"].tolist()

    print(f"Generating embeddings for {len(descriptions)} products...")
    embeddings = model.encode(
        descriptions,
        batch_size=64,
        show_progress_bar=True
    )

    return embeddings, descriptions


# -------------------------------
# 5. Upload vectors to Pinecone
# -------------------------------
def upsert_vectors(index, df, embeddings, batch_size=200):
    print("Uploading vectors to Pinecone...")

    total = len(df)
    ids = [f"prod-{i}" for i in range(total)]

    # metadata
    metadatas = [
        {
            "description": df.iloc[i]["Description"],
            "stockcode": str(df.iloc[i]["StockCode"])
        }
        for i in range(total)
    ]

    # Batch upload
    for start in tqdm(range(0, total, batch_size)):
        end = min(start + batch_size, total)

        batch_ids = ids[start:end]
        batch_vectors = embeddings[start:end].tolist()
        batch_metadata = metadatas[start:end]

        vectors = [
            {
                "id": batch_ids[i - start],
                "values": batch_vectors[i - start],
                "metadata": batch_metadata[i - start],
            }
            for i in range(start, end)
        ]

        index.upsert(vectors=vectors)

    print(f"Upload complete: {total} vectors upserted.")


# -------------------------------
# 6. Orchestrator
# -------------------------------
def rebuild_index():
    start_time = time.time()

    df = load_data()
    pc, index_name = init_pinecone()
    index = create_index_if_needed(pc, index_name)

    embeddings, descriptions = embed_products(df)
    upsert_vectors(index, df, embeddings)

    print("Pinecone index build complete.")
    print(f"Total time: {round(time.time() - start_time, 2)} seconds")


# -------------------------------
# 7. Run directly
# -------------------------------
if __name__ == "__main__":
    rebuild_index()