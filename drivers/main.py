from fastapi import Depends, FastAPI

from drivers.dependencies import get_token_header
from drivers.routers import auth, crud, users

app = FastAPI(title="Savibud API")

app.include_router(auth.router, tags=["auth"])
app.include_router(
    users.router, dependencies=[Depends(get_token_header)], tags=["user"]
)
app.include_router(crud.router, dependencies=[Depends(get_token_header)], tags=["CRUD"])
