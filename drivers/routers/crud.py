import json
from enum import Enum
from typing import Annotated

from fastapi import APIRouter
from pydantic import AfterValidator

from drivers.dependencies import get_adapter_repository
from drivers.validators.json_validator import check_valid_dict_str

router = APIRouter(prefix="/crud")


class Tables(Enum):
    """List of table mapping keys"""

    USER = "user"


@router.get("/{table}")
def read(
    table: Tables, filters: Annotated[str, AfterValidator(check_valid_dict_str)] = "{}"
):
    """Retrieve all elements for requested table"""
    table_class = get_adapter_repository(table.value)
    return table_class().read(**json.loads(filters)) if table_class else None


@router.post("/{table}")
def create(table: Tables, item: dict):
    """Create new element"""
    table_class = get_adapter_repository(table.value)
    return table_class().create(**item) if table_class else None


@router.put("/{table}/{item_id}")
def update(table: Tables, item_id: str, item: dict):
    """Update specific element from table"""
    table_class = get_adapter_repository(table.value)
    return table_class().update(item_id, item) if table_class else None


@router.delete("/{table}/{item_id}")
def delete(table: Tables, item_id: str):
    """Delete specific element from table"""
    table_class = get_adapter_repository(table.value)
    return table_class().delete(item_id) if table_class else None
