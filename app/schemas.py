from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone

#schema for creating an expense in JSON

class ExpenseCreate(BaseModel):
    #rules for the BaselModel
    amount: float
    currency: str = "USD"
    category: str = "uncategorized"
    description: str | None=None
    occurred_at: Optional[datetime] = None

#Schema for reading an expense back from DB
#output for when expense is created, it returns the id
class ExpenseRead(ExpenseCreate):
    id: int
    created_at : datetime

#for the Config class we specify true do we dont need to use dictionary notation
    class Config:
        orm_mode = True  #forSQlAmchtm  to access dictionary attributs instead of keys
#####################################################################
#ORM relationships: lets Python code easily navigate linked tables.
class UserCreate(BaseModel):
    username: str
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    expenses: Optional[List[ExpenseRead]] = [] #return nested expenses

    class Config:
        orm_mode = True