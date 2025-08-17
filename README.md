# AJ-AI-Tutor
.\venv_3.13\Scripts\Activate
### To Run the FastAPI Backend 
`uvicorn app.main:app --reload`

### to run the Frontend
npm run dev

## to run postgresql scripts 
python -m app.scripts.create_tables
python -m app.scripts.test_db

# Build and start both containers  - note for AJ - to try and automate the table creation into the container the next time.
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


# to share the conatiner with someone
docker push yourusername/ai-tutor:latest
docker login

docker pull yourusername/ai-tutor:latest
create docker-compose.yml (insert the code)
provide .env
docker compose up


# new
docker tag ai-tutor-backend:latest ancy0501/ai-tutor:latest
docker login
docker push ancy0501/ai-tutor:latest

# provide a smimple `docker-compose.yml` to the tester
# provide `.env`

docker pull ancy0501/ai-tutor:latest
docker compose up