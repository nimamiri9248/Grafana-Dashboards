from prometheus_client import start_http_server, Gauge
import psutil
import time

# Define metrics
g_active_users = Gauge('system_active_users', 'Active System Users', ['user'])

def collect_metrics():
    # Clear previous metrics
    g_active_users.clear()

    # Collect logged-in users (simulate if empty)
    users = psutil.users()
    if not users:
        # Simulate a user if none are detected
        g_active_users.labels(user="simulated_user").set(1)
    else:
        for user in users:
            g_active_users.labels(user=user.name).set(1)

if __name__ == '__main__':
    # Start the Prometheus metrics server
    start_http_server(9102)  # Use port 9102 for custom exporter
    # Collect metrics every 15 seconds
    while True:
        collect_metrics()
        time.sleep(15)
