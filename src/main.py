import os
import os.path
import time
from datetime import datetime
from dotenv import load_dotenv

from bluepy import btle

import ble_resources
from ubidots_resources import Ubidots
from csv_logger import Logger
from gdrive_exporter import GoogleDrive


# load environmental variables
load_dotenv()

DATA_LOGGER_INTERVAL_IN_SECONDS = 0.1
UBIDOTS_PUBLISH_INTERVAL_IN_SECONDS = 2

APP_PARAMETERS = {
    'ble': {
        'mac_address': 'de:9c:c4:f3:2c:b6',
        'service_uuid': '68D2E014-B38D-11EC-B909-0242AC120002',
        'char_uuid': '68D2E015-B38D-11EC-B909-0242AC120002',
    }, 
    'ubidots': {
        'token': os.getenv('UBIDOTS_TOKEN'),
        'device_label': 'beaglebone-green-wireless',
        'variable_label': 'strain-gauge-reading',
        'broker': 'industrial.api.ubidots.com'
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

    # setup ubidots
    ubi = Ubidots(
        token=APP_PARAMETERS['ubidots']['token'],
        broker=APP_PARAMETERS['ubidots']['broker']
    )

    # setup CSV data logger for gauge readings
    lg = Logger()
    
    # set up google drive api for log exporting
    gd = GoogleDrive()

    uploaded_file = False
    
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
                try:
                    # read gauge reading from BLE peripheral
                    gauge_reading = ble_resources.read_gauge_reading(
                        service=gauge_service,
                        char_uuid=APP_PARAMETERS['ble']['char_uuid'])

                    print(f"Gauge value: {round(gauge_reading, 2)}")
                    
                    if not csv_created:
                        # setup logger file name
                        timestamp = datetime.now()
                        formated_timestamp = datetime.strftime(timestamp, "%Y-%m-%d %H %M %S")
                        lg.file_name = "{}.csv".format(formated_timestamp)

                        csv_created = True
                    
                    if( time.time() - logger_start_time >= DATA_LOGGER_INTERVAL_IN_SECONDS ):
                        # log gauge reading to CSV file
                        lg.collect_data(gauge_reading)
                        lg.log_data()
                        lg.print_data()
                        
                        logger_start_time = time.time()
            
                    if( time.time() - ubidots_start_time >= UBIDOTS_PUBLISH_INTERVAL_IN_SECONDS ):
                        # publish data to ubidots MQTT broker
                        ubi.mqtt_publish(
                            value=gauge_reading,
                            topic=f"/v1.6/devices/{APP_PARAMETERS['ubidots']['device_label']}/{APP_PARAMETERS['ubidots']['variable_label']}"
                        )
            
                        ubidots_start_time = time.time()
                
                except btle.BTLEException as e:
                    if uploaded_file == False:
                        #print(f"Failed to connect to BLE peripheral {APP_PARAMETERS.ble.mac_address}...")
                        print(e)

                        file_path = os.path.join(os.getcwd(), "src", "csv_logger", "data", lg.file_name)
                        
                        # export file to google drive
                        gd.upload_csv_file(
                            parents=[APP_PARAMETERS['gdrive']['parent_folder_id']],
                            file_path=file_path,
                            folder_name=APP_PARAMETERS['gdrive']['folder_name'])
                        
                        uploaded_file = True
                    break
                except Exception as e:
                    print(e)
                    break

        except btle.BTLEException as e:
            mac = APP_PARAMETERS["ble"]["mac_address"]
            #print(f"Failed to connect to BLE peripheral {mac}...")
            print(e)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    main()