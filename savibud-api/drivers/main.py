from fastapi import Depends, FastAPI

from drivers.database import init_db
from drivers.dependencies import get_token_header
from drivers.routers import auth, dashboard, powens, transactions, users, categories, budgets

app = FastAPI(title="Savibud API")

init_db()

app.include_router(auth.router, tags=["auth"])
app.include_router(
    users.router, dependencies=[Depends(get_token_header)], tags=["user"]
)
app.include_router(
    powens.router, dependencies=[Depends(get_token_header)], tags=["powens"]
)
app.include_router(
    transactions.router, dependencies=[Depends(get_token_header)], tags=["transactions"]
)
app.include_router(
    transactions.acc_router, dependencies=[Depends(get_token_header)], tags=["accounts"]
)
app.include_router(
    categories.router, dependencies=[Depends(get_token_header)], tags=["categories"]
)
app.include_router(
    budgets.router, dependencies=[Depends(get_token_header)], tags=["budgets"]
)
app.include_router(
    dashboard.router, dependencies=[Depends(get_token_header)], tags=["dashboard"]
)
