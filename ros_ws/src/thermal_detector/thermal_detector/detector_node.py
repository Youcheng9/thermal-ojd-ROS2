import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from std_msgs.msg import String

import cv2
import numpy as np
# import torch
from ultralytics import YOLO

"""
Thermal Detector Node
This node subscribes to the thermal image topic, performs object detection using a YOLO model, and publishes the detection results.
"""


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
        
        self.overlay_pub = self.create_publisher(
            Image,
            '/thermal/detection_overlay',
            10
        )
        
        def publish_overlay(self, detections, frame):
            overlay = detections[0].plot()

            overlay_msg = self.bridge.cv2_to_imgmsg(
                overlay,
                encoding='bgr8'
            )
            
            overlay_sg.header = header
            self.overlay_pub.publish(overlay_msg)
        
    def load_model(self):
        # model inference block
        try:
            self.model = YOLO(model_path)
            self.get_logger().info("Model loaded successfully.")
            return self.model
        except Exception as e:
            self.get_logger().error(f"Error loading model: {e}")
        
    def inference(self, frame):
        if self.model is None:
            self.get_logger().error("Model is not loaded.")
            return None
        
        result = self.model(frame)
        return result

    def publish_detections(self, detections):
        result = detections[0]
        record = []
        
        for box in result.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            message = (
                f"class: {cls_id}, confidence: {conf:.2f}, "
                f"bounding box: [{x1}, {y1}, {x2}, {y2}]"
            )
            record.append(message)
            self.get_logger().info(
                message
                )
            
            msg_out = String()
            msg_out.data = "\n".join(record) if record else "No detections"
            self.detection_pub.publish(msg_out)

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding='bgr8'
            )
            
            results = self.inference(frame)
            
            if results is None:
                return
            
            self.publish_detections(results)
            self.publish_overlay(results, msg.header)
            
        except Exception as e:
            self.get_logger().error(f'Detection error: {e}')
            return
        

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
