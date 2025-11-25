"""
Exceptions for RoboCompute SDK
"""


class RoboComputeError(Exception):
    """Base exception for all RoboCompute errors"""
    
    def __init__(self, message: str, code: str = None, details: dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(RoboComputeError):
    """Authentication error"""
    pass


class InsufficientFundsError(RoboComputeError):
    """Insufficient funds in wallet"""
    
    def __init__(self, message: str, required: str = None, available: str = None, currency: str = None):
        details = {}
        if required:
            details["required"] = required
        if available:
            details["available"] = available
        if currency:
            details["currency"] = currency
        super().__init__(message, code="INSUFFICIENT_FUNDS", details=details)


class TaskNotFoundError(RoboComputeError):
    """Task not found"""
    
    def __init__(self, message: str, task_id: str = None):
        details = {"task_id": task_id} if task_id else {}
        super().__init__(message, code="TASK_NOT_FOUND", details=details)


class ProviderUnavailableError(RoboComputeError):
    """Provider unavailable"""
    
    def __init__(self, message: str, provider_id: str = None):
        details = {"provider_id": provider_id} if provider_id else {}
        super().__init__(message, code="PROVIDER_UNAVAILABLE", details=details)


class InvalidResourceRequirementsError(RoboComputeError):
    """Invalid resource requirements"""
    
    def __init__(self, message: str, requirements: dict = None):
        details = {"requirements": requirements} if requirements else {}
        super().__init__(message, code="INVALID_RESOURCE_REQUIREMENTS", details=details)


class WalletSignatureError(RoboComputeError):
    """Wallet signature error"""
    
    def __init__(self, message: str):
        super().__init__(message, code="WALLET_SIGNATURE_INVALID")


class RateLimitError(RoboComputeError):
    """Rate limit exceeded"""
    
    def __init__(self, message: str, retry_after: int = None):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(message, code="RATE_LIMIT_EXCEEDED", details=details)


class NetworkError(RoboComputeError):
    """Network error"""
    
    def __init__(self, message: str, status_code: int = None):
        details = {"status_code": status_code} if status_code else {}
        super().__init__(message, code="NETWORK_ERROR", details=details)


class InsufficientStakeError(RoboComputeError):
    """Insufficient stake (for providers)"""
    
    def __init__(self, message: str, required: str = None, current: str = None, currency: str = None):
        details = {}
        if required:
            details["required"] = required
        if current:
            details["current"] = current
        if currency:
            details["currency"] = currency
        super().__init__(message, code="INSUFFICIENT_STAKE", details=details)


class ResourceUnavailableError(RoboComputeError):
    """Resource unavailable"""
    
    def __init__(self, message: str, resource_id: str = None):
        details = {"resource_id": resource_id} if resource_id else {}
        super().__init__(message, code="RESOURCE_UNAVAILABLE", details=details)


class TaskAlreadyAcceptedError(RoboComputeError):
    """Task already accepted"""
    
    def __init__(self, message: str, task_id: str = None):
        details = {"task_id": task_id} if task_id else {}
        super().__init__(message, code="TASK_ALREADY_ACCEPTED", details=details)


class VerificationFailedError(RoboComputeError):
    """Node verification failed"""
    
    def __init__(self, message: str):
        super().__init__(message, code="VERIFICATION_FAILED")


class SlashingEventError(RoboComputeError):
    """Slashing event (for providers)"""
    
    def __init__(self, message: str, amount: str = None):
        details = {"amount": amount} if amount else {}
        super().__init__(message, code="SLASHING_EVENT", details=details)

