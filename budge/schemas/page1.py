from pydantic import BaseModel, field_validator, model_validator
from typing import Optional


class Page1Input(BaseModel):
    numbers_operands: str
    operation: str
    a: float
    b: float
    c: Optional[float] = None

    @field_validator("numbers_operands")
    def validate_numbers_operands(cls, value):
        if value not in {"two", "three"}:
            raise ValueError('numbers_operands must be "two" or "three"')
        return value

    @field_validator("operation")
    def validate_operation(cls, value):
        if value not in {"addition", "multiplication"}:
            raise ValueError('operation must be "addition" or "multiplication"')
        return value

    @field_validator("a")
    def validate_a(cls, value):
        if value <= 5:
            raise ValueError("a must be greater than 5")
        return value

    @model_validator(mode="after")
    def validate_c(self):
        if self.numbers_operands == "three" and self.c is None:
            raise ValueError('c is required when numbers_operands is "three"')
        return self
