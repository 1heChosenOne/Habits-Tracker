from engine import engine
from datetime import datetime
from sqlalchemy import text
from fastapi import HTTPException

def get_conn():
    with engine.begin() as conn:
            yield conn
            
def current_time():
    date=datetime.now().replace(microsecond=0)
    return date

def habit_id_validator(habit_id:int,conn):
    # max_id=conn.execute(text("SELECT MAX(id) FROM habits")).fetchone()[0]
    # if habit_id is None:
    #     raise HTTPException(status_code=404,detail=f"habit id not provided")
    # if habit_id > max_id or habit_id <=0:
    #     raise HTTPException(status_code=404,detail=f"habit with id {habit_id} not found")
    result=conn.execute(text("SELECT id FROM habits WHERE id=:id"),{"id":habit_id}).fetchone()
    if result is None:
        raise HTTPException(status_code=404,detail=f"Habit with id {habit_id} not found")
    pass
    
def user_id_validator(user_id:int,conn):
    result=conn.execute(text("SELECT id FROM users WHERE id=?"),(user_id,)).fetchone()
    if result is None:
        raise HTTPException(status_code=404,detail=f"User with id {user_id} not found")
    pass
        
    
    
    