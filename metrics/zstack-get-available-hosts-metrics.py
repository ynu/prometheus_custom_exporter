import requests
from prometheus_client import Gauge
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

# API endpoint and key
ZSTACK_API_URL, ZSTACK_API_KEY = os.getenv("ZSTACK_API_URL"), os.getenv("ZSTACK_API_KEY")
if not ZSTACK_API_URL or not ZSTACK_API_KEY:
    raise ValueError("Missing ZStack API URL or API key")

# Define Prometheus metrics
zstack_available_host_count = Gauge('zstack_availableHostCount', 'Number of available hosts in ZStack')
zstack_total_memory_capacity = Gauge('zstack_totalMemoryCapacity', 'Total memory capacity in ZStack (bytes)')
zstack_total_cpu_capacity = Gauge('zstack_totalCpuCapacity', 'Total CPU capacity in ZStack')
zstack_available_cpu_capacity = Gauge('zstack_availableCpuCapacity', 'Available CPU capacity in ZStack')
zstack_available_memory_capacity = Gauge('zstack_availableMemoryCapacity', 'Available memory capacity in ZStack (bytes)')
zstack_primary_storage_total_capacity = Gauge('zstack_primaryStorageTotalCapacity', 'Total primary storage capacity in ZStack (bytes)')
zstack_primary_storage_available_capacity = Gauge('zstack_primaryStorageAvailableCapacity', 'Available primary storage capacity in ZStack (bytes)')
zstack_total_host_count = Gauge('zstack_totalHostCount', 'Total number of hosts in ZStack')
zstack_total_vm_count = Gauge('zstack_totalVmCount', 'Total number of VMs in ZStack')
zstack_running_vm_count = Gauge('zstack_runningVmCount', 'Number of running VMs in ZStack')

# Last successful fetch time
zstack_last_successful_fetch = Gauge('zstack_lastSuccessfulFetch', 'Timestamp of the last successful fetch from ZStack API')

# Fetch error counter
zstack_fetch_errors = Gauge('zstack_fetchErrors', 'Number of errors encountered when fetching from ZStack API')

def fetch_zstack_metrics():
    """Fetch metrics from ZStack API"""
    try:
        params = {'apikey': ZSTACK_API_KEY}
        response = requests.get(ZSTACK_API_URL, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('data', {})
            else:
                print(f"ZStack API returned error: {data.get('message', 'Unknown error')}")
                return None
        else:
            print(f"ZStack API request failed with status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching ZStack metrics: {e}")
        return None

def process():
    """Process ZStack metrics and update Prometheus gauges"""
    print("ZStack metrics processing...")
    
    # Fetch metrics from ZStack API
    metrics_data = fetch_zstack_metrics()
    
    if metrics_data:
        # Update all metrics
        zstack_available_host_count.set(metrics_data.get('availableHostCount', 0))
        zstack_total_memory_capacity.set(metrics_data.get('totalMemoryCapacity', 0))
        zstack_total_cpu_capacity.set(metrics_data.get('totalCpuCapacity', 0))
        zstack_available_cpu_capacity.set(metrics_data.get('availableCpuCapacity', 0))
        zstack_available_memory_capacity.set(metrics_data.get('availableMemoryCapacity', 0))
        zstack_primary_storage_total_capacity.set(metrics_data.get('primaryStorageTotalCapacity', 0))
        zstack_primary_storage_available_capacity.set(metrics_data.get('primaryStorageAvailableCapacity', 0))
        zstack_total_host_count.set(metrics_data.get('totalHostCount', 0))
        zstack_total_vm_count.set(metrics_data.get('totalVmCount', 0))
        zstack_running_vm_count.set(metrics_data.get('runningVmCount', 0))
        
        # Update last successful fetch time
        zstack_last_successful_fetch.set(time.time())
        print("ZStack metrics updated successfully")
    else:
        # Increment error counter
        zstack_fetch_errors.inc()
        print("Failed to update ZStack metrics")

# Initial processing
if __name__ == "__main__":
    process()