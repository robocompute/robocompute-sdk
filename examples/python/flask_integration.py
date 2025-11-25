"""
Flask integration example for RoboCompute SDK
"""
from flask import Flask, request, jsonify
from robocompute import RoboComputeClient
from solana.rpc.api import Client
import os

app = Flask(__name__)

# Initialize RoboCompute client
client = RoboComputeClient(
    api_key=os.getenv("ROBOCOMPUTE_API_KEY", "rc_live_your_api_key"),
    wallet_address=os.getenv("ROBOCOMPUTE_WALLET_ADDRESS", "YourSolanaWalletAddress"),
    solana_rpc=os.getenv("SOLANA_RPC", "https://api.mainnet-beta.solana.com")
)


@app.route('/tasks/submit', methods=['POST'])
def submit_task():
    """Submit a new compute task"""
    try:
        data = request.json
        task = client.tasks.create(
            name=data.get('name'),
            type=data.get('type', 'gpu'),
            resource_requirements={
                "cpu_cores": data.get('cpu_cores', 4),
                "gpu_memory_gb": data.get('gpu_memory_gb', 8),
                "ram_gb": data.get('ram_gb', 16)
            },
            docker_image=data.get('docker_image'),
            command=data.get('command', []),
            max_price_per_hour=data.get('max_price_per_hour', '10.00')  # USDC
        )
        return jsonify({
            "task_id": task.task_id,
            "status": task.status,
            "estimated_cost": getattr(task, 'estimated_cost', None)
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """Get task details"""
    try:
        task = client.tasks.get(task_id)
        return jsonify({
            "task_id": task.task_id,
            "status": task.status,
            "progress": getattr(task, 'progress', None)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 404


@app.route('/tasks/<task_id>/cancel', methods=['POST'])
def cancel_task(task_id):
    """Cancel a task"""
    try:
        result = client.tasks.cancel(task_id)
        return jsonify({
            "task_id": task_id,
            "status": "cancelled",
            "refund_amount": getattr(result, 'refund_amount', None)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/wallet/balance', methods=['GET'])
def get_balance():
    """Get wallet balance"""
    try:
        balance = client.wallet.get_balance()
        return jsonify(balance), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

