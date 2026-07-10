# iot.py
# IoT Sensor Integration cho SciOS Cognitive Core

import paho.mqtt.client as mqtt
import requests
from typing import Dict, Any

class IoTSensor:
    """
    IoTSensor chịu trách nhiệm:
    - Kết nối tới broker MQTT
    - Subscribe và nhận dữ liệu từ topic
    - Publish dữ liệu tới topic
    - Gửi/nhận dữ liệu qua HTTP API
    """

    def __init__(self, client_id: str = "scios_iot_client"):
        self.client_id = client_id
        self.client = mqtt.Client(client_id)
        self.latest_data = None

    # --- MQTT ---
    def connect_mqtt(self, broker: str, port: int = 1883) -> None:
        """Kết nối tới MQTT broker."""
        self.client.connect(broker, port, 60)
        print(f"Connected to MQTT broker {broker}:{port}")

    def subscribe(self, topic: str) -> None:
        """Subscribe dữ liệu từ MQTT topic."""
        def on_message(client, userdata, msg):
            self.latest_data = msg.payload.decode()
            print(f"Received from {topic}: {self.latest_data}")
        self.client.subscribe(topic)
        self.client.on_message = on_message
        self.client.loop_start()

    def publish(self, topic: str, message: str) -> None:
        """Publish dữ liệu tới MQTT topic."""
        self.client.publish(topic, message)

    # --- HTTP ---
    def get_http(self, url: str) -> Dict[str, Any]:
        """Gửi GET request tới IoT device API."""
        response = requests.get(url)
        return {"status": response.status_code, "data": response.json()}

    def post_http(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Gửi POST request tới IoT device API."""
        response = requests.post(url, json=payload)
        return {"status": response.status_code, "data": response.json()}

    def read(self) -> Dict[str, Any]:
        """Đọc dữ liệu mới nhất từ IoT sensor."""
        return {"client_id": self.client_id, "latest_data": self.latest_data}
