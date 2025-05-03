from fastapi import Depends, FastAPI

from drivers.dependencies import get_token_header
from drivers.routers import auth, users

app = FastAPI(title="Savibud API")

app.include_router(auth.router)
app.include_router(users.router, dependencies=[Depends(get_token_header)])
