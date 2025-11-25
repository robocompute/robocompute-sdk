"""
Tests for RoboCompute exceptions
"""
import unittest
from robocompute.exceptions import (
    RoboComputeError,
    InsufficientFundsError,
    TaskNotFoundError,
    ProviderUnavailableError,
    AuthenticationError,
    RateLimitError
)


class TestExceptions(unittest.TestCase):
    """Test cases for custom exceptions"""
    
    def test_robo_compute_error(self):
        """Test base exception"""
        error = RoboComputeError("Test error")
        self.assertEqual(str(error), "Test error")
    
    def test_insufficient_funds_error(self):
        """Test insufficient funds error"""
        error = InsufficientFundsError("Insufficient funds", details={"required": "10.00", "available": "5.00"})
        self.assertEqual(str(error), "Insufficient funds")
        self.assertEqual(error.details["required"], "10.00")
    
    def test_task_not_found_error(self):
        """Test task not found error"""
        error = TaskNotFoundError("Task not found", task_id="task_123")
        self.assertEqual(str(error), "Task not found")
        self.assertEqual(error.task_id, "task_123")
    
    def test_provider_unavailable_error(self):
        """Test provider unavailable error"""
        error = ProviderUnavailableError("Provider unavailable", provider_id="provider_123")
        self.assertEqual(str(error), "Provider unavailable")
        self.assertEqual(error.provider_id, "provider_123")
    
    def test_authentication_error(self):
        """Test authentication error"""
        error = AuthenticationError("Invalid API key")
        self.assertEqual(str(error), "Invalid API key")
    
    def test_rate_limit_error(self):
        """Test rate limit error"""
        error = RateLimitError("Rate limit exceeded", retry_after=60)
        self.assertEqual(str(error), "Rate limit exceeded")
        self.assertEqual(error.retry_after, 60)


if __name__ == '__main__':
    unittest.main()

