import os
import sys
from logging.config import fileConfig

from sqlalchemy import MetaData, engine_from_config, pool
from sqlmodel import SQLModel

from alembic import context

# allow imports from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import settings and models so SQLModel.metadata is populated
from drivers.config import settings  # noqa: E402
from entities.account import Account, SnapshotAccount
from entities.budget import Budget
from entities.category import Category
from entities.powens import PowensConnection
from entities.saving import SavingsGoal, SavingsAutomation
from entities.transaction import Transaction
from entities.user import User

# this is the Alembic Config object, which provides access to the values within the .ini file
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# set SQLAlchemy URL from env var if present or from settings
db_url = settings.database_url
config.set_main_option("sqlalchemy.url", db_url)

# Provide SQLModel metadata with a naming convention
# This helps Alembic identify constraints properly in Postgres
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# Provide SQLModel metadata for 'autogenerate' support
target_metadata = SQLModel.metadata
target_metadata.naming_convention = naming_convention


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),  # type: ignore
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
