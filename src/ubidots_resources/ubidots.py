import paho.mqtt.client as mqtt

class Ubidots():
  def __init__(self, token: str, broker: str):
    self.client = mqtt.Client()

    self.client.username_pw_set(token, "")
    self.client.connect(broker, 1883, 60)

  def mqtt_publish(self, topic: str, value: float):
    ''' MQTT publish message function '''
    
    print('-' * 120)
    print("\n - MQTT Publish -\n")
    
    # send a message to the device topic
    msg = '{"value":'+str(value)+'}'
    print(msg)
    self.client.publish(topic, payload=msg, qos=0, retain=False)
