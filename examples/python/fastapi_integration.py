"""
Example of RoboCompute integration with FastAPI
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from robocompute import RoboComputeClient, InsufficientFundsError, TaskNotFoundError

app = FastAPI()

# Initialize client
client = RoboComputeClient(
    api_key="rc_live_your_api_key",
    wallet_address="YourSolanaWalletAddress",
    solana_rpc="https://api.mainnet-beta.solana.com"
)


class TaskRequest(BaseModel):
    name: str
    type: str
    cpu_cores: int
    gpu_memory_gb: int
    ram_gb: int
    docker_image: str
    command: list[str]
    max_price_per_hour: str


@app.post("/tasks/submit")
async def submit_task(request: TaskRequest):
    """Submit task for execution"""
    try:
        task = client.tasks.create(
            name=request.name,
            type=request.type,
            resource_requirements={
                "cpu_cores": request.cpu_cores,
                "gpu_memory_gb": request.gpu_memory_gb,
                "ram_gb": request.ram_gb
            },
            docker_image=request.docker_image,
            command=request.command,
            max_price_per_hour=request.max_price_per_hour  # USDC
        )
        return {"task_id": task["task_id"], "status": task["status"]}
    except InsufficientFundsError as e:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "Insufficient funds",
                "required": e.details.get("required"),
                "available": e.details.get("available")
            }
        )


@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """Get task information"""
    try:
        task = client.tasks.get(task_id)
        return task
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")


@app.get("/wallet/balance")
async def get_balance():
    """Get wallet balance"""
    balance = client.wallet.get_balance()
    return balance


@app.get("/billing/history")
async def get_billing_history(start_date: str = None, end_date: str = None):
    """Get transaction history"""
    history = client.billing.get_history(start_date=start_date, end_date=end_date)
    return history

