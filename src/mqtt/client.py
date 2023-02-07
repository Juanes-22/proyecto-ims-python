import paho.mqtt.client as mqtt
import logging


class MQTTClient():
    def __init__(self) -> None:
        self.client = mqtt.Client()
        self.client.connected_flag = False
        
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message

        # setup logging
        self.logger = logging.getLogger('mqtt')

    def connect(self, broker: str, username: str, password: str, port: int=1883) -> None:
        try:
            self.client.username_pw_set(username=username, password=password)
            self.client.connect(broker, port)
            self.client.loop_start()
        except Exception as e:
            self.logger.error("Failed to connect to broker...")

    def publish(self, topic: str, msg: str) -> None:
        try:
            self.client.publish(topic, msg)
        except Exception as e:
            self.logger.error("Failed to publish message.")

    def on_connect(self, client, userdata, flags, rc) -> None:
        if rc == 0:
            self.logger.info("Connected to broker successfully")
            self.client.connected_flag = True
        else:
            self.logger.error(f"Failed to connect to broker. Error code: {rc}")        

    def on_disconnect(self, client, userdata, rc) -> None:
        self.logger.error(f"Disconnected with result code {rc}")
        self.client.connected_flag = False
        self.client.reconnect()

    def on_publish(self, client, userdata, mid) -> None:
        self.logger.info(f"Message published. Message ID: {mid}")

    def on_subscribe(self, client, userdata, mid, granted_qos) -> None:
        self.logger.info("Subscribed to topic successfully")

    def on_message(self, client, userdata, message) -> None:
        self.logger.info("Received message: {}".format(message.payload.decode("utf-8")))