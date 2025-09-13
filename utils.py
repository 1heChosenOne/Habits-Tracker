from db import engine
from datetime import datetime
from sqlalchemy import text
from fastapi import HTTPException
import psutil,os
from prometheus_client import Gauge,Histogram
from contextlib import contextmanager
import time
       
       
CPU_USAGE=Gauge("system_cpu_usage_percent","CPU usage percent")
RAM_USAGE=Gauge("system_ram_usage_percent","RAM usage percent")
RAM_USAGE_MBYTES=Gauge("system_ram_usage_megabytes","RAM usage in megabytes")
DB_LATENCY=Histogram("db_query_latency_seconds","latency of sqlite query in seconds",["operation"])

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

def collect_system_metrics():
    CPU_USAGE.set(psutil.cpu_percent())
    RAM_USAGE.set(psutil.virtual_memory().percent)
    used_bytes=psutil.virtual_memory().used
    used_mbytes=used_bytes/(1024*1024)
    RAM_USAGE_MBYTES.set(used_mbytes)
    
@contextmanager
def observe_read_latency():
    start=time.time()
    try:
        yield
    finally:
        latency=time.time()-start
        DB_LATENCY.labels("read").observe(latency)
        
@contextmanager
def observe_write_latency():
    start=time.time()
    try:
        yield
    finally:
        latency=time.time()-start
        DB_LATENCY.labels("write").observe(latency)

    

