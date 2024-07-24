from prometheus_client import start_http_server, Gauge
import psutil
import time

# Define metrics
g_connected_devices = Gauge('connected_hardware_devices', 'Connected Hardware Devices', ['device', 'mountpoint', 'fstype'])

def collect_metrics():
    # Clear previous metrics
    g_connected_devices.clear()

    # Collect hardware information
    devices = psutil.disk_partitions()
    for device in devices:
        g_connected_devices.labels(device=device.device, mountpoint=device.mountpoint, fstype=device.fstype).set(1)

if __name__ == '__main__':
    # Start the Prometheus metrics server
    start_http_server(9103)  # Use port 9103 for custom exporter
    # Collect metrics every 15 seconds
    while True:
        collect_metrics()
        time.sleep(15)
