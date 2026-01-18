import psutil
import logging
import logging.handlers
import time
import subprocess
from datetime import datetime
import os
import sys

# Configuration
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "system_monitor.log")
POLL_INTERVAL = 60  # seconds
CPU_THRESHOLD = 90  # %
MEM_THRESHOLD = 90  # %

# Ensure log directory exists
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.handlers.TimedRotatingFileHandler(
            LOG_FILE, when='midnight', interval=1, backupCount=30
        ),
        logging.StreamHandler(sys.stdout)
    ]
)

def check_internet(host="8.8.8.8", timeout=2):
    """
    Check internet connectivity by pinging Google DNS.
    Returns 'OK' or 'FAIL'.
    """
    try:
        # -c 1: count 1 packet
        # -W 2: timeout 2 seconds (macOS/Linux)
        # Note: Windows uses -n instead of -c and -w (ms) instead of -W (s).
        # Since user is on Mac (from context), -c and -W are correct.
        subprocess.check_call(
            ["ping", "-c", "1", "-W", str(timeout), host],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return "OK"
    except subprocess.CalledProcessError:
        return "FAIL"
    except Exception:
        return "ERROR"

def get_top_processes(sort_by='cpu'):
    """
    Returns a string details of top 5 processes by cpu or memory.
    """
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
        try:
            procs.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    key = 'cpu_percent' if sort_by == 'cpu' else 'memory_percent'
    procs.sort(key=lambda x: x.get(key, 0), reverse=True)
    
    top_5 = procs[:5]
    details = []
    for p in top_5:
        details.append(f"{p['name']} (PID: {p['pid']}, CPU: {p['cpu_percent']}%, MEM: {p['memory_percent']:.1f}%)")
    
    return "; ".join(details)
    

def monitor_loop():
    logging.info("Starting System Monitor...")
    
    while True:
        try:
            # 1. CPU
            cpu_pct = psutil.cpu_percent(interval=1)
            load_avg = os.getloadavg() # (1min, 5min, 15min)
            
            # 2. Memory
            mem = psutil.virtual_memory()
            mem_pct = mem.percent
            
            # 3. Disk
            disk = psutil.disk_usage('/')
            disk_pct = disk.percent
            
            # 4. Network
            net_status = check_internet()
            
            # Log standard metrics
            msg = (f"CPU: {cpu_pct}% (Load: {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}) | "
                   f"RAM: {mem_pct}% ({mem.used // (1024*1024)}MB used) | "
                   f"DISK: {disk_pct}% | NET: {net_status}")
            
            logging.info(msg)
            
            # Alerting logic
            if cpu_pct > CPU_THRESHOLD:
                top_cpu = get_top_processes('cpu')
                logging.warning(f"High CPU ({cpu_pct}%) detected! Top processes: {top_cpu}")
                
            if mem_pct > MEM_THRESHOLD:
                top_mem = get_top_processes('memory')
                logging.warning(f"High Memory ({mem_pct}%) detected! Top processes: {top_mem}")
                
        except Exception as e:
            logging.error(f"Error in monitor loop: {e}")
        
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    monitor_loop()
