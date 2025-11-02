import chromadb
from sentence_transformers import SentenceTransformer
from data_preparation import load_and_clean_data

def create_vector_store(df):
    """
    Create a Chroma vector store from product descriptions.
    """
    # Initialize Chroma client and collection
    client = chromadb.Client()
    collection = client.get_or_create_collection(name="products_collection")

    # Load embedding model
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Prepare data
    descriptions = df["Description"].tolist()
    ids = [str(i) for i in range(len(descriptions))]

    print("🔄 Generating embeddings... (this may take 1–2 minutes)")
    embeddings = model.encode(descriptions)

    # Add to Chroma
    collection.add(
        ids=ids,
        documents=descriptions,
        embeddings=embeddings
    )
    print(f"✅ Stored {len(descriptions)} product embeddings in Chroma")

    return collection

def test_query(collection, query="red mug"):
    """
    Test similarity search for a given query.
    """
    results = collection.query(
        query_texts=[query],
        n_results=5
    )
    print("🔍 Query:", query)
    print("Top Results:")
    for doc in results["documents"][0]:
        print("-", doc)

if __name__ == "__main__":
    df = load_and_clean_data()
    collection = create_vector_store(df)
    #test_query(collection, "red mug")
    test_query(collection, "blue bag")
    #test_query(collection, "christmas candle")
    #test_query(collection, "glass bottle")

