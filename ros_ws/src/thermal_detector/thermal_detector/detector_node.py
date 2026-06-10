import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from std_msgs.msg import String

import cv2
import numpy as np
# import torch
from ultralytics import YOLO



class ThermalDetectorNode(Node):
    def __init__(self):
        super().__init__('thermal_detector')
        
        #cvbridge for converting ros images to opencv images
        self.bridge = CvBridge() 
        
        self.subscription = self.create_subscription(
            Image,
            '/thermal/image_raw',
            self.image_callback,
            10
        )
        
        self.get_logger().info("Thermal Detector Node has been started.")
        
        self.detection_pub = self.create_publisher(
            String,
            '/thermal/detections',
            10
        )
        
        
    def load_model(self):
        # model inference block
        try:
            self.model = YOLO(model_path)
        except Exception as e:
            self.get_logger().error(f"Error loading model: {e}")
        
    def inference(self, frame):
        result = self.model(frame)
        return result

    def publish_detections(self, detections):
        result = detections[0]
        
        for box in result.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            self.get_logger().info(
                f"Detected class {cls_id} with confidence {conf:.2f} at [{x1}, {y1}, {x2}, {y2}]"
                )
        
    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding='bgr8'
            )
            
            results = self.inference(frame)
            self.publish_detections(results)
            
        except Exception as e:
            self.get_logger().error(f'Detection error: {e}')
            return
        
        msg_out = String()
        msg_out.data = "frame received"
        self.detection_pub.publish(msg_out)

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
