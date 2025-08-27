from pydantic import BaseModel,Field,EmailStr
from typing import Annotated

class user_base(BaseModel):
    name:Annotated[str,Field(min_length=2,max_length=60)]
    email:EmailStr
    
class user_create(user_base):
    pass
class habit_base(BaseModel):
    name:Annotated[str,Field(min_length=2,max_length=60)]
    last_mark:str
    streak:int
class habit_create(habit_base):
    ...
    