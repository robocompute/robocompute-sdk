"""
RoboCompute SDK - Official Python SDK for RoboCompute decentralized computing platform.

RoboCompute enables robots, IoT devices, and AI agents to rent computational power,
paying with Solana stablecoins (USDC/USDT). Providers can share their resources
and earn Solana stablecoins as rewards.
"""

__version__ = "1.0.0"
__author__ = "RoboCompute Team"
__email__ = "support@robocompute.xyz"

from robocompute.client import RoboComputeClient
from robocompute.provider import RoboComputeProvider
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

__all__ = [
    "RoboComputeClient",
    "RoboComputeProvider",
    "RoboComputeError",
    "AuthenticationError",
    "InsufficientFundsError",
    "TaskNotFoundError",
    "ProviderUnavailableError",
    "InvalidResourceRequirementsError",
    "WalletSignatureError",
    "RateLimitError",
    "NetworkError",
]

