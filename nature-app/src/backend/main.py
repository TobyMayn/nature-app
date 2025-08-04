
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth_routes, layers_routers, results_routes, users_routes

app = FastAPI(title="Nature Assessment Tool API", root_path="/api/v1", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_routes.router)
app.include_router(layers_routers.router)
app.include_router(results_routes.router)
app.include_router(auth_routes.router)



