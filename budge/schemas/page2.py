from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Literal
import uuid


class TableRecord(BaseModel):
    table_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: Literal["A", "B", "C"]
    x: int
    y: float


class Page2Input(BaseModel):
    table: List[TableRecord] = Field(default_factory=list)


def generate_table_record() -> Dict:
    return TableRecord(category="A", x=0, y=0.0).model_dump()
