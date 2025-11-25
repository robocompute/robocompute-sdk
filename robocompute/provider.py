"""
Provider for working with RoboCompute API (for sellers of computational power)
"""

import json
import time
from typing import Dict, List, Optional, Any, Callable
from urllib.parse import urljoin
from threading import Thread
import requests
from solana.rpc.api import Client as SolanaClient

from robocompute.exceptions import (
    RoboComputeError,
    InsufficientStakeError,
    ResourceUnavailableError,
    TaskAlreadyAcceptedError,
    VerificationFailedError,
    SlashingEventError,
)
from robocompute.client import RoboComputeClient


class RoboComputeProvider:
    """
    Provider for working with RoboCompute API
    
    Enables users to provide computational resources
    and earn Solana stablecoins (USDC/USDT).
    """
    
    BASE_URL = "https://robocompute.xyz/api"
    API_VERSION = "v1"
    
    def __init__(
        self,
        api_key: str,
        provider_id: str,
        wallet_address: str,
        solana_rpc: str = "https://api.mainnet-beta.solana.com",
        base_url: Optional[str] = None,
    ):
        """
        Initialize provider
        
        Args:
            api_key: Provider API key
            provider_id: Provider ID
            wallet_address: Solana wallet address
            solana_rpc: Solana RPC node URL
            base_url: Base API URL (optional)
        """
        self.api_key = api_key
        self.provider_id = provider_id
        self.wallet_address = wallet_address
        self.solana_rpc = solana_rpc
        self.base_url = base_url or self.BASE_URL
        self.api_url = f"{self.base_url}/{self.API_VERSION}"
        
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })
        
        self.solana_client = SolanaClient(solana_rpc)
        self.running = False
        self.task_handlers: List[Callable] = []
        
        self.resources = ResourceManager(self)
        self.tasks = ProviderTaskManager(self)
        self.earnings = EarningsManager(self)
        self.staking = StakingManager(self)
        self.monitoring = MonitoringManager(self)
    
    def on_task_assigned(self, handler: Callable):
        """
        Register handler for new tasks
        
        Args:
            handler: Handler function that accepts task as argument
        """
        self.task_handlers.append(handler)
    
    def start(self):
        """Start provider and begin listening for tasks"""
        self.running = True
        # In real implementation, this should use WebSocket or polling
        # to receive new tasks
        Thread(target=self._listen_for_tasks, daemon=True).start()
    
    def stop(self):
        """Stop provider"""
        self.running = False
    
    def _listen_for_tasks(self):
        """Listen for new tasks (internal method)"""
        while self.running:
            try:
                # Get available tasks
                available_tasks = self._get_available_tasks()
                
                for task in available_tasks:
                    for handler in self.task_handlers:
                        try:
                            handler(task)
                        except Exception as e:
                            print(f"Error in task handler: {e}")
                
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                print(f"Error listening for tasks: {e}")
                time.sleep(10)
    
    def _get_available_tasks(self) -> List[Dict[str, Any]]:
        """Get available tasks (internal method)"""
        try:
            response = self._make_request("GET", f"/providers/{self.provider_id}/tasks/available")
            return response.get("tasks", [])
        except Exception:
            return []
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = urljoin(self.api_url, endpoint)
        
        timestamp = int(time.time())
        signature = self._sign_message(f"{method}{endpoint}{timestamp}")
        
        headers = {
            "X-Wallet-Signature": signature,
            "X-Timestamp": str(timestamp),
        }
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error = error_data.get("error", {})
                    code = error.get("code", "UNKNOWN_ERROR")
                    message = error.get("message", str(e))
                    details = error.get("details", {})
                    
                    if code == "INSUFFICIENT_STAKE":
                        raise InsufficientStakeError(
                            message,
                            required=details.get("required"),
                            current=details.get("current"),
                            currency=details.get("currency"),
                        )
                    elif code == "RESOURCE_UNAVAILABLE":
                        raise ResourceUnavailableError(message, details.get("resource_id"))
                    elif code == "TASK_ALREADY_ACCEPTED":
                        raise TaskAlreadyAcceptedError(message, details.get("task_id"))
                    elif code == "VERIFICATION_FAILED":
                        raise VerificationFailedError(message)
                    elif code == "SLASHING_EVENT":
                        raise SlashingEventError(message, details.get("amount"))
                    else:
                        raise RoboComputeError(message, code=code, details=details)
                except ValueError:
                    pass
            
            raise RoboComputeError(f"Network error: {str(e)}")
    
    def _sign_message(self, message: str) -> str:
        """Sign message"""
        import base64
        return base64.b64encode(message.encode()).decode()


class ResourceManager:
    """Manager for working with provider resources"""
    
    def __init__(self, provider: RoboComputeProvider):
        self.provider = provider
    
    def create(
        self,
        resource_type: str,
        specifications: Dict[str, Any],
        pricing: Dict[str, str],
        availability: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Register resource
        
        Args:
            resource_type: Resource type (cpu, gpu, ram, storage)
            specifications: Resource specifications
            pricing: Pricing (per_hour in USDC)
            availability: Availability settings
            
        Returns:
            Information about registered resource
        """
        data = {
            "resource_type": resource_type,
            "specifications": specifications,
            "pricing": pricing,
        }
        if availability:
            data["availability"] = availability
        
        return self.provider._make_request(
            "POST",
            f"/providers/{self.provider.provider_id}/resources",
            data=data,
        )
    
    def get(self, resource_id: str) -> Dict[str, Any]:
        """Get resource information"""
        return self.provider._make_request(
            "GET",
            f"/providers/{self.provider.provider_id}/resources/{resource_id}",
        )
    
    def list(
        self,
        type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List resources"""
        params = {}
        if type:
            params["type"] = type
        if status:
            params["status"] = status
        
        return self.provider._make_request(
            "GET",
            f"/providers/{self.provider.provider_id}/resources",
            params=params,
        )
    
    def update(
        self,
        resource_id: str,
        pricing: Optional[Dict[str, str]] = None,
        availability: Optional[Dict[str, Any]] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update resource"""
        data = {}
        if pricing:
            data["pricing"] = pricing
        if availability:
            data["availability"] = availability
        if status:
            data["status"] = status
        
        return self.provider._make_request(
            "PATCH",
            f"/providers/{self.provider.provider_id}/resources/{resource_id}",
            data=data,
        )
    
    def delete(self, resource_id: str) -> Dict[str, Any]:
        """Delete resource"""
        return self.provider._make_request(
            "DELETE",
            f"/providers/{self.provider.provider_id}/resources/{resource_id}",
        )


class ProviderTaskManager:
    """Manager for working with provider tasks"""
    
    def __init__(self, provider: RoboComputeProvider):
        self.provider = provider
    
    def accept(self, task_id: str, resource_id: Optional[str] = None) -> Dict[str, Any]:
        """Accept task"""
        data = {"task_id": task_id}
        if resource_id:
            data["resource_id"] = resource_id
        
        return self.provider._make_request(
            "POST",
            f"/providers/{self.provider.provider_id}/tasks/accept",
            data=data,
        )
    
    def start(
        self,
        task_id: str,
        container_id: Optional[str] = None,
        resource_usage: Optional[Dict[str, int]] = None,
    ) -> Dict[str, Any]:
        """Start task execution"""
        data = {}
        if container_id:
            data["container_id"] = container_id
        if resource_usage:
            data["resource_usage"] = resource_usage
        
        return self.provider._make_request(
            "POST",
            f"/providers/{self.provider.provider_id}/tasks/{task_id}/start",
            data=data,
        )
    
    def update_progress(
        self,
        task_id: str,
        progress: int,
        status: str = "running",
        metrics: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Update task progress"""
        data = {
            "progress": progress,
            "status": status,
        }
        if metrics:
            data["metrics"] = metrics
        
        return self.provider._make_request(
            "PATCH",
            f"/providers/{self.provider.provider_id}/tasks/{task_id}/progress",
            data=data,
        )
    
    def complete(
        self,
        task_id: str,
        result_hash: str,
        result_storage_url: str,
        execution_time_seconds: int,
        resource_usage: Dict[str, float],
    ) -> Dict[str, Any]:
        """Complete task"""
        data = {
            "result_hash": result_hash,
            "result_storage_url": result_storage_url,
            "execution_time_seconds": execution_time_seconds,
            "resource_usage": resource_usage,
        }
        
        return self.provider._make_request(
            "POST",
            f"/providers/{self.provider.provider_id}/tasks/{task_id}/complete",
            data=data,
        )
    
    def fail(
        self,
        task_id: str,
        error_code: str,
        error_message: str,
        logs: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Report task execution error"""
        data = {
            "error_code": error_code,
            "error_message": error_message,
        }
        if logs:
            data["logs"] = logs
        
        return self.provider._make_request(
            "POST",
            f"/providers/{self.provider.provider_id}/tasks/{task_id}/fail",
            data=data,
        )


class EarningsManager:
    """Manager for working with earnings and payouts"""
    
    def __init__(self, provider: RoboComputeProvider):
        self.provider = provider
    
    def get_summary(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get earnings summary"""
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        return self.provider._make_request(
            "GET",
            f"/providers/{self.provider.provider_id}/earnings",
            params=params,
        )
    
    def request_payout(
        self,
        amount: str,
        currency: str = "USDC",
        wallet_address: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Request payout"""
        data = {
            "amount": amount,
            "currency": currency,
        }
        if wallet_address:
            data["wallet_address"] = wallet_address
        else:
            data["wallet_address"] = self.provider.wallet_address
        
        return self.provider._make_request(
            "POST",
            f"/providers/{self.provider.provider_id}/payouts/request",
            data=data,
        )
    
    def get_payout_history(self, limit: int = 50) -> Dict[str, Any]:
        """Get payout history"""
        params = {"limit": limit}
        return self.provider._make_request(
            "GET",
            f"/providers/{self.provider.provider_id}/payouts/history",
            params=params,
        )
    
    def get_pending_payouts(self) -> Dict[str, Any]:
        """Get pending payouts"""
        return self.provider._make_request(
            "GET",
            f"/providers/{self.provider.provider_id}/payouts/pending",
        )


class StakingManager:
    """Manager for working with staking"""
    
    def __init__(self, provider: RoboComputeProvider):
        self.provider = provider
    
    def get_status(self) -> Dict[str, Any]:
        """Get staking status"""
        return self.provider._make_request(
            "GET",
            f"/providers/{self.provider.provider_id}/staking",
        )
    
    def stake(self, amount: str, currency: str = "USDC") -> Dict[str, Any]:
        """Stake funds"""
        data = {
            "amount": amount,
            "currency": currency,
        }
        return self.provider._make_request(
            "POST",
            f"/providers/{self.provider.provider_id}/staking/stake",
            data=data,
        )
    
    def unstake(self, amount: str, currency: str = "USDC") -> Dict[str, Any]:
        """Unstake funds"""
        data = {
            "amount": amount,
            "currency": currency,
        }
        return self.provider._make_request(
            "POST",
            f"/providers/{self.provider.provider_id}/staking/unstake",
            data=data,
        )


class MonitoringManager:
    """Manager for monitoring provider node"""
    
    def __init__(self, provider: RoboComputeProvider):
        self.provider = provider
    
    def get_status(self) -> Dict[str, Any]:
        """Get node status"""
        return self.provider._make_request(
            "GET",
            f"/providers/{self.provider.provider_id}/status",
        )
    
    def send_heartbeat(
        self,
        status: str = "online",
        resources_available: Optional[Dict[str, int]] = None,
        active_tasks: int = 0,
    ) -> Dict[str, Any]:
        """Send heartbeat"""
        data = {
            "status": status,
            "active_tasks": active_tasks,
        }
        if resources_available:
            data["resources_available"] = resources_available
        
        return self.provider._make_request(
            "POST",
            f"/providers/{self.provider.provider_id}/heartbeat",
            data=data,
        )
    
    def get_metrics(self, period: str = "7d") -> Dict[str, Any]:
        """Get performance metrics"""
        params = {"period": period}
        return self.provider._make_request(
            "GET",
            f"/providers/{self.provider.provider_id}/metrics",
            params=params,
        )

