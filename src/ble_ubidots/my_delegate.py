from bluepy import btle
from struct import *

class MyDelegate(btle.DefaultDelegate):
    unpacked_data = 0.0
    def __init__(self):
        super().__init__()

    def handleNotification(self, cHandle, data):       
        print('-' * 120)
        print("- handleNotification -\n")
        
        # received BLE data
        print("data: ", data)
        #print(type(data))
        print("data length: ", len(data))
        
        # unpack float from data bytes
        unpacked_data = unpack('f', data)
        print("unpacked data: ", unpacked_data[0])
        #print(type(unpacked_data))
        
        MyDelegate.unpacked_data = unpacked_data[0]