"""
Tests for RoboCompute Client SDK
"""

import pytest
from unittest.mock import Mock, patch
from robocompute import RoboComputeClient
from robocompute.exceptions import (
    InsufficientFundsError,
    TaskNotFoundError,
    RateLimitError,
)


class TestRoboComputeClient:
    """Tests for RoboComputeClient"""
    
    @pytest.fixture
    def client(self):
        """Client fixture"""
        return RoboComputeClient(
            api_key="test_api_key",
            wallet_address="test_wallet_address",
            solana_rpc="https://api.testnet.solana.com"
        )
    
    @patch('robocompute.client.requests.Session.request')
    def test_create_task_success(self, mock_request, client):
        """Test successful task creation"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "task_id": "task_123",
            "status": "pending",
            "estimated_cost": "5.50"
        }
        mock_request.return_value = mock_response
        
        task = client.tasks.create(
            name="Test Task",
            type="gpu",
            resource_requirements={"cpu_cores": 4, "gpu_memory_gb": 8, "ram_gb": 16},
            docker_image="test/image:tag",
            command=["python", "test.py"],
            max_price_per_hour="10.00"
        )
        
        assert task["task_id"] == "task_123"
        assert task["status"] == "pending"
    
    @patch('robocompute.client.requests.Session.request')
    def test_create_task_insufficient_funds(self, mock_request, client):
        """Test insufficient funds error"""
        mock_response = Mock()
        mock_response.status_code = 402
        mock_response.json.return_value = {
            "error": {
                "code": "INSUFFICIENT_FUNDS",
                "message": "Insufficient funds",
                "details": {
                    "required": "10.00",
                    "available": "5.50",
                    "currency": "USDC"
                }
            }
        }
        mock_request.return_value = mock_response
        mock_request.side_effect = Exception()
        mock_request.side_effect.response = mock_response
        
        with pytest.raises(InsufficientFundsError) as exc_info:
            client.tasks.create(
                name="Test Task",
                type="gpu",
                resource_requirements={"cpu_cores": 4},
                docker_image="test/image:tag",
                command=["python", "test.py"],
                max_price_per_hour="10.00"
            )
        
        assert exc_info.value.code == "INSUFFICIENT_FUNDS"
    
    @patch('robocompute.client.requests.Session.request')
    def test_get_task_not_found(self, mock_request, client):
        """Test task not found error"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "error": {
                "code": "TASK_NOT_FOUND",
                "message": "Task not found",
                "details": {"task_id": "task_123"}
            }
        }
        mock_request.return_value = mock_response
        mock_request.side_effect = Exception()
        mock_request.side_effect.response = mock_response
        
        with pytest.raises(TaskNotFoundError):
            client.tasks.get("task_123")
    
    @patch('robocompute.client.requests.Session.request')
    def test_rate_limit(self, mock_request, client):
        """Test rate limit error"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60"}
        mock_request.return_value = mock_response
        
        with pytest.raises(RateLimitError) as exc_info:
            client.tasks.get("task_123")
        
        assert exc_info.value.code == "RATE_LIMIT_EXCEEDED"
        assert exc_info.value.details.get("retry_after") == 60


class TestWalletManager:
    """Tests for WalletManager"""
    
    @pytest.fixture
    def client(self):
        return RoboComputeClient(
            api_key="test_api_key",
            wallet_address="test_wallet_address"
        )
    
    @patch('robocompute.client.requests.Session.request')
    def test_get_balance(self, mock_request, client):
        """Test getting balance"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "wallet_address": "test_wallet",
            "usdc_balance": "1000.50",
            "usdt_balance": "500.25",
            "sol_balance": "0.5"
        }
        mock_request.return_value = mock_response
        
        balance = client.wallet.get_balance()
        
        assert balance["usdc_balance"] == "1000.50"
        assert balance["usdt_balance"] == "500.25"

