
from deps import get_current_user
from fastapi import FastAPI
from routes import auth_routes, layers_routers, results_routes, users_routes

app = FastAPI(title="Nature Assessment Tool API", root_path="/api/v1", version="0.1.0")

app.include_router(users_routes.router, dependencies=get_current_user)
app.include_router(layers_routers.router)
app.include_router(results_routes.router)
app.include_router(auth_routes.router)



