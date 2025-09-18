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
LOAD_1MIN_AVERAGE=Gauge("node_load1","1 minute average system load (processes running or waiting for CPU")
CPU_USAGE_BY_MODE=Gauge("cpu_usage_percent","cpu usage percent depending on mode(system,user,etc)",["mode"])
SWAPPED_RAM=Gauge("node_swap_used_megabytes","swapped info from RAM into hard drive in megabytes")
RSS=Gauge("process_resident_memory_megabytes","RSS Resident memory size in megabytes")
TCP_ESTABLISHED=Gauge("node_netstat_tcp_CurrEstab", "Number of established TCP connections")


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
    CPU_USAGE_BY_MODE.labels(mode="user").set(psutil.cpu_times_percent(interval=0).user)
    CPU_USAGE_BY_MODE.labels(mode="system").set(psutil.cpu_times_percent(interval=0).system)
    pid=os.getpid()
    process=psutil.Process(pid)
    rss_mbytes=process.memory_info().rss/(1024*1024)
    RSS.set(rss_mbytes)
    swapped_memory=psutil.swap_memory()
    swapped_memory_mbytes=swapped_memory/(1024*1024)
    SWAPPED_RAM.set(swapped_memory_mbytes)
    load1=psutil.getloadavg()[0]
    LOAD_1MIN_AVERAGE.set(load1)
    used_bytes=psutil.virtual_memory().used
    used_mbytes=used_bytes/(1024*1024)
    RAM_USAGE_MBYTES.set(used_mbytes)
    tcp_conns=psutil.net_connections(kind="tcp")
    tcp_conns_established=[c for c in tcp_conns if c.status=="ESTABLISHED"]
    TCP_ESTABLISHED.set(len(tcp_conns_established))
    
    
    
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

    

