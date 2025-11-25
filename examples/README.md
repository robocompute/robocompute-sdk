# Examples

This directory contains example integrations and usage patterns for the RoboCompute SDK.

## Python Examples

### Basic Usage

- **[client_basic.py](./python/client_basic.py)** - Basic client usage example
- **[provider_node.py](./python/provider_node.py)** - Provider node example

### Framework Integrations

- **[fastapi_integration.py](./python/fastapi_integration.py)** - FastAPI integration
- **[flask_integration.py](./python/flask_integration.py)** - Flask integration
- **[django_integration.py](./python/django_integration.py)** - Django integration
- **[ros2_integration.py](./python/ros2_integration.py)** - ROS2 integration for robotics

## Node.js Examples

- **[express_integration.js](./nodejs/express_integration.js)** - Express.js integration
- **[nestjs_integration.ts](./nodejs/nestjs_integration.ts)** - NestJS integration

## Running Examples

### Python

```bash
# Install dependencies
pip install robocompute-sdk

# Set environment variables
export ROBOCOMPUTE_API_KEY="your_api_key"
export ROBOCOMPUTE_WALLET_ADDRESS="your_wallet_address"
export SOLANA_RPC="https://api.mainnet-beta.solana.com"

# Run example
python examples/python/client_basic.py
```

### Node.js

```bash
# Install dependencies
npm install @robocompute/node-sdk

# Set environment variables
export ROBOCOMPUTE_API_KEY="your_api_key"
export ROBOCOMPUTE_WALLET_ADDRESS="your_wallet_address"

# Run example
node examples/nodejs/express_integration.js
```

## Notes

- Replace placeholder API keys and wallet addresses with your own
- Use testnet RPC endpoints for development/testing
- Ensure your wallet has sufficient USDC/USDT balance for tasks
- For providers, ensure you have staked sufficient funds

