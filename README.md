# AJ-AI-Tutor
.\venv_3.13\Scripts\Activate
### To Run the FastAPI Backend 
`uvicorn app.main:app --reload`

### to run the Frontend
npm run dev

## to run postgresql scripts 
python -m app.scripts.create_tables
python -m app.scripts.test_db

# Build and start both containers 
docker compose up --build
docker compose build --no-cache

docker compose up

docker exec -it tutor-db psql -U postgres -d AJDB
CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE chat (
    id SERIAL PRIMARY KEY,
    chat_session_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    query VARCHAR NOT NULL,
    answer VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);
\dt
\q
docker compose up