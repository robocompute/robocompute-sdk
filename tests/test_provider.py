"""
Tests for RoboCompute Provider SDK
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from robocompute.provider import RoboComputeProvider


class TestRoboComputeProvider(unittest.TestCase):
    """Test cases for RoboComputeProvider"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.provider = RoboComputeProvider(
            api_key="test_api_key",
            provider_id="test_provider_id",
            wallet_address="test_wallet_address",
            solana_rpc="https://api.testnet.solana.com"
        )
    
    def test_provider_initialization(self):
        """Test provider initialization"""
        self.assertEqual(self.provider.api_key, "test_api_key")
        self.assertEqual(self.provider.provider_id, "test_provider_id")
        self.assertEqual(self.provider.wallet_address, "test_wallet_address")
        self.assertEqual(self.provider.base_url, "https://robocompute.xyz/api")
    
    @patch('robocompute.provider.requests.post')
    def test_register_resource(self, mock_post):
        """Test resource registration"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "resource_id": "resource_123",
            "status": "available"
        }
        mock_response.status_code = 201
        mock_post.return_value = mock_response
        
        result = self.provider.resources.create(
            resource_type="gpu",
            specifications={"model": "NVIDIA RTX 4090", "memory_gb": 24},
            pricing={"per_hour": "8.00"}
        )
        
        self.assertEqual(result["resource_id"], "resource_123")
        mock_post.assert_called_once()
    
    @patch('robocompute.provider.requests.post')
    def test_accept_task(self, mock_post):
        """Test task acceptance"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "task_id": "task_123",
            "status": "accepted"
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = self.provider.tasks.accept("task_123")
        
        self.assertEqual(result["status"], "accepted")
        mock_post.assert_called_once()
    
    @patch('robocompute.provider.requests.get')
    def test_get_staking_status(self, mock_get):
        """Test getting staking status"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "staked_amount": "1000.00",
            "currency": "USDC",
            "minimum_required": "500.00"
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = self.provider.staking.get_status()
        
        self.assertEqual(result["staked_amount"], "1000.00")
        mock_get.assert_called_once()
    
    @patch('robocompute.provider.requests.get')
    def test_get_earnings_summary(self, mock_get):
        """Test getting earnings summary"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "total_usdc": "1250.75",
            "total_tasks": 45
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = self.provider.earnings.get_summary()
        
        self.assertEqual(result["total_usdc"], "1250.75")
        mock_get.assert_called_once()


if __name__ == '__main__':
    unittest.main()

