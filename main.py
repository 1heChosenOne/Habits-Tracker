from fastapi import FastAPI ,Depends,HTTPException,Response,Request
from fastapi.security import HTTPBasic , HTTPBasicCredentials
from db import get_conn
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from pydantic_schemas import user_create,habit_create,user,habit,habit_mark,new_habit_name
from utils import current_time,get_habit_or_404,get_user_or_404,require_habit_row_exists
from prometheus_client import Counter , Histogram,generate_latest,CONTENT_TYPE_LATEST
import time,os
import tables
from dotenv import load_dotenv

app=FastAPI()

security=HTTPBasic()

load_dotenv()

correct_login=os.getenv("CORRECT_LOGIN")
correct_password=os.getenv("CORRECT_PASSWORD")



@app.get("/users")
async def users_all(conn=Depends(get_conn)):
        result=conn.execute(text("SELECT * FROM users")).fetchall()
        if not result:
            raise HTTPException(status_code=404,detail="No users found")
        return (dict(row._mapping) for row in result)
    
@app.get("/users/{user_id}")
async def user_by_id(user_id:int,conn=Depends(get_conn)):
    row=get_user_or_404(user_id,conn)
    return dict(row._mapping)

@app.get("/users/{user_id}/habits")
async def get_user_habits(user_id:int,conn=Depends(get_conn)):
    res=conn.execute(text("SELECT * FROM habits WHERE owner_id=:id"),{"id":user_id}).fetchall()
    if not res:
        raise HTTPException(status_code=404,detail=f"Habits with owner id {user_id} not found")
    return (dict(row._mapping) for row in res)
    

@app.get("/habits/{habit_id}")
async def get_habit(habit_id:int,conn=Depends(get_conn)):
    row=get_habit_or_404(habit_id,conn)
    return dict(row._mapping)

@app.get("/")
async def home():
    return {"message":"""Hello everybody my name is Markiplier and i am officially back! In this API you can send GET to /users, /users/{user_id}, /users/{user_id}, /users/{user_id}/habits, /habits, /habits/{habit_id} POST to /users, /habits PATCH to /habits/{habit_id}/mark to mark habit, /habits/{habit_id}/rename DELETE to /habits/{habit_id}"""}
    
@app.post("/users")
async def create_user(user_info:user_create,conn=Depends(get_conn)):
    try:
        res=conn.execute(text("INSERT INTO users (name,email) VALUES (:name,:email) RETURNING id,name,email"),{"name":user_info.name,"email":user_info.email}).fetchone()
        return dict(res._mapping)
    except IntegrityError:
        raise HTTPException(status_code=409,detail="This email is taken by other user")
    
@app.post("/habits")
async def create_task(habit_info:habit_create,conn=Depends(get_conn)):
    time=current_time()
    res=conn.execute(text("""INSERT INTO habits (name,owner_id,last_mark)
                          VALUES (:name,:owner_id,:last_mark)
                          RETURNING id,name,owner_id,last_mark,streak"""),{"name":habit_info.name,"owner_id":habit_info.owner_id,"last_mark":time}).fetchone()
    return dict(res._mapping)

@app.patch("/habits/{habit_id}/mark")
async def mark_habit(habit_id:int,mark_task:habit_mark,conn=Depends(get_conn)):
    if mark_task.mark_habit is True:
        streak=conn.execute(text("SELECT streak FROM habits WHERE id=:id"),{"id":habit_id}).fetchone()
        require_habit_row_exists(streak,habit_id)
        new_streak=streak[0]+1
        new_datetime=current_time()
        result=conn.execute(text("UPDATE habits SET streak=:streak,last_mark=:new_datetime WHERE id=:id RETURNING streak,last_mark"),{"streak":new_streak,"new_datetime":new_datetime,"id":habit_id}).fetchone()
        return dict(result._mapping)
    
@app.patch("/habits/{habit_id}/rename")
async def rename_habit(habit_id:int,new_name:new_habit_name,conn=Depends(get_conn)):
    result1=conn.execute(text("SELECT name FROM habits WHERE id=:id"),{"id":habit_id}).fetchone()
    require_habit_row_exists(result1,habit_id)
    result2=conn.execute(text("UPDATE habits SET name=:name WHERE id=:id RETURNING id,owner_id,name,last_mark,streak"),{"name":new_name.new_name,"id":habit_id}).fetchone()
    return dict(result1._mapping),{"message":"New name:"},dict(result2._mapping)

@app.delete("/habits/{habit_id}")
async def delete_habit(habit_id:int,conn=Depends(get_conn)):
    result=conn.execute(text("DELETE FROM habits WHERE id=:id RETURNING *"),{"id":habit_id}).fetchone()
    require_habit_row_exists(result,habit_id)
    return (dict(result._mapping) ,{"message":"deleted"})


REQUEST_COUNT=Counter("http_requests_total","total of all http methods",["method","endpoint"])
REQUEST_LATENCY=Histogram("http_request_latency_seconds","HTTP request latency",["method", "endpoint"])

@app.middleware("http")
async def metrics_middleware(request:Request,call_next):
    method=request.method
    endpoint=request.url.path
    start=time.time()
    response = await call_next(request)
    end=time.time()-start
    REQUEST_COUNT.labels(method=method,endpoint=endpoint).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(end)
    return response


def check_admin_auth(credential:HTTPBasicCredentials=Depends(security)):
    if not credential.username == correct_login or not credential.password == correct_password:
        raise HTTPException(status_code=401,detail="Wrong login or password")
    return credential

@app.get("/metrics")
async def metrics(auth:HTTPBasicCredentials=Depends(check_admin_auth)):
    return Response(generate_latest(),media_type=CONTENT_TYPE_LATEST)


    
    
