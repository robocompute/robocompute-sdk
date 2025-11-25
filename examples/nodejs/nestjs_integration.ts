/**
 * Пример интеграции RoboCompute с NestJS
 */

import { Controller, Post, Get, Body, Param, Query } from '@nestjs/common';
import { RoboComputeClient } from '@robocompute/nestjs';
import { Connection } from '@solana/web3.js';

@Controller('tasks')
export class TasksController {
    private client: RoboComputeClient;

    constructor() {
        this.client = new RoboComputeClient({
            apiKey: 'rc_live_your_api_key',
            walletAddress: 'YourSolanaWalletAddress',
            solanaRpc: 'https://api.mainnet-beta.solana.com'
        });
    }

    @Post('submit')
    async submitTask(@Body() taskData: any) {
        try {
            const task = await this.client.tasks.create({
                name: taskData.name,
                type: taskData.type,
                resourceRequirements: {
                    cpuCores: taskData.cpu_cores,
                    gpuMemoryGb: taskData.gpu_memory_gb,
                    ramGb: taskData.ram_gb
                },
                dockerImage: taskData.docker_image,
                command: taskData.command,
                maxPricePerHour: taskData.max_price_per_hour // USDC
            });
            
            return { task_id: task.taskId, status: task.status };
        } catch (error) {
            if (error.code === 'INSUFFICIENT_FUNDS') {
                throw new Error(`Insufficient funds: ${error.details.required} required, ${error.details.available} available`);
            }
            throw error;
        }
    }

    @Get(':taskId')
    async getTask(@Param('taskId') taskId: string) {
        return await this.client.tasks.get(taskId);
    }
}

@Controller('wallet')
export class WalletController {
    private client: RoboComputeClient;

    constructor() {
        this.client = new RoboComputeClient({
            apiKey: 'rc_live_your_api_key',
            walletAddress: 'YourSolanaWalletAddress',
            solanaRpc: 'https://api.mainnet-beta.solana.com'
        });
    }

    @Get('balance')
    async getBalance() {
        return await this.client.wallet.getBalance();
    }
}

@Controller('billing')
export class BillingController {
    private client: RoboComputeClient;

    constructor() {
        this.client = new RoboComputeClient({
            apiKey: 'rc_live_your_api_key',
            walletAddress: 'YourSolanaWalletAddress',
            solanaRpc: 'https://api.mainnet-beta.solana.com'
        });
    }

    @Get('history')
    async getHistory(
        @Query('start_date') startDate?: string,
        @Query('end_date') endDate?: string
    ) {
        return await this.client.billing.getHistory({
            startDate,
            endDate
        });
    }
}

