from pydantic import BaseModel,Field,EmailStr
from typing import Annotated
from datetime import datetime

class user_base(BaseModel):
    name:Annotated[str,Field(min_length=2,max_length=60)]
    email:EmailStr
    
class user_create(user_base):
    pass
class habit_base(BaseModel):
    name:Annotated[str,Field(min_length=2,max_length=60)]
    owner_id:int 
class habit_create(habit_base):
    ...
    
class user(user_base):
    id:int
    
class habit(habit_base):
    id:int
    last_mark:datetime
    streak:int
    
class habit_mark(BaseModel):
    mark_habit:bool

class new_habit_name(BaseModel):
    new_name:Annotated[str,Field(min_length=2,max_length=60)]