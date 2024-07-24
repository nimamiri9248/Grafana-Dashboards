import time
import requests
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

# Prometheus configuration
registry = CollectorRegistry()
g = Gauge('page_load_time_seconds', 'Time taken to load a web page', registry=registry)

def measure_load_time(retries=5, delay=5):
    for attempt in range(retries):
        start = time.time()
        try:
            response = requests.get('https://gateway.nobicode.ir', timeout=10)
            load_time = time.time() - start
            print(f"Load time: {load_time} seconds")
            return load_time
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}, Attempt: {attempt + 1}/{retries}")
            time.sleep(delay)
    return None  # Return None if all retries fail

if __name__ == '__main__':
    while True:  # Keep running indefinitely
        load_time = measure_load_time()
        if load_time is not None:
            g.set(load_time)
            push_to_gateway('localhost:9091', job='page_load_monitor', registry=registry)
        time.sleep(60)  # Wait before the next measurement
