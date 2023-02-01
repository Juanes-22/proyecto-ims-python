import os
import os.path

import time
from datetime import datetime

from dotenv import load_dotenv

from csv_logger import Logger
import ble_ubidots

from bluepy import btle

from ble_ubidots.my_delegate import MyDelegate
import ble_ubidots.constants as c

from gdrive_exporter import GoogleDrive

load_dotenv()

DATA_LOGGER_INTERVAL_IN_SECONDS = 0.1
UBIDOTS_PUBLISH_INTERVAL_IN_SECONDS = 2

APP_PARAMETERS = {
    'ble': {
        'mac_address': '02:1c:e7:76:cd:25',
        'service_uuid': '68D2E014-B38D-11EC-B909-0242AC120002',
        'char_uuid': '68D2E015-B38D-11EC-B909-0242AC120002',
    }, 
    'ubidots': {
        'token': os.getenv('UBIDOTS_TOKEN'),
        'device_label': 'beaglebone-green-wireless',
        'variable_label': 'strain-gauge-reading'
    },
    'gdrive': {
        'parent_folder_id': os.getenv('GDRIVE_PARENT_FOLDER_ID'),
        'folder_name': 'Mediciones'
    }
}

def ble_setup():
    # setup BLE peripheral 
    p = btle.Peripheral(c.mac_address)
    p.setDelegate(MyDelegate())
    
    # setup to turn notifications on
    svc = p.getServiceByUUID(c.service_uuid)
    ch = svc.getCharacteristics(c.char_uuid)[0]
    
    setup_data = bytes(b'\x01\x00')
    p.writeCharacteristic(ch.valHandle + 1, setup_data)
    ch_data = p.readCharacteristic(ch.valHandle + 1)


def run():
    print("""
    Project: IMS IoT gauge
    Author: Juan Garcia
    Email: <juane.garciam@upb.edu.co>
    Repository: <https://github.com/Juanes-22/proyecto-ims>
    """)

    # setup CSV data logger for gauge readings
    lg = Logger()
    
    # set up google drive api
    gd = GoogleDrive()

    while True:
        try:
            csv_created = False

            # set up BLE peripheral
            ble_setup()

            logger_start_time = time.time()
            ubidots_start_time = time.time()
            
            # BLE connection is stablished, data reception starts
            while True:
                uploaded_file = False

                try:
                    # peripheral wait for central notifications
                    if p.waitForNotifications(0.01):
                        continue
                    
                    if not csv_created:
                        # setup logger file name
                        timestamp = datetime.now()
                        formated_timestamp = datetime.strftime(timestamp, "%Y-%m-%d %H %M %S")
                        lg.file_name = "{}.csv".format(formated_timestamp)

                        csv_created = True
                    
                    # received and unpacked BLE value from gauge
                    gauge_value = ble_ubidots.MyDelegate.unpacked_data
                    
                    if( time.time() - logger_start_time >= DATA_LOGGER_INTERVAL_IN_SECONDS ):
                        # log gauge reading to CSV file
                        lg.collect_data(gauge_value)
                        lg.log_data()
                        lg.print_data()
                        
                        logger_start_time = time.time()
            
                    if( time.time() - ubidots_start_time >= UBIDOTS_PUBLISH_INTERVAL_IN_SECONDS ):
                        # publish data to ubidots MQTT broker
                        ble_ubidots.mqtt_publish(gauge_value)
            
                        ubidots_start_time = time.time()
                
                except Exception as e:
                    if uploaded_file == False:
                        print(f"Failed to connect to BLE peripheral {APP_PARAMETERS.ble.mac_address}...")
                        print(e)

                        file_path = os.path.join(os.getcwd(), "src", "csv_logger", "data", lg.file_name)
                        
                        # export file to google drive
                        gd.upload_csv_file(file_path, [APP_PARAMETERS["gdrive"]["parent_folder_id"]])
                        uploaded_file = True
                  
        except Exception as e:
            mac = APP_PARAMETERS["ble"]["mac_address"]
            print(f"Failed to connect to BLE peripheral {mac}...")
            #print(e)


if __name__ == '__main__':
    run()