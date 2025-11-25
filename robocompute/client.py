"""
Client for working with RoboCompute API (for buyers of computational power)
"""

import json
import time
from typing import Dict, List, Optional, Any, Iterator
from urllib.parse import urljoin

import requests
from websocket import create_connection
from solana.rpc.api import Client as SolanaClient
from solana.keypair import Keypair
from base58 import b58encode, b58decode

from robocompute.exceptions import (
    RoboComputeError,
    AuthenticationError,
    InsufficientFundsError,
    TaskNotFoundError,
    ProviderUnavailableError,
    InvalidResourceRequirementsError,
    WalletSignatureError,
    RateLimitError,
    NetworkError,
)


class RoboComputeClient:
    """
    Client for working with RoboCompute API
    
    Enables robots, IoT devices, and AI agents to rent computational power,
    paying with Solana stablecoins (USDC/USDT).
    """
    
    BASE_URL = "https://robocompute.xyz/api"
    API_VERSION = "v1"
    
    def __init__(
        self,
        api_key: str,
        wallet_address: str,
        solana_rpc: str = "https://api.mainnet-beta.solana.com",
        base_url: Optional[str] = None,
    ):
        """
        Initialize client
        
        Args:
            api_key: API key from RoboCompute
            wallet_address: Solana wallet address
            solana_rpc: Solana RPC node URL
            base_url: Base API URL (optional, for testing)
        """
        self.api_key = api_key
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
        self.tasks = TaskManager(self)
        self.wallet = WalletManager(self)
        self.billing = BillingManager(self)
        self.providers = ProviderManager(self)
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to API
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint
            data: Data to send
            params: Request parameters
            
        Returns:
            API response
            
        Raises:
            RoboComputeError: On API error
        """
        url = urljoin(self.api_url, endpoint)
        
        # Add wallet signature
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
            
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                raise RateLimitError(
                    "Rate limit exceeded",
                    retry_after=retry_after
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
                    
                    if code == "INSUFFICIENT_FUNDS":
                        raise InsufficientFundsError(
                            message,
                            required=details.get("required"),
                            available=details.get("available"),
                            currency=details.get("currency"),
                        )
                    elif code == "TASK_NOT_FOUND":
                        raise TaskNotFoundError(message, details.get("task_id"))
                    elif code == "PROVIDER_UNAVAILABLE":
                        raise ProviderUnavailableError(message, details.get("provider_id"))
                    elif code == "INVALID_RESOURCE_REQUIREMENTS":
                        raise InvalidResourceRequirementsError(message, details.get("requirements"))
                    elif code == "WALLET_SIGNATURE_INVALID":
                        raise WalletSignatureError(message)
                    elif code == "RATE_LIMIT_EXCEEDED":
                        raise RateLimitError(message, details.get("retry_after"))
                    else:
                        raise RoboComputeError(message, code=code, details=details)
                except ValueError:
                    pass
            
            raise NetworkError(f"Network error: {str(e)}", status_code=getattr(e.response, 'status_code', None))
    
    def _sign_message(self, message: str) -> str:
        """
        Sign message using Solana wallet
        
        Args:
            message: Message to sign
            
        Returns:
            Base64-encoded signature
        """
        # In real implementation, this should sign via Solana wallet
        # For example, returning a stub
        import base64
        return base64.b64encode(message.encode()).decode()


class TaskManager:
    """Manager for working with tasks"""
    
    def __init__(self, client: RoboComputeClient):
        self.client = client
    
    def create(
        self,
        name: str,
        type: str,
        resource_requirements: Dict[str, int],
        docker_image: str,
        command: List[str],
        max_price_per_hour: str,
        timeout_seconds: Optional[int] = 3600,
        priority: str = "normal",
        storage_gb: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Create new task
        
        Args:
            name: Task name
            type: Task type (cpu, gpu, etc.)
            resource_requirements: Resource requirements
            docker_image: Docker image for execution
            command: Command to run
            max_price_per_hour: Maximum price per hour (USDC)
            timeout_seconds: Execution timeout in seconds
            priority: Priority (high, normal, low)
            storage_gb: Required storage in GB
            
        Returns:
            Information about created task
        """
        data = {
            "name": name,
            "type": type,
            "resource_requirements": resource_requirements,
            "docker_image": docker_image,
            "command": command,
            "max_price_per_hour": max_price_per_hour,
            "timeout_seconds": timeout_seconds,
            "priority": priority,
        }
        
        if storage_gb:
            data["resource_requirements"]["storage_gb"] = storage_gb
        
        return self.client._make_request("POST", "/tasks", data=data)
    
    def get(self, task_id: str) -> Dict[str, Any]:
        """
        Get task information
        
        Args:
            task_id: Task ID
            
        Returns:
            Task information
        """
        return self.client._make_request("GET", f"/tasks/{task_id}")
    
    def list(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        List tasks
        
        Args:
            status: Status filter
            limit: Results limit
            offset: Offset
            
        Returns:
            List of tasks
        """
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        
        return self.client._make_request("GET", "/tasks", params=params)
    
    def update(
        self,
        task_id: str,
        max_price_per_hour: Optional[str] = None,
        priority: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Update task
        
        Args:
            task_id: Task ID
            max_price_per_hour: New maximum price
            priority: New priority
            timeout_seconds: New timeout
            
        Returns:
            Updated task information
        """
        data = {}
        if max_price_per_hour:
            data["max_price_per_hour"] = max_price_per_hour
        if priority:
            data["priority"] = priority
        if timeout_seconds:
            data["timeout_seconds"] = timeout_seconds
        
        return self.client._make_request("PATCH", f"/tasks/{task_id}", data=data)
    
    def cancel(self, task_id: str) -> Dict[str, Any]:
        """
        Cancel task
        
        Args:
            task_id: Task ID
            
        Returns:
            Information about cancelled task
        """
        return self.client._make_request("DELETE", f"/tasks/{task_id}")
    
    def stream(self, task_id: str) -> Iterator[Dict[str, Any]]:
        """
        Stream task updates via WebSocket
        
        Args:
            task_id: Task ID
            
        Yields:
            Task updates
        """
        ws_url = f"wss://robocompute.xyz/api/{self.client.API_VERSION}/tasks/{task_id}/stream"
        
        try:
            ws = create_connection(ws_url)
            ws.send(json.dumps({
                "action": "subscribe",
                "task_id": task_id,
            }))
            
            while True:
                message = ws.recv()
                data = json.loads(message)
                yield data
                
                if data.get("status") in ["completed", "failed", "cancelled", "timeout"]:
                    break
            
            ws.close()
        except Exception as e:
            raise NetworkError(f"WebSocket error: {str(e)}")
    
    def get_logs(
        self,
        task_id: str,
        lines: int = 100,
        follow: bool = False,
    ) -> Dict[str, Any]:
        """
        Get task logs
        
        Args:
            task_id: Task ID
            lines: Number of lines
            follow: Follow logs in real-time
            
        Returns:
            Task logs
        """
        params = {"lines": lines, "follow": follow}
        return self.client._make_request("GET", f"/tasks/{task_id}/logs", params=params)
    
    def get_metrics(self, task_id: str) -> Dict[str, Any]:
        """
        Get task metrics
        
        Args:
            task_id: Task ID
            
        Returns:
            Task metrics
        """
        return self.client._make_request("GET", f"/tasks/{task_id}/metrics")
    
    def get_results(self, task_id: str) -> Dict[str, Any]:
        """
        Get task execution results
        
        Args:
            task_id: Task ID
            
        Returns:
            Task results
        """
        return self.client._make_request("GET", f"/tasks/{task_id}/results")


class WalletManager:
    """Manager for working with wallet"""
    
    def __init__(self, client: RoboComputeClient):
        self.client = client
    
    def get_balance(self) -> Dict[str, Any]:
        """
        Get wallet balance
        
        Returns:
            Balance in USDC, USDT and SOL
        """
        return self.client._make_request("GET", "/wallet/balance")
    
    def deposit(
        self,
        amount: str,
        currency: str = "USDC",
        memo: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create deposit
        
        Args:
            amount: Deposit amount
            currency: Currency (USDC or USDT)
            memo: Transaction memo
            
        Returns:
            Deposit information
        """
        data = {
            "amount": amount,
            "currency": currency,
        }
        if memo:
            data["memo"] = memo
        
        return self.client._make_request("POST", "/wallet/deposit", data=data)


class BillingManager:
    """Manager for working with billing"""
    
    def __init__(self, client: RoboComputeClient):
        self.client = client
    
    def get_history(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get transaction history
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Transaction history
        """
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        return self.client._make_request("GET", "/billing/history", params=params)
    
    def get_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """
        Get invoice
        
        Args:
            invoice_id: Invoice ID
            
        Returns:
            Invoice information
        """
        return self.client._make_request("GET", f"/billing/invoices/{invoice_id}")
    
    def set_payment_method(
        self,
        preferred_currency: str = "USDC",
        auto_topup: bool = False,
        topup_threshold: Optional[str] = None,
        topup_amount: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Set payment method
        
        Args:
            preferred_currency: Preferred currency (USDC or USDT)
            auto_topup: Automatic top-up
            topup_threshold: Threshold for auto top-up
            topup_amount: Auto top-up amount
            
        Returns:
            Payment method information
        """
        data = {
            "preferred_currency": preferred_currency,
            "auto_topup": auto_topup,
        }
        if topup_threshold:
            data["topup_threshold"] = topup_threshold
        if topup_amount:
            data["topup_amount"] = topup_amount
        
        return self.client._make_request("POST", "/billing/payment-method", data=data)


class ProviderManager:
    """Manager for working with providers"""
    
    def __init__(self, client: RoboComputeClient):
        self.client = client
    
    def search(
        self,
        gpu_memory_min: Optional[int] = None,
        cpu_cores_min: Optional[int] = None,
        max_price: Optional[str] = None,
        location: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search providers
        
        Args:
            gpu_memory_min: Minimum GPU memory in GB
            cpu_cores_min: Minimum number of CPU cores
            max_price: Maximum price per hour (USDC)
            location: Provider location
            
        Returns:
            List of providers
        """
        params = {}
        if gpu_memory_min:
            params["gpu_memory_min"] = gpu_memory_min
        if cpu_cores_min:
            params["cpu_cores_min"] = cpu_cores_min
        if max_price:
            params["max_price"] = max_price
        if location:
            params["location"] = location
        
        return self.client._make_request("GET", "/providers/search", params=params)
    
    def get(self, provider_id: str) -> Dict[str, Any]:
        """
        Get provider information
        
        Args:
            provider_id: Provider ID
            
        Returns:
            Provider information
        """
        return self.client._make_request("GET", f"/providers/{provider_id}")

