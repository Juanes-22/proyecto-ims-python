import paho.mqtt.client as mqtt
import logging

class MQTTClient():
    def __init__(self, broker: str, username: str, password: str, port: int=1883) -> None:
        self.client = mqtt.Client()
        
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message

        self.broker = broker
        self.username = username
        self.password = password
        self.port = port

    def connect(self) -> None:
        try:
            self.client.username_pw_set(username=self.username, password=self.password)
            self.client.connect(self.broker, self.port)
        except Exception as e:
            logging.error("\t[MQTT] Failed to connect to broker.")

    def publish(self, topic: str, msg: str) -> None:
        try:
            self.client.publish(topic, msg)
        except Exception as e:
            logging.error("\t[MQTT] Failed to publish message.")

    def on_connect(self, client, userdata, flags, rc) -> None:
        if rc == 0:
            logging.info("\t[MQTT] Connected to broker successfully")
        else:
            logging.error(f"\t[MQTT] Failed to connect to broker. Error code: {rc}")        

    def on_publish(self, client, userdata, mid) -> None:
        logging.info(f"\t[MQTT] Message published. Message ID: {mid}")

    def on_subscribe(self, client, userdata, mid, granted_qos) -> None:
        logging.info("\t[MQTT] Subscribed to topic successfully")

    def on_message(self, client, userdata, message) -> None:
        logging.info("\t[MQTT] Received message: ", str(message.payload.decode("utf-8")))