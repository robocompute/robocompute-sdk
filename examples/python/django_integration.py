"""
Django integration example for RoboCompute SDK

Add this to your Django views.py or create a separate app
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from robocompute import RoboComputeClient
import json
import os

# Initialize client (can be done in settings or as a singleton)
_client = None

def get_client():
    """Get or create RoboCompute client instance"""
    global _client
    if _client is None:
        _client = RoboComputeClient(
            api_key=getattr(settings, 'ROBOCOMPUTE_API_KEY', os.getenv('ROBOCOMPUTE_API_KEY', 'rc_live_your_api_key')),
            wallet_address=getattr(settings, 'ROBOCOMPUTE_WALLET_ADDRESS', os.getenv('ROBOCOMPUTE_WALLET_ADDRESS', 'YourSolanaWalletAddress')),
            solana_rpc=getattr(settings, 'SOLANA_RPC', os.getenv('SOLANA_RPC', 'https://api.mainnet-beta.solana.com'))
        )
    return _client


@csrf_exempt
@require_http_methods(["POST"])
def submit_task(request):
    """Submit a new compute task"""
    try:
        data = json.loads(request.body)
        client = get_client()
        
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
        
        return JsonResponse({
            "task_id": task.task_id,
            "status": task.status,
            "estimated_cost": getattr(task, 'estimated_cost', None)
        }, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@require_http_methods(["GET"])
def get_task(request, task_id):
    """Get task details"""
    try:
        client = get_client()
        task = client.tasks.get(task_id)
        return JsonResponse({
            "task_id": task.task_id,
            "status": task.status,
            "progress": getattr(task, 'progress', None)
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def cancel_task(request, task_id):
    """Cancel a task"""
    try:
        client = get_client()
        result = client.tasks.cancel(task_id)
        return JsonResponse({
            "task_id": task_id,
            "status": "cancelled",
            "refund_amount": getattr(result, 'refund_amount', None)
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@require_http_methods(["GET"])
def get_balance(request):
    """Get wallet balance"""
    try:
        client = get_client()
        balance = client.wallet.get_balance()
        return JsonResponse(balance)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

