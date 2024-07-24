from prometheus_client import start_http_server, Gauge
import psutil
import time

# Define metrics
g_source_ip = Gauge('network_connection_source_ip', 'Source IP Address', ['source_ip'])
g_dest_ip = Gauge('network_connection_dest_ip', 'Destination IP Address', ['dest_ip'])
g_port = Gauge('network_connection_port', 'Port Number', ['port'])
g_protocol = Gauge('network_connection_protocol', 'Protocol', ['protocol'])
g_metadata = Gauge('network_connection_metadata', 'Metadata', ['metadata'])


def collect_metrics():
    # Clear previous metrics
    g_source_ip.clear()
    g_dest_ip.clear()
    g_port.clear()
    g_protocol.clear()
    g_metadata.clear()

    # Collect network connections
    connections = psutil.net_connections()
    for conn in connections:
        if conn.laddr and conn.raddr:
            g_source_ip.labels(source_ip=conn.laddr.ip).set(1)
            g_dest_ip.labels(dest_ip=conn.raddr.ip).set(1)
            g_port.labels(port=conn.laddr.port).set(1)
            protocol = 'TCP' if conn.type == 1 else 'UDP'
            g_protocol.labels(protocol=protocol).set(1)
            g_metadata.labels(metadata="example_metadata").set(1)


if __name__ == '__main__':
    # Start the Prometheus metrics server
    start_http_server(9101)  # Use port 9101 for custom exporter
    # Collect metrics every 15 seconds
    while True:
        collect_metrics()
        time.sleep(10)
