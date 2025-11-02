# 🧠 TempoRec: Real-time Recommendation Engine using Temporal Vector Search

TempoRec is a lightweight proof-of-concept system that delivers **real-time, context-aware product recommendations** for e-commerce platforms.  
It uses **vector similarity search (ChromaDB)** and **sentence embeddings (SentenceTransformers)** to find semantically similar items based on a product or category query.

---

## 🚀 Features
- Real-time, vector-based product recommendations  
- Semantic search using SentenceTransformers  
- Vector storage and retrieval with ChromaDB  
- Modular, clean Python backend  
- Streamlit interface (coming in Day 3)  

---

## 🗂️ Project Structure
tempo-rec/
├── data/
│ └── online_retail_cleaned_dataset.csv
├── src/
│ ├── data_preparation.py # cleans and prepares data
│ ├── vector_store.py # builds embeddings + vector search
│ └── recommendation_app.py # (to be added) Streamlit UI
├── requirements.txt
├── README.md
└── .gitignore

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/tempo-rec.git
cd tempo-rec
```
### 2️⃣ Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```
### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

## 🧩 Usage
### 🧠 Data Preparation
```bash
python src/data_preparation.py
```
Cleans and normalizes the dataset by removing duplicates and missing descriptions.

### 🔢 Build Vector Store
```bash
python src/vector_store.py
```
Generates sentence embeddings for product descriptions and stores them in a Chroma collection.

### Example Output
```bash
🔄 Generating embeddings...
✅ Stored 40900 product embeddings in Chroma
🔍 Query: red mug
Top Results:
- red ceramic coffee mug
- red heart-shaped mug
- white and red polka dot cup
```

## 📅 Project Progress
Day	Focus	Status
Day 1	Environment setup & GitHub initialization	✅ Completed
Day 2	Data cleaning, embeddings, and Chroma integration	✅ Completed
Day 3	Streamlit UI for real-time recommendations	🔜 Pending

## 🧠 Next Step

Implement recommendation_app.py using Streamlit

Build a dropdown-based UI to browse categories and display recommendations

Integrate with Chroma to fetch top-N similar items dynamically
