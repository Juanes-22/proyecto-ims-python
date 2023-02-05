import os
import os.path
import time
from datetime import datetime
from dotenv import load_dotenv

from bluepy import btle

import ble_resources
import ubidots_resources
from csv_logger import Logger
from gdrive_exporter import GoogleDrive


# load environmental variables
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


def main():
    print("""
    Project: IMS IoT gauge
    Author: Juan Garcia
    Email: <juane.garciam@upb.edu.co>
    Repository: <https://github.com/Juanes-22/ProyectoIMS>
    """)

    # setup CSV data logger for gauge readings
    lg = Logger()
    
    # set up google drive api for log exporting
    gd = GoogleDrive()

    while True:
        try:
            csv_created = False

            # set up BLE peripheral
            print("Connecting...")
            p = btle.Peripheral(APP_PARAMETERS['ble']['mac_address'])

            print("Discovering Services...")
            _ = p.services
            gauge_service = p.getServiceByUUID(APP_PARAMETERS['ble']['service_uuid'])
            
            print("Discovering Characteristics...")
            _ = gauge_service.getCharacteristics()

            logger_start_time = time.time()
            ubidots_start_time = time.time()
            
            # BLE connection is stablished, data reception starts
            while True:
                print("\n")

                uploaded_file = False

                try:
                    gauge_value = ble_resources.read_gauge_value(gauge_service)
                    
                    if not csv_created:
                        # setup logger file name
                        timestamp = datetime.now()
                        formated_timestamp = datetime.strftime(timestamp, "%Y-%m-%d %H %M %S")
                        lg.file_name = "{}.csv".format(formated_timestamp)

                        csv_created = True
                    
                    if( time.time() - logger_start_time >= DATA_LOGGER_INTERVAL_IN_SECONDS ):
                        # log gauge reading to CSV file
                        lg.collect_data(gauge_value)
                        lg.log_data()
                        lg.print_data()
                        
                        logger_start_time = time.time()
            
                    if( time.time() - ubidots_start_time >= UBIDOTS_PUBLISH_INTERVAL_IN_SECONDS ):
                        # publish data to ubidots MQTT broker
                        ubidots_resources.mqtt_publish(gauge_value)
            
                        ubidots_start_time = time.time()
                
                except Exception as e:
                    if uploaded_file == False:
                        print(f"Failed to connect to BLE peripheral {APP_PARAMETERS.ble.mac_address}...")
                        print(e)

                        file_path = os.path.join(os.getcwd(), "src", "csv_logger", "data", lg.file_name)
                        
                        # export file to google drive
                        gd.upload_csv_file(
                            file_path,
                            [APP_PARAMETERS['gdrive']['parent_folder_id']],
                            APP_PARAMETERS['gdrive']['folder_name'])
                        
                        uploaded_file = True
                  
        except Exception as e:
            mac = APP_PARAMETERS["ble"]["mac_address"]
            print(f"Failed to connect to BLE peripheral {mac}...")
            #print(e)

if __name__ == '__main__':
    main()