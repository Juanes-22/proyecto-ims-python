import paho.mqtt.client as mqtt
import logging
import time
import socket

class MQTTClient():
    def __init__(self, broker: str, port: int=1883, username: str=None, password: str=None):
        self.client = mqtt.Client()
        
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message

        self._broker = broker
        self._port = port
        self._username = username
        self._password = password

        self.connected_flag = False
        self.retry_interval = 5

        # setup logging
        self._logger = logging.getLogger('mqtt')


    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._logger.info("Connected to MQTT broker")
            self.connected_flag = True
        else:
            self._logger.info(f"Connection to MQTT broker failed with result code: {rc}")


    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            self._logger.error("Unexpected disconnection from MQTT broker. Attempting to reconnect...")
            self.connected_flag = False
            self.start()       
    
    
    def start(self):
        self.client.username_pw_set(self._username, self._password)

        try:
            self.client.connect(self._broker, self._port)
        except ConnectionRefusedError:
            self._logger.error(f"Error: Connection to MQTT broker refused. Retrying in {self.retry_interval} seconds...")
            time.sleep(self.retry_interval)
            self.start()
        except OSError as e:
            self._logger.error(f"Error: Network is unreachable. Retrying in {self.retry_interval} seconds...")
            time.sleep(self.retry_interval)
            self.start()
        except socket.gaierror as e:
            self._logger.error(f"Error: Network is unreachable. Retrying in {self.retry_interval} seconds...")
            time.sleep(self.retry_interval)
            self.start()

        self.client.loop_start()

    def publish(self, topic: str, payload: str):
        self.client.publish(topic, payload)


    def subscribe(self, topic: str):
        self.client.subscribe(topic) 


    def on_publish(self, client, userdata, mid):
        self._logger.info(f"Message published. Message ID: {mid}")


    def on_subscribe(self, client, userdata, mid, granted_qos):
        self._logger.info("Subscribed to topic successfully")


    def on_message(self, client, userdata, message):
        self._logger.info("Received message: {}".format(message.payload.decode("utf-8")))


    def wait_for_connection(self):
        while not self.connected_flag:
            time.sleep(self.retry_interval)
            self.start()


    def __str__(self) -> str:
        return f"MQTT Client connected to broker at {self._broker}:{self._port}"