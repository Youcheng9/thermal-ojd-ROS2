from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='thermal_camera',
            executable='camera_node',
            name='thermal_camera',
            output='screen',
            parameters=[
                {
                    'camera_index':0,
                    'image_topic':'/thermal/image_raw',
                    'frame_id':'thermal_camera'
                }
            ]
        )
    ])