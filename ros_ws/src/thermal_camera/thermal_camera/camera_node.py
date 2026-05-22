import rclpy
from rclpy.node import Node

import cv2
from cv_bridge import CvBridge
from sensor_msgs.msg import Image

class ThermalCameraNode(Node):
    
    def __init__(self):
        super().__init__('thermal_camera_publisher')
        self.publisher_ = self.create_publisher(
            Image,
            '/thermal/image_raw',
            10
        )
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.cap = cv2.VideoCapture(1) # change the number to match your camera index
        if not self.cap.isOpened():
            self.get_logger().error("Could not open camera/video source")
        
        self.bridge = CvBridge()
    
    
    def timer_callback(self):
        ret, frame = self.cap.read()
        if ret:
            msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = "thermal_camera"
            
            self.publisher_.publish(msg)
            self.get_logger().info('Publishing thermal image')
        

def main():
    rclpy.init()
    thermal_camera_node = ThermalCameraNode()
    rclpy.spin(thermal_camera_node)
    thermal_camera_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
