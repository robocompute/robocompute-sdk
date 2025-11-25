"""
Example of computational power provider
"""

from robocompute.provider import RoboComputeProvider
import time
import subprocess


def execute_task(task):
    """
    Execute task
    
    Args:
        task: Task information
        
    Returns:
        Execution results
    """
    # Here should be real task execution logic
    # For example, running Docker container
    task_id = task["task_id"]
    docker_image = task["docker_image"]
    command = task["command"]
    
    # Simulate execution
    print(f"Executing task {task_id}...")
    time.sleep(5)  # Simulate work
    
    return {
        "result_hash": "sha256_hash_here",
        "result_storage_url": f"https://storage.robocompute.io/results/{task_id}",
        "execution_time_seconds": 5,
        "resource_usage": {
            "cpu_hours": 0.01,
            "gpu_hours": 0.01,
            "ram_hours": 0.01
        }
    }


# Initialize provider
provider = RoboComputeProvider(
    api_key="rc_prov_live_your_api_key",
    provider_id="provider_xyz789",
    wallet_address="YourSolanaWalletAddress",
    solana_rpc="https://api.mainnet-beta.solana.com"
)

# Register resources
gpu_resource = provider.resources.create(
    resource_type="gpu",
    specifications={
        "model": "NVIDIA RTX 4090",
        "memory_gb": 24,
        "compute_capability": "8.9"
    },
    pricing={
        "per_hour": "8.00",  # USDC
        "per_minute": "0.133"
    },
    availability={
        "max_concurrent_tasks": 4,
        "scheduling_policy": "fifo"
    }
)

print(f"GPU resource registered: {gpu_resource['resource_id']}")

# Check staking
staking_status = provider.staking.get_status()
print(f"Staked amount: {staking_status['staked_amount']} {staking_status['currency']}")
print(f"Minimum required: {staking_status['minimum_required']}")

# Handler for new tasks
@provider.on_task_assigned
def handle_task(task):
    """Handle assigned task"""
    print(f"New task assigned: {task['task_id']}")
    
    try:
        # Accept task
        provider.tasks.accept(task['task_id'], resource_id=gpu_resource['resource_id'])
        
        # Start execution
        provider.tasks.start(task['task_id'])
        
        # Execute task
        result = execute_task(task)
        
        # Update progress
        provider.tasks.update_progress(
            task['task_id'],
            progress=100,
            status="running",
            metrics={
                "cpu_usage": 85.5,
                "gpu_usage": 92.3,
                "memory_usage_gb": 12.5
            }
        )
        
        # Complete task
        completion = provider.tasks.complete(
            task['task_id'],
            result_hash=result["result_hash"],
            result_storage_url=result["result_storage_url"],
            execution_time_seconds=result["execution_time_seconds"],
            resource_usage=result["resource_usage"]
        )
        
        print(f"Task completed! Earnings: {completion['earnings']} USDC")
        
    except Exception as e:
        print(f"Error executing task: {e}")
        provider.tasks.fail(
            task['task_id'],
            error_code="EXECUTION_ERROR",
            error_message=str(e)
        )

# Start provider
print("Starting provider node...")
provider.start()

# Send heartbeat every 30 seconds
try:
    while True:
        provider.monitoring.send_heartbeat(
            status="online",
            resources_available={
                "cpu_cores": 8,
                "gpu_memory_gb": 24,
                "ram_gb": 32
            },
            active_tasks=1
        )
        time.sleep(30)
except KeyboardInterrupt:
    print("Stopping provider...")
    provider.stop()

