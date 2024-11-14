"""schemas/estimation.py"""

from pydantic import BaseModel, field_validator


class EstimationInput(BaseModel):
    """Estimation input schema"""

    method: str
    plant_type: str
    equipment: str
    equipment_type: str
    sizing_value: float

    @field_validator("method")
    @classmethod
    def method_validate(cls, v):
        if not v:
            raise ValueError("Method must be selected.")
        return v

    @field_validator("plant_type")
    @classmethod
    def plant_type_must_not_be_empty(cls, v):
        if not v:
            raise ValueError("Plant type must be selected.")
        return v

    @field_validator("equipment")
    @classmethod
    def equipment_validate(cls, v):
        if not v:
            raise ValueError("Equipment must be selected.")
        return v

    @field_validator("equipment_type")
    @classmethod
    def equipment_type_validate(cls, v):
        if not v:
            raise ValueError("Equipment type must be selected.")
        return v

    @field_validator("sizing_value")
    @classmethod
    def sizing_validate(cls, v):
        if v is None or v <= 0:
            raise ValueError("Sizing quantity must be a positive number.")
        return v
