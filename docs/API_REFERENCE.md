# API Reference

Complete API reference for RoboCompute SDK.

## Base URL

All API requests are made to: `https://robocompute.xyz/api/v1`

## Authentication

All requests require authentication using API keys and Solana wallet signatures.

### Headers

```
Authorization: Bearer {api_key}
X-Wallet-Signature: {base64_encoded_signature}
X-Timestamp: {unix_timestamp}
```

## Client API

### Tasks

#### Create Task

```python
task = client.tasks.create(
    name="Task Name",
    type="gpu",  # or "cpu"
    resource_requirements={
        "cpu_cores": 4,
        "gpu_memory_gb": 8,
        "ram_gb": 16,
        "storage_gb": 50
    },
    docker_image="your-registry/image:tag",
    command=["python", "script.py"],
    max_price_per_hour="10.00",  # USDC
    timeout_seconds=3600,
    priority="high"  # or "normal", "low"
)
```

#### Get Task

```python
task = client.tasks.get(task_id)
```

#### List Tasks

```python
tasks = client.tasks.list(
    status="running",
    limit=50,
    offset=0
)
```

#### Update Task

```python
result = client.tasks.update(
    task_id,
    max_price_per_hour="15.00",
    priority="high"
)
```

#### Cancel Task

```python
result = client.tasks.cancel(task_id)
```

#### Stream Task Updates

```python
for update in client.tasks.stream(task_id):
    print(f"Status: {update.status}, Progress: {update.progress}%")
```

#### Get Task Logs

```python
logs = client.tasks.get_logs(task_id, lines=100, follow=False)
```

#### Get Task Metrics

```python
metrics = client.tasks.get_metrics(task_id)
```

### Wallet

#### Get Balance

```python
balance = client.wallet.get_balance()
# Returns: {"usdc_balance": "1000.50", "usdt_balance": "500.25"}
```

#### Deposit Funds

```python
deposit = client.wallet.deposit(
    amount="100.00",
    currency="USDC"  # or "USDT"
)
```

### Billing

#### Get Billing History

```python
history = client.billing.get_history(
    start_date="2025-01-01",
    end_date="2025-01-31"
)
```

#### Get Invoice

```python
invoice = client.billing.get_invoice(invoice_id)
```

### Providers

#### Search Providers

```python
providers = client.providers.search(
    gpu_memory_min=8,
    cpu_cores_min=4,
    max_price=15.00,
    location="us-east"
)
```

#### Get Provider Details

```python
provider = client.providers.get(provider_id)
```

## Provider API

### Resources

#### Create Resource

```python
resource = provider.resources.create(
    resource_type="gpu",
    specifications={
        "model": "NVIDIA RTX 4090",
        "memory_gb": 24
    },
    pricing={"per_hour": "8.00"}
)
```

#### Get Resource

```python
resource = provider.resources.get(resource_id)
```

#### List Resources

```python
resources = provider.resources.list(type="gpu", status="available")
```

#### Update Resource

```python
result = provider.resources.update(
    resource_id,
    pricing={"per_hour": "10.00"},
    status="available"
)
```

#### Delete Resource

```python
result = provider.resources.delete(resource_id)
```

### Tasks

#### Accept Task

```python
result = provider.tasks.accept(task_id, resource_id="resource_123")
```

#### Start Task

```python
result = provider.tasks.start(
    task_id,
    container_id="docker_container_id",
    resource_usage={"cpu_cores": 4, "gpu_memory_gb": 8}
)
```

#### Update Progress

```python
result = provider.tasks.update_progress(
    task_id,
    progress=65,
    metrics={"cpu_usage": 85.5, "gpu_usage": 92.3}
)
```

#### Complete Task

```python
result = provider.tasks.complete(
    task_id,
    result_hash="sha256_hash",
    result_storage_url="https://storage.robocompute.xyz/results/...",
    execution_time_seconds=3600
)
```

#### Fail Task

```python
result = provider.tasks.fail(
    task_id,
    error_code="EXECUTION_ERROR",
    error_message="Container crashed"
)
```

### Earnings

#### Get Earnings Summary

```python
summary = provider.earnings.get_summary(
    start_date="2025-01-01",
    end_date="2025-01-31"
)
```

#### Request Payout

```python
payout = provider.payouts.request(
    amount="500.00",
    currency="USDC",
    wallet_address="YourSolanaWalletAddress"
)
```

#### Get Payout History

```python
history = provider.payouts.get_history(limit=50)
```

### Staking

#### Get Staking Status

```python
status = provider.staking.get_status()
```

#### Stake Funds

```python
result = provider.staking.stake(
    amount="1000.00",
    currency="USDC"
)
```

#### Unstake Funds

```python
result = provider.staking.unstake(
    amount="500.00",
    currency="USDC"
)
```

## Error Handling

All errors inherit from `RoboComputeError`:

```python
from robocompute.exceptions import (
    InsufficientFundsError,
    TaskNotFoundError,
    ProviderUnavailableError,
    AuthenticationError,
    RateLimitError
)

try:
    task = client.tasks.create(...)
except InsufficientFundsError as e:
    print(f"Insufficient funds: {e.details}")
except TaskNotFoundError as e:
    print(f"Task {e.task_id} not found")
except RateLimitError as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
```

## Rate Limits

- **Free Tier**: 100 requests/minute
- **Pro Tier**: 1000 requests/minute
- **Enterprise**: Custom limits

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit per window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Unix timestamp when limit resets

