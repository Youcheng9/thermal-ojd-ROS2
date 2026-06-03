import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class ThermalDetectorNode(Node):
    def __init__(self):
        super.__init__('thermal_detector')
        
        self.bridge = CvBridge()
        
        self.subscription = self.create_subscription(
            Image,
            '/thermal/image_raw/',
            self.image_callback,
            10
        )
        
    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding='bgr8'
        )
        
        self.get_logger().info(
            f"Received frame: {frame.shape}"
        )
        
    def main(args=None):
        rclpy.init(args=args)
        
        node = ThermalDetectorNode()
        
        try:
            rclpy.spin(node)
        except KeyboardInterrupt:
            pass

        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
