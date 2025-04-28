from fastapi import FastAPI, Depends

from drivers.routers import auth, users
from drivers.dependencies import get_token_header

app = FastAPI(title="Savibud API")

app.include_router(auth.router)
app.include_router(users.router, dependencies=[Depends(get_token_header)])
