from typing import List, Dict, Optional, Final
from pydantic import BaseModel, Field, field_validator, model_validator


class MetaInput(BaseModel):
    file_name: str
    client_name: Optional[str]
    project_name: Optional[str]
    project_description: Optional[str]
