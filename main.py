from fastapi import FastAPI ,Depends,HTTPException,Body
from engine import engine
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from pydantic_schemas import user_create,habit_create,user,habit,habit_mark,new_habit_name
from functions import get_conn,current_time,habit_id_validator,user_id_validator



app=FastAPI()



@app.get("/users")
async def users_all(conn=Depends(get_conn)):
        result=conn.execute(text("SELECT * FROM users")).fetchall()
        return (dict(row._mapping) for row in result)
    
@app.get("/users/{user_id}")
async def user_by_id(user_id:int,conn=Depends(get_conn)):
    user_id_validator(user_id,conn)
    res=conn.execute(text("SELECT * FROM users WHERE id=:user_id"),{"user_id":user_id}).fetchone()
    return dict(res._mapping)

@app.get("/habits/{habit_id}")
async def get_habit(habit_id:int,conn=Depends(get_conn)):
    habit_id_validator(habit_id,conn)
    res=conn.execute(text("SELECT * FROM habits WHERE id=:id"),{"id":habit_id}).fetchone()
    return dict(res._mapping)

@app.get("/")
async def home():
    return {"message":"Hello everybody my name is Markiplier and i am officially back! in this API you can send Get to /users"}
    
@app.post("/users")
async def create_user(user_info:user_create,conn=Depends(get_conn)):
    try:
        res=conn.execute(text("INSERT INTO users (name,email) VALUES (:name,:email) RETURNING id,name,email"),{"name":user_info.name,"email":user_info.email}).fetchone()
        return dict(res._mapping)
    except IntegrityError:
        raise HTTPException(status_code=409,detail="Данный email занят другим пользователем")
    
@app.post("/habits")
async def create_task(habit_info:habit_create,conn=Depends(get_conn)):
    time=current_time()
    res=conn.execute(text("""INSERT INTO habits (name,owner_id,last_mark)
                          VALUES (:name,:owner_id,:last_mark)
                          RETURNING id,name,owner_id,last_mark,streak"""),{"name":habit_info.name,"owner_id":habit_info.owner_id,"last_mark":time}).fetchone()
    return dict(res._mapping)

@app.patch("/habits/{habit_id}")
async def mark_habit(habit_id:int,mark_task:habit_mark,conn=Depends(get_conn)):
    habit_id_validator(habit_id,conn)
    if mark_task.mark_habit is True:
        streak=conn.execute(text("SELECT streak FROM habits WHERE id=:id"),{"id":habit_id}).fetchone()[0]
        new_streak=streak+1
        result=conn.execute(text("UPDATE habits SET streak=:streak WHERE id=:id RETURNING streak"),{"streak":new_streak,"id":habit_id}).fetchone()
        new_time=current_time()
        result1=conn.execute(text("UPDATE habits SET last_mark=:new_datetime WHERE id=:id RETURNING last_mark"),{"new_datetime":new_time,"id":habit_id}).fetchone()
        return dict(result._mapping),dict(result1._mapping)
    
@app.patch("/habits/{habit_id}/rename")
async def rename_habit(habit_id:int,new_name:new_habit_name,conn=Depends(get_conn)):
    habit_id_validator(habit_id,conn)
    result1=conn.execute(text("SELECT name FROM habits WHERE id=:id"),{"id":habit_id}).fetchone()._mapping
    result2=conn.execute(text("UPDATE habits SET name=:name WHERE id=:id RETURNING id,owner_id,name,last_mark,streak"),{"name":new_name.new_name,"id":habit_id}).fetchone()._mapping
    return dict(result1),{"message":"New name:"},dict(result2)

@app.delete("/habits/{habit_id}")
async def delete_habit(habit_id:int,conn=Depends(get_conn)):
    habit_id_validator(habit_id,conn)
    result=conn.execute(text("DELETE FROM habits WHERE id=:id RETURNING *"),{"id":habit_id}).fetchone()._mapping
    return (dict(result) ,{"message":"deleted"})
    
    
