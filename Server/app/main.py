from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from jose import jwt
from datetime import datetime, timedelta

app = FastAPI()

#Allow CORS for all origins (optional, but common for APIs)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[""],
    allow_credentials=True,
    allow_methods=[""],
    allow_headers=["*"],
)

#Dummy user table
users_db = {
    "testuser": {
        "username": "testuser",
        "password": "testpass"  # In production, use hashed passwords!
    }
}

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class LoginInput(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str



#Accept both form and JSON input for login
@app.post("/login", response_model=Token)
async def login(request: Request):
    if request.headers.get("content-type", "").startswith("application/json"):
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
    else:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
    user = users_db.get(username)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": user["username"], "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": encoded_jwt, "token_type": "bearer"}

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}