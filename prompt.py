
page1_input = {
    "numbers_operands": "two",
    "operation": "addition",
    "a": 1,
    "b": 2,
    "c": 3,
}

make a pydantic schema. for the above using the following rules:
    
    - The schema should be named Page1Input
    - The schema should have a property numbers_operands of type str. this can take the values "two" or "three"
    - The schema should have a property operation of type str. this can take the values "addition" and  "multiplication"
    - The schema should have a property a of type float (always required)
    - The schema should have a property b of type float (always required)
    - The schema should have a property c of type float (always required if numbers_operands is "three" otherwise optional)

# make schema
class Page1Input(BaseModel):
    numbers_operands: str
    operation: str
    a: float
    b: float
    c: Optional[float] = None

