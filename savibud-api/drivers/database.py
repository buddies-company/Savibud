from typing import Generator

from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel, create_engine

from drivers.config import settings
from entities.account import Account, SnapshotAccount, ManualAccount
from entities.category import Category
from entities.powens import PowensConnection
from entities.rule import Rule
from entities.saving import SavingsGoal
from entities.transaction import Transaction
from entities.user import User

engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(
    class_=Session,
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    SQLModel.metadata.create_all(engine)
