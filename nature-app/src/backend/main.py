
from fastapi import FastAPI
from routes import layers_routers, results_routes, token_routes, users_routes

app = FastAPI(title="Nature Assessment Tool API", root_path="/api/v1", version="0.1.0")

app.include_router(users_routes.router)
app.include_router(layers_routers.router)
app.include_router(results_routes.router)
app.include_router(token_routes.router)



