import paho.mqtt.client as mqtt

import ble_ubidots.constants as c


def mqtt_publish(value):
    ''' MQTT publish message function '''
    
    print('-' * 120)
    print("\n - MQTT Publish -\n")
    
    # send a message to the device topic
    msg = '{"value":'+str(value)+'}'
    print(msg)
    client.publish(c.UBIDOTS_TOPIC, payload=msg, qos=0, retain=False)


def on_connect(client, userdata, flags, rc):
    ''' The callback for when the client receives a CONNACK response from the server '''
    
    if rc == 0:
        print("Connected success")
    else:
        print("Connected fail with code", rc)

# configure client and connect to broker
client = mqtt.Client()

client.on_connect = on_connect
client.username_pw_set(c.UBIDOTS_TOKEN, "")
client.connect(c.UBIDOTS_BROKER, 1883, 60)