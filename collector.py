import psutil
import time
from collections import deque
from datetime import datetime

BUFFER_SIZE = 60  # keep last 60 readings (~5 min at 5s interval)

metrics_buffer = deque(maxlen=BUFFER_SIZE)

def collect_metrics():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    net = psutil.net_io_counters()

    top_procs = sorted(
        psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']),
        key=lambda p: p.info['cpu_percent'] or 0,
        reverse=True
    )[:5]

    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "cpu": cpu,
        "ram": ram,
        "disk": disk,
        "net_bytes_sent": net.bytes_sent,
        "net_bytes_recv": net.bytes_recv,
        "top_processes": [
            {
                "pid": p.info['pid'],
                "name": p.info['name'],
                "cpu": p.info['cpu_percent'],
                "ram": p.info['memory_percent']
            }
            for p in top_procs
        ]
    }

    metrics_buffer.append(snapshot)
    return snapshot


def get_buffer():
    return list(metrics_buffer)


if __name__ == "__main__":
    print("Collector running — press Ctrl+C to stop\n")
    while True:
        m = collect_metrics()
        print(f"[{m['timestamp']}] CPU: {m['cpu']}%  RAM: {m['ram']}%  Disk: {m['disk']}%")
        time.sleep(5)