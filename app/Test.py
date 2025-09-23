from pydantic import BaseModel




class MyFirstModel(BaseModel):
    first_name: str
    last_name: str

validating = MyFirstModel(first_name=123, last_name="nealer")

