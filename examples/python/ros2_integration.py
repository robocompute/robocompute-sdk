"""
Example of RoboCompute integration with ROS2
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from robocompute import RoboComputeClient


class RoboComputeROS2Node(Node):
    """ROS2 node for RoboCompute integration"""
    
    def __init__(self):
        super().__init__('robocompute_node')
        
        # Initialize client
        self.client = RoboComputeClient(
            api_key="rc_live_your_api_key",
            wallet_address="YourSolanaWalletAddress",
            solana_rpc="https://api.mainnet-beta.solana.com"
        )
        
        # Subscribe to compute requests
        self.compute_subscription = self.create_subscription(
            String,
            'compute_request',
            self.compute_request_callback,
            10
        )
        
        # Publish task status
        self.status_publisher = self.create_publisher(String, 'task_status', 10)
        
        self.get_logger().info('RoboCompute ROS2 node started')
    
    def compute_request_callback(self, msg):
        """Handle compute request"""
        request_data = eval(msg.data)  # In reality use JSON
        
        self.get_logger().info(f'Received compute request: {request_data["name"]}')
        
        # Submit task to RoboCompute
        task = self.client.tasks.create(
            name=request_data["name"],
            type=request_data.get("type", "gpu"),
            resource_requirements=request_data["resource_requirements"],
            docker_image=request_data["docker_image"],
            command=request_data["command"],
            max_price_per_hour=request_data.get("max_price_per_hour", "10.00")
        )
        
        self.get_logger().info(f'Task submitted: {task["task_id"]}')
        
        # Monitor task
        self.monitor_task(task["task_id"])
    
    def monitor_task(self, task_id):
        """Monitor task and publish status"""
        for update in self.client.tasks.stream(task_id):
            status_msg = String()
            status_msg.data = f"{task_id}:{update.get('status')}:{update.get('progress', 0)}"
            self.status_publisher.publish(status_msg)
            
            if update.get('status') == 'completed':
                results = self.client.tasks.get_results(task_id)
                self.get_logger().info(f'Task {task_id} completed: {results}')
                break


def main(args=None):
    rclpy.init(args=args)
    node = RoboComputeROS2Node()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

