from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='thermal_detector',
            executable='detector_node',
            name='thermal_detector',
            output='screen',
            parameters=[
                {'model_path': 'model/best.pt'},
                {'confidence_threshold': 0.31},
                {'image_topic': '/thermal/image_raw'},
                {'detection_topic': '/thermal/detections'},
                {'overlay_topic': '/thermal/detection_overlay'},
                {'device': 'cuda'}
            ]
        )
    ])