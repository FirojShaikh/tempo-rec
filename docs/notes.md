## Pinecone Configuration (Phase 1, Step 1)
- Using Pinecone Serverless index: temprec-index
- Embedding dimension: 384 (MiniLM L6 v2)
- Environment variables set via .env and shell profile
- API key secured and excluded from Git
- Will be used in vector_store.py and recommendation_app.py

## `.env` file placehoder values
```
PINECONE_API_KEY=YOUR_API_KEY_HERE
PINECONE_INDEX_NAME=temprec-index
PINECONE_ENVIRONMENT=us-east-1
```
