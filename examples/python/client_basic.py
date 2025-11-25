"""
Basic example of using RoboCompute Client SDK
"""

from robocompute import RoboComputeClient

# Initialize client
client = RoboComputeClient(
    api_key="rc_live_your_api_key",
    wallet_address="YourSolanaWalletAddress",
    solana_rpc="https://api.mainnet-beta.solana.com"
)

# Check wallet balance
balance = client.wallet.get_balance()
print(f"USDC Balance: {balance['usdc_balance']}")
print(f"USDT Balance: {balance['usdt_balance']}")

# Create task
task = client.tasks.create(
    name="Object Detection Task",
    type="gpu",
    resource_requirements={
        "cpu_cores": 4,
        "gpu_memory_gb": 8,
        "ram_gb": 16,
        "storage_gb": 50
    },
    docker_image="your-registry/image:tag",
    command=["python", "detect.py"],
    max_price_per_hour="10.00",  # USDC
    timeout_seconds=3600,
    priority="high"
)

print(f"Task created: {task['task_id']}")
print(f"Status: {task['status']}")
print(f"Estimated cost: {task['estimated_cost']} USDC")

# Monitor task
for update in client.tasks.stream(task['task_id']):
    print(f"Status: {update.get('status')}, Progress: {update.get('progress', 0)}%")
    
    if update.get('status') == 'completed':
        results = client.tasks.get_results(task['task_id'])
        print(f"Task completed! Results: {results}")
        break
    elif update.get('status') in ['failed', 'cancelled', 'timeout']:
        print(f"Task {update.get('status')}")
        break

# Get logs
logs = client.tasks.get_logs(task['task_id'], lines=100)
for log_entry in logs.get('logs', []):
    print(f"[{log_entry['timestamp']}] {log_entry['level']}: {log_entry['message']}")

# Get metrics
metrics = client.tasks.get_metrics(task['task_id'])
print(f"CPU Usage: {metrics['metrics']['cpu_usage_percent']}%")
print(f"GPU Usage: {metrics['metrics']['gpu_usage_percent']}%")

