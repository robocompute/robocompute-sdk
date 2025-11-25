/**
 * Пример интеграции RoboCompute с Express.js
 */

const express = require('express');
const { RoboComputeClient } = require('@robocompute/node-sdk');

const app = express();
app.use(express.json());

// Инициализация клиента
const client = new RoboComputeClient({
    apiKey: 'rc_live_your_api_key',
    walletAddress: 'YourSolanaWalletAddress',
    solanaRpc: 'https://api.mainnet-beta.solana.com'
});

// Отправка задачи
app.post('/tasks/submit', async (req, res) => {
    try {
        const task = await client.tasks.create({
            name: req.body.name,
            type: req.body.type,
            resourceRequirements: {
                cpuCores: req.body.cpu_cores,
                gpuMemoryGb: req.body.gpu_memory_gb,
                ramGb: req.body.ram_gb
            },
            dockerImage: req.body.docker_image,
            command: req.body.command,
            maxPricePerHour: req.body.max_price_per_hour // USDC
        });
        
        res.json({ task_id: task.taskId, status: task.status });
    } catch (error) {
        if (error.code === 'INSUFFICIENT_FUNDS') {
            res.status(402).json({
                error: 'Insufficient funds',
                required: error.details.required,
                available: error.details.available
            });
        } else {
            res.status(500).json({ error: error.message });
        }
    }
});

// Получение информации о задаче
app.get('/tasks/:taskId', async (req, res) => {
    try {
        const task = await client.tasks.get(req.params.taskId);
        res.json(task);
    } catch (error) {
        if (error.code === 'TASK_NOT_FOUND') {
            res.status(404).json({ error: 'Task not found' });
        } else {
            res.status(500).json({ error: error.message });
        }
    }
});

// Получение баланса
app.get('/wallet/balance', async (req, res) => {
    try {
        const balance = await client.wallet.get_balance();
        res.json(balance);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// История транзакций
app.get('/billing/history', async (req, res) => {
    try {
        const history = await client.billing.getHistory({
            startDate: req.query.start_date,
            endDate: req.query.end_date
        });
        res.json(history);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});

