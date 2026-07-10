# ros.py
# ROS Sensor Integration cho SciOS Cognitive Core

import rospy
from std_msgs.msg import String
from typing import Dict

class ROSSensor:
    """
    ROSSensor chịu trách nhiệm:
    - Kết nối tới ROS node
    - Subscribe dữ liệu từ topic
    - Publish dữ liệu tới topic
    """

    def __init__(self, node_name: str = "scios_sensor_node"):
        self.node_name = node_name
        self.publisher = None
        self.subscriber = None
        self.latest_data = None

    def initialize(self) -> None:
        """Khởi tạo ROS node."""
        rospy.init_node(self.node_name, anonymous=True)
        print(f"ROS node {self.node_name} initialized.")

    def subscribe(self, topic: str, msg_type=String) -> None:
        """Subscribe dữ liệu từ topic."""
        def callback(data):
            self.latest_data = data.data
            rospy.loginfo(f"Received data: {self.latest_data}")
        self.subscriber = rospy.Subscriber(topic, msg_type, callback)

    def publish(self, topic: str, msg: str, msg_type=String) -> None:
        """Publish dữ liệu tới topic."""
        self.publisher = rospy.Publisher(topic, msg_type, queue_size=10)
        rate = rospy.Rate(10)  # 10 Hz
        while not rospy.is_shutdown():
            self.publisher.publish(msg)
            rate.sleep()

    def read(self) -> Dict:
        """Đọc dữ liệu mới nhất từ subscriber."""
        return {"node": self.node_name, "latest_data": self.latest_data}
