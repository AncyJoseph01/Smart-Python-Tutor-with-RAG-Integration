from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import database
from app.api import auth, tutor
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

app = FastAPI(
    title="AI Tutor API",
    description="API Documentation for AI Tutor Application",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(tutor.router, prefix="/tutor", tags=["Tutor"])

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"message": "Oops! Invalid input.", "errors": exc.errors()}
    )


