from db import engine
from datetime import datetime
from sqlalchemy import text
from fastapi import HTTPException
       
def current_time():
    date=datetime.now().replace(microsecond=0)
    return date


def require_habit_row_exists(row,habit_id:int):
    if not row:
        raise HTTPException(status_code=404,detail=f"Habit with id {habit_id} not found")
    
    
def get_habit_or_404(habit_id:int,conn):
    row=conn.execute(text("SELECT * FROM habits WHERE id=:id"),
                     {"id":habit_id}).fetchone()
    require_habit_row_exists(row,habit_id)
    return row
    
def get_user_or_404(user_id:int,conn):
    row=conn.execute(text("SELECT * FROM users WHERE id=:id"),{"id":user_id}).fetchone()
    if not row:
        raise HTTPException(status_code=404,detail=f"User with id {user_id} not found")
    return row
    

