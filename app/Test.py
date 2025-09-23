from pydantic import BaseModel




class MyFirstModel(BaseModel):
    first_name: str
    last_name: str

validating = MyFirstModel(first_name=123, last_name="nealer")

#so this is a new feature I am adding and so I have written this code

print("this is a new feature for the branch")
