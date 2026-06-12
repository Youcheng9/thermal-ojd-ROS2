import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import cv2
import numpy as np
from ultralytics import YOLO
from pathlib import Path

from vision_msgs.msg import Detection2DArray, Detection2D, ObjectHypothesisWithPose

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
            Detection2DArray,
            '/thermal/detections',
            10
        )
        
        self.overlay_pub = self.create_publisher(
            Image,
            '/thermal/detection_overlay',
            10
        )
        
        self.declare_parameter(
            "model_path",
            ""
        )
        
        self.declare_parameter(
            "confidence_threshold",
            0.31
        )
        
        self.model_path = self.get_parameter("model_path").value
        self.confidence_threshold = self.get_parameter("confidence_threshold").value
   

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
            model_file = Path(self.model_path)

            if not model_file.exists():
                raise FileNotFoundError(f"Model file not found: {model_file}")

            self.get_logger().info(f"Loading model: {model_file}")
            model = YOLO(str(model_file))
            self.get_logger().info("Model loaded successfully")

            return model
        except Exception as e:
            self.get_logger().error(f"Error loading model: {e}")
            return None
        
    def inference(self, frame):
        if self.model is None:
            self.get_logger().error("Model is not loaded.")
            return None
        
        result = self.model(frame, verbose=False)
        return result

    def publish_detections(self, detections, header):
        result = detections[0]
        
        detection_array = Detection2DArray()
        detection_array.header = header
        
        
        for box in result.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            if conf<self.confidence_threshold:
                continue
            
            detection = Detection2D()
            detection.bbox.center.x = (x1 + x2) / 2
            detection.bbox.center.y = (y1 + y2) / 2
            detection.bbox.size_x = x2 - x1
            detection.bbox.size_y = y2 - y1
            
            hypothesis = ObjectHypothesisWithPose()
            hypothesis.hyposthesis.class_id = str(cls_id)
            hypothesis.hypothesis.score = conf
            
            detection.results.append(hypothesis)
            detection_array.detections.append(detection)
            
            self.get_logger().info(
                f"class: {cls_id}, confidence: {conf:.2f}, "
                f"bounding box: [{x1}, {y1}, {x2}, {y2}]"
            )
            
            
            self.detection_pub.publish(detection_array)

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding='bgr8'
            )
            
            results = self.inference(frame)
            
            if results is None:
                return
            
            self.publish_detections(results, msg.header)
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
