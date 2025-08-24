
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth_routes, results_routes, users_routes

# Load environment variables
load_dotenv()

# Get configuration from environment
API_TITLE = os.getenv("API_TITLE")
API_ROOT_PATH = os.getenv("API_ROOT_PATH")
API_VERSION = os.getenv("API_VERSION")
CORS_ALLOW_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS")
CORS_ALLOW_METHODS = os.getenv("CORS_ALLOW_METHODS")
CORS_ALLOW_HEADERS = os.getenv("CORS_ALLOW_HEADERS")

app = FastAPI(title=API_TITLE, root_path=API_ROOT_PATH, version=API_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ALLOW_ORIGINS],
    allow_credentials=True,
    allow_methods=[CORS_ALLOW_METHODS],
    allow_headers=[CORS_ALLOW_HEADERS],
)

app.include_router(users_routes.router)
app.include_router(results_routes.router)
app.include_router(auth_routes.router)



