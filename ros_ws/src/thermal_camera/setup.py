from setuptools import find_packages, setup

package_name = 'thermal_camera'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Youcheng',
    maintainer_email='youchengtaing9999@gmail.com',
    description='Thermal Object Detection with ROS2',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'camera_node = thermal_camera.camera_node:main'
        ],
    },
)
