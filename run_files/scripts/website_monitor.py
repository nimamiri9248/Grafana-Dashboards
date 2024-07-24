import json
import requests
import socket
import ssl
from datetime import datetime
import subprocess
import time
from prometheus_client import start_http_server, Gauge

# Define metrics
PING_TIME = Gauge('ping_time', 'Ping times for the domain', ['domain'])
RESPONSE_TIME = Gauge('response_time', 'Response time for the domain', ['domain'])
DNS_RECORDS = Gauge('dns_records_count', 'Count of DNS records for the domain', ['domain'])
SSL_NOT_BEFORE = Gauge('ssl_not_before', 'SSL certificate not before date', ['domain'])
SSL_NOT_AFTER = Gauge('ssl_not_after', 'SSL certificate not after date', ['domain'])
WEB_SERVER_INFO = Gauge('web_server_info', 'Web server information for the domain', ['domain', 'web_server_name', 'web_server_type'])
ONLINE_STATUS = Gauge('online_status', 'Online status of the domain (1 = online, 0 = offline)', ['domain'])

# Function to get web server type and name
def get_web_server_info(domain):
    try:
        response = requests.head(f"http://{domain}", allow_redirects=True, timeout=10)
        print(f"Debug: Headers received from {domain}:\n{response.headers}")  # Debug statement
        web_server_info = response.headers.get('Server', 'unknown')
        web_server_name = web_server_info
        web_server_type = web_server_info.split('/')[0] if '/' in web_server_info else web_server_info
        print(f"Debug: Parsed web server name: {web_server_name}, type: {web_server_type}")  # Debug statement
        WEB_SERVER_INFO.labels(domain=domain, web_server_name=web_server_name, web_server_type=web_server_type).set(1)
    except Exception as e:
        print(f"Error fetching web server info for {domain}: {e}")

# Function to get SSL certificate information
def get_ssl_info(domain):
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.connect((domain, 443))
            cert = s.getpeercert()
        
        ssl_not_before = datetime.strptime(cert.get("notBefore"), "%b %d %H:%M:%S %Y %Z").timestamp()
        ssl_not_after = datetime.strptime(cert.get("notAfter"), "%b %d %H:%M:%S %Y %Z").timestamp()
        
        SSL_NOT_BEFORE.labels(domain=domain).set(ssl_not_before)
        SSL_NOT_AFTER.labels(domain=domain).set(ssl_not_after)
    except Exception as e:
        print(f"Error fetching SSL info for {domain}: {e}")

# Function to get DNS records
def get_dns_records(domain):
    try:
        result = subprocess.run(["dig", "+short", domain], capture_output=True, text=True)
        dns_records_count = len(result.stdout.split("\n")) - 1  # Exclude empty line
        DNS_RECORDS.labels(domain=domain).set(dns_records_count)
    except Exception as e:
        print(f"Error fetching DNS records for {domain}: {e}")

# Function to get ping time
def get_ping_time(domain):
    try:
        result = subprocess.run(["ping", "-c", "4", domain], capture_output=True, text=True)
        for line in result.stdout.split("\n"):
            if "time=" in line:
                time_ms = line.split("time=")[1].split(" ")[0]
                PING_TIME.labels(domain=domain).set(float(time_ms))
    except Exception as e:
        print(f"Error fetching ping time for {domain}: {e}")

# Function to get uptime and response time
def get_uptime_and_response_time(domain):
    try:
        response = requests.get(f"http://{domain}", timeout=10)
        response_time = response.elapsed.total_seconds()
        RESPONSE_TIME.labels(domain=domain).set(response_time)
        ONLINE_STATUS.labels(domain=domain).set(1)  # Set online status to 1 (online)
    except requests.RequestException:
        ONLINE_STATUS.labels(domain=domain).set(0)  # Set online status to 0 (offline)
    except Exception as e:
        print(f"Error fetching uptime and response time for {domain}: {e}")

if __name__ == "__main__":
    domain = "gateway.nobicode.ir"
    
    # Start the Prometheus HTTP server
    start_http_server(9106)  # Port where metrics will be exposed
    
    while True:
        get_web_server_info(domain)
        get_ssl_info(domain)
        get_dns_records(domain)
        get_ping_time(domain)
        get_uptime_and_response_time(domain)
        time.sleep(300)  # Repeat every 5 minutes
