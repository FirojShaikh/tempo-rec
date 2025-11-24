## Pinecone Configuration (Phase 1, Step 1)
- Using Pinecone Serverless index: temprec-index
- Embedding dimension: 384 (MiniLM L6 v2)
- Environment variables set via .env and shell profile
- API key secured and excluded from Git
- Will be used in vector_store.py and recommendation_app.py

### `.env` file placehoder values
```
PINECONE_API_KEY=YOUR_API_KEY_HERE
PINECONE_INDEX_NAME=temprec-index
PINECONE_ENVIRONMENT=us-east-1
```
## Phase 1 Step 2 — Pinecone Vector Store Design

Embedding Model:
- all-MiniLM-L6-v2, dim=384

Index:
- Name: temprec-index
- Metric: cosine
- Cloud: AWS
- Region: us-east-1

Metadata per vector:
- description: cleaned product description
- stockcode: SKU code
- (future) category, unitprice, etc.

Vector IDs:
- "prod-<i>"

Batch Strategy:
- 200 vectors per upsert call

Rebuild Strategy:
- Create index if missing
- Admin trigger for full rebuild (Phase 6)

## Phase 1 Step 3 — vector_store.py blueprint

Functions:
- load_data()
- init_pinecone()
- create_index_if_needed()
- embed_products()
- upsert_vectors()
- rebuild_index()

Data flow:
CSV -> cleaned DataFrame -> embeddings -> Pinecone index

Vector ID: prod-<i>
Batch size: 200
Metadata: description, stockcode
Embedding model: all-MiniLM-L6-v2 (384 dims)

Index behavior: Create if missing, else reuse.

Will become the foundation for Admin panel & AWS Lambda rebuild.

## Phase 1 Step 5 — Recommendation Query Module Design

Purpose:
- Clean separation of Pinecone search logic
- Reusable across UI pages and future backend API

Functions:
- load_model()
- load_pinecone_index()
- embed_query()
- search_vectors()
- recommend()

Input:
- text query
Output:
- list of matches with: score, description, stockcode

Will later support:
- personalized recommendations from user embedding
- admin test queries
- AWS Lambda backend

## Phase 2 Step 1 — Multi-Page Streamlit App Design

Pages:
1. Home – overview + architecture + navigation
2. Explore – browse dataset (search, filter)
3. Recommendations – Pinecone-based search
4. User Session – temporal recommendations
5. Analytics – charts + insights
6. Admin – rebuild index + system health

Support modules:
- recommender.py
- session_manager.py
- auth.py (Phase 3)

Folder structure finalized under src/pages/

Navigation uses native Streamlit multipage layout.

## Phase 2 Step 2 — Multi-Page Skeleton Created
- Created src/app.py as main entry
- Added src/pages directory
- Added 6 screen templates:
  - Home
  - Explore Products
  - Recommendations
  - User Session
  - Analytics
  - Admin
- Verified navigation works via Streamlit multipage feature

## Phase 2 Step 3 — Product Explorer Implemented
- Added search bar for product descriptions
- Implemented pagination and sidebar filters
- Displays product description, StockCode, price, country
- Useful for testing and previewing the dataset
- This page will later allow users to add events into their session

## Phase 2 Step 4 — Recommendation Screen Implemented
- Added custom and dropdown search inputs
- Integrated recommender.py (Pinecone vector search)
- Displayed item descriptions, scores, stockcode
- First fully intelligent UI screen

## Phase 2 Step 5 — Temporal Session Page Design

User Session Page Responsibilities:
- Display session events (view, search, click)
- Allow adding simulated interactions
- Store events in session_data/<username>.json
- Compute temporal embedding using weighted formula:
    0.7 * last + 0.2 * second_last + 0.1 * historical average
- Use recommend_from_embedding() for personalized recommendations
- Clear session for demo reset

Modules:
- session_manager.py (load, save, embed, clear)
- recommender.py (pinecone search)

## Phase 2 Step 6 — Temporal Session Implementation

- Added session_manager.py to store user events in session_data/<user>.json
- Implemented User Session page:
  - Shows chronological session events
  - Allows adding typed interests and viewed products
  - Clears session on demand
- Implemented temporal embedding:
  - If 1 event → use its embedding
  - If 2 events → 0.7 * last + 0.3 * second_last
  - If ≥3 events → 0.7 * last + 0.2 * second_last + 0.1 * mean(older)
- Used recommend_from_embedding() to get personalized Pinecone recommendations
- Displays recent interests considered for explainability

## Phase 2 Step 6 — Temporal Session Implementation

- Added session_manager.py to store user events in session_data/<user>.json
- Implemented User Session page:
  - Shows chronological session events
  - Allows adding typed interests and viewed products
  - Clears session on demand
- Implemented temporal embedding:
  - If 1 event → use its embedding
  - If 2 events → 0.7 * last + 0.3 * second_last
  - If ≥3 events → 0.7 * last + 0.2 * second_last + 0.1 * mean(older)
- Used recommend_from_embedding() to get personalized Pinecone recommendations
- Displays recent interests considered for explainability

## Phase 2 Step 7 — Analytics Dashboard Design

Sections:
1. Dataset Metrics:
   - num_products
   - description length hist
   - previews

2. Session Metrics:
   - event_count
   - count by type
   - top keywords
   - timeline of events

Visualizations:
- Histogram (description length)
- Bar chart (event types)
- Line/Timeline chart (event timestamps)

Dependencies:
- session_manager.py
- dataset CSV

Purpose:
- Provide insights into user behavior
- Explain temporal recommendations
- Support admin and demo storytelling


## Phase 3 — Auth & Role-Based Access Design

- Users stored in config/users.json with:
  - username
  - password (plain for demo)
  - role: admin | user
- Auth module (auth.py):
  - load_users()
  - authenticate(username, password)
  - set_logged_in_user(username, role)
  - logout()
  - get_current_user()

Session state keys:
- is_authenticated: bool
- username: str
- role: str (admin | user | guest)

Access rules:
- Home, Explore: open to all
- Recommendations, User Session, Analytics: require login
- Admin Panel: admin only

Login UI:
- Implemented in app.py
- Simple form (username + password)
- Logout button when authenticated

## Phase 3 Step 2 — Auth Implementation Completed
- Added config/users.json for credentials
- Added authentication helper module auth.py
- Added login/logout UI inside app.py
- Added role protection for pages
- Admin Panel now admin-only
- User Session, Recommendations, Analytics now require login
- Session state tracks is_authenticated, username, role
