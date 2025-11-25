# RoboCompute SDK

Official SDK for interacting with the RoboCompute decentralized computing platform. Rent computational power for robots and AI, or provide resources and earn Solana stablecoins (USDC/USDT).

## Features

- 🚀 **Easy Integration** - Simple API for submitting and managing compute tasks
- 💰 **Solana Integration** - Native support for USDC/USDT payments
- 🔒 **Secure** - Wallet signature authentication
- 📊 **Real-time Monitoring** - WebSocket support for task updates
- 🌐 **Multi-language** - Python, Node.js, Go, Rust, C++ support
- 🤖 **Robot Ready** - ROS2 integration for robotics applications

## Installation

### Python

```bash
pip install robocompute-sdk
```

### Node.js

```bash
npm install @robocompute/node-sdk
```

### Go

```bash
go get github.com/robocompute/go-sdk
```

## Quick Start

### Python - Client (Rent Compute)

```python
from robocompute import RoboComputeClient
from solana.rpc.api import Client

# Initialize client
client = RoboComputeClient(
    api_key="rc_live_your_api_key",
    wallet_address="YourSolanaWalletAddress",
    solana_rpc="https://api.mainnet-beta.solana.com"
)

# Submit a task
task = client.tasks.create(
    name="Object Detection",
    type="gpu",
    resource_requirements={
        "cpu_cores": 4,
        "gpu_memory_gb": 8,
        "ram_gb": 16
    },
    docker_image="your-registry/image:tag",
    command=["python", "detect.py"],
    max_price_per_hour="10.00"  # USDC
)

# Monitor task progress
for update in client.tasks.stream(task.task_id):
    print(f"Status: {update.status}, Progress: {update.progress}%")
    if update.status == "completed":
        results = client.tasks.get_results(task.task_id)
        break
```

### Python - Provider (Share Compute)

```python
from robocompute.provider import RoboComputeProvider

# Initialize provider
provider = RoboComputeProvider(
    api_key="rc_prov_live_your_api_key",
    provider_id="provider_xyz789",
    wallet_address="YourSolanaWalletAddress",
    solana_rpc="https://api.mainnet-beta.solana.com"
)

# Register resources
resource = provider.resources.create(
    resource_type="gpu",
    specifications={
        "model": "NVIDIA RTX 4090",
        "memory_gb": 24
    },
    pricing={"per_hour": "8.00"}  # USDC
)

# Listen for tasks
@provider.on_task_assigned
def handle_task(task):
    provider.tasks.accept(task.task_id)
    provider.tasks.start(task.task_id)
    result = execute_task(task)
    provider.tasks.complete(task.task_id, result)

# Start provider node
provider.start()
```

### Node.js - Client

```javascript
const { RoboComputeClient } = require('@robocompute/node-sdk');

const client = new RoboComputeClient({
    apiKey: 'rc_live_your_api_key',
    walletAddress: 'YourSolanaWalletAddress',
    solanaRpc: 'https://api.mainnet-beta.solana.com'
});

// Submit task
const task = await client.tasks.create({
    name: 'Object Detection',
    type: 'gpu',
    resourceRequirements: {
        cpuCores: 4,
        gpuMemoryGb: 8,
        ramGb: 16
    },
    dockerImage: 'your-registry/image:tag',
    command: ['python', 'detect.py'],
    maxPricePerHour: '10.00' // USDC
});

// Monitor task
client.tasks.stream(task.taskId, (update) => {
    console.log(`Status: ${update.status}, Progress: ${update.progress}%`);
});
```

## API Reference

### Client API

#### Tasks

- `client.tasks.create(**kwargs)` - Submit a new compute task
- `client.tasks.get(task_id)` - Get task details
- `client.tasks.list(**filters)` - List all tasks
- `client.tasks.update(task_id, **updates)` - Update task parameters
- `client.tasks.cancel(task_id)` - Cancel a task
- `client.tasks.stream(task_id)` - Stream task updates via WebSocket
- `client.tasks.get_logs(task_id)` - Get task execution logs
- `client.tasks.get_metrics(task_id)` - Get task performance metrics

#### Wallet

- `client.wallet.get_balance()` - Check USDC/USDT balance
- `client.wallet.deposit(amount, currency)` - Deposit funds

#### Billing

- `client.billing.get_history(**filters)` - Get billing history
- `client.billing.get_invoice(invoice_id)` - Get invoice details

#### Providers

- `client.providers.search(**filters)` - Search for providers
- `client.providers.get(provider_id)` - Get provider details

### Provider API

#### Resources

- `provider.resources.create(**kwargs)` - Register a resource
- `provider.resources.get(resource_id)` - Get resource details
- `provider.resources.list(**filters)` - List all resources
- `provider.resources.update(resource_id, **updates)` - Update resource
- `provider.resources.delete(resource_id)` - Remove resource

#### Tasks

- `provider.tasks.accept(task_id)` - Accept a task
- `provider.tasks.start(task_id)` - Start task execution
- `provider.tasks.update_progress(task_id, progress, metrics)` - Update progress
- `provider.tasks.complete(task_id, result)` - Complete task
- `provider.tasks.fail(task_id, error)` - Report task failure

#### Earnings

- `provider.earnings.get_summary(**filters)` - Get earnings summary
- `provider.payouts.request(amount, currency)` - Request payout
- `provider.payouts.get_history(**filters)` - Get payout history

#### Staking

- `provider.staking.get_status()` - Check staking status
- `provider.staking.stake(amount, currency)` - Stake funds
- `provider.staking.unstake(amount, currency)` - Unstake funds

## API Configuration

API base domain: `robocompute.xyz/api/`

All API requests are made to the `robocompute.xyz/api/` domain. The SDK automatically uses this domain by default.

## Authentication

All API requests require authentication using API keys and Solana wallet signatures.

1. Register at [RoboCompute Dashboard](https://robocompute.xyz)
2. Get your API key
3. Configure your Solana wallet address
4. Ensure your wallet has USDC/USDT for payments

## Payment

RoboCompute uses Solana stablecoins (USDC/USDT) for all transactions:

- **Clients**: Pay for compute tasks in USDC/USDT
- **Providers**: Earn USDC/USDT for providing resources
- **Staking**: Providers must stake USDC/USDT as collateral

## Examples

See the [examples](./examples/) directory for complete examples:

- [Basic Task Submission](./examples/python/client_basic.py)
- [FastAPI Integration](./examples/python/fastapi_integration.py)
- [Flask Integration](./examples/python/flask_integration.py)
- [Provider Node](./examples/python/provider_node.py)
- [ROS2 Integration](./examples/python/ros2_integration.py)
- [Express.js Integration](./examples/nodejs/express_integration.js)
- [NestJS Integration](./examples/nodejs/nestjs_integration.ts)

## Framework Integrations

### FastAPI

```python
from fastapi import FastAPI
from robocompute import RoboComputeClient

app = FastAPI()
client = RoboComputeClient(api_key="...", wallet_address="...")

@app.post("/tasks/submit")
async def submit_task(task_data: dict):
    task = client.tasks.create(**task_data)
    return {"task_id": task.task_id, "status": task.status}
```

### Flask

```python
from flask import Flask, request, jsonify
from robocompute import RoboComputeClient

app = Flask(__name__)
client = RoboComputeClient(api_key="...", wallet_address="...")

@app.route('/tasks/submit', methods=['POST'])
def submit_task():
    task = client.tasks.create(**request.json)
    return jsonify({"task_id": task.task_id, "status": task.status})
```

### Express.js

```javascript
const express = require('express');
const { RoboComputeClient } = require('@robocompute/node-sdk');

const app = express();
const client = new RoboComputeClient({ apiKey: '...', walletAddress: '...' });

app.post('/tasks/submit', async (req, res) => {
    const task = await client.tasks.create(req.body);
    res.json({ task_id: task.taskId, status: task.status });
});
```

## Error Handling

```python
from robocompute.exceptions import (
    InsufficientFundsError,
    TaskNotFoundError,
    ProviderUnavailableError
)

try:
    task = client.tasks.create(...)
except InsufficientFundsError as e:
    print(f"Insufficient funds: {e.details}")
except TaskNotFoundError:
    print("Task not found")
```

## Rate Limits

- **Free Tier**: 100 requests/minute
- **Pro Tier**: 1000 requests/minute
- **Enterprise**: Custom limits

## Documentation

- 📖 [API Reference](./docs/API_REFERENCE.md) - Complete API reference
- 🌐 [Client Documentation](https://robocompute.xyz/clients) - Client API docs
- 🔧 [Provider Documentation](https://robocompute.xyz/providers) - Provider API docs

## License

MIT License - see [LICENSE](./LICENSE) file for details.

## Contributing

Contributions are welcome! Please read our [Contributing Guide](./CONTRIBUTING.md) for details.

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for a list of changes.
