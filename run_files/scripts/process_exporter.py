from prometheus_client import start_http_server, Gauge
import psutil

# Define metrics
g_process_name = Gauge('custom_process_name', 'Process Name', ['pid', 'name'])
g_process_cpu_usage = Gauge('custom_process_cpu_usage', 'CPU Usage Percentage', ['pid', 'name'])
g_process_memory_usage = Gauge('custom_process_memory_usage', 'Memory Usage (bytes)', ['pid', 'name'])

def collect_metrics():
    # Clear existing metrics to avoid stale data
    g_process_name.clear()
    g_process_cpu_usage.clear()
    g_process_memory_usage.clear()

    # Collect process metrics
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
        try:
            pid = proc.info['pid']
            name = proc.info['name']
            cpu_usage = proc.info['cpu_percent']
            memory_usage = proc.info['memory_info'].rss

            g_process_name.labels(pid=pid, name=name).set(1)
            g_process_cpu_usage.labels(pid=pid, name=name).set(cpu_usage)
            g_process_memory_usage.labels(pid=pid, name=name).set(memory_usage)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

if __name__ == '__main__':
    start_http_server(9104)
    while True:
        collect_metrics()

