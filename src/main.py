import os
import os.path
import time
from datetime import datetime
from dotenv import load_dotenv
import logging

from bluepy import btle
from googleapiclient.errors import HttpError

from ble import BLECentral
from mqtt import MQTTClient
from gdrive import GoogleDrive
from csv_logger import Logger


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


def main() -> None:
    print("""
    Project: IMS IoT gauge
    Author: Juan Garcia
    Email: <juane.garciam@upb.edu.co>
    Repository: <https://github.com/Juanes-22/ProyectoIMS>
    """)
    
    # setup logging module for debug purposes
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # setup ubidots
    ubi = MQTTClient(
        broker=APP_PARAMETERS['ubidots']['broker'],
        username=APP_PARAMETERS['ubidots']['token'],
        password="",
    )

    ubi.connect()

    # setup CSV data logger for gauge readings
    lg = Logger()
    
    # set up google drive api for csv upload
    gd = GoogleDrive(
        credentials_json_path=os.path.join(os.getcwd(), "src", "gdrive", "credentials.json")
    )

    
    # main loop
    while True:
        try:
            uploaded_file = False
            csv_created = False

            # setup BLE
            ble = BLECentral()

            # try to connect to BLE peripheral
            ble.connect_to_peripheral(
                mac_address=APP_PARAMETERS['ble']['mac_address'],
                service_uuid=APP_PARAMETERS['ble']['service_uuid']
            )

            logger_start_time = time.time()
            ubidots_start_time = time.time()
            
            # BLE connection is stablished, data reception starts
            while True:
                try:
                    # read gauge reading from BLE peripheral
                    gauge_reading = ble.read_gauge_reading(
                        char_uuid=APP_PARAMETERS['ble']['char_uuid']
                    )
                    
                    if not csv_created:
                        # setup csv file name
                        timestamp = datetime.now()
                        formated_timestamp = datetime.strftime(timestamp, "%Y-%m-%d %H %M %S")
                        lg.file_name = f"{formated_timestamp}.csv"

                        csv_created = True
                    
                    # log gauge reading to CSV file
                    if( time.time() - logger_start_time >= DATA_LOGGER_INTERVAL_IN_SECONDS ):
                        lg.collect_data(gauge_reading)
                        lg.log_data()
                        lg.print_data()
                        
                        logger_start_time = time.time()

                    # publish data to ubidots MQTT broker
                    if( time.time() - ubidots_start_time >= UBIDOTS_PUBLISH_INTERVAL_IN_SECONDS ):
                        ubi.publish(
                            msg='{"value": ' + str(gauge_reading) + '}',
                            topic=f"/v1.6/devices/{APP_PARAMETERS['ubidots']['device_label']}/{APP_PARAMETERS['ubidots']['variable_label']}"
                        )
            
                        ubidots_start_time = time.time()
                
                # BLE peripheral disconnected
                except btle.BTLEException as e:
                    # upload file to google drive
                    if uploaded_file == False:
                        file_path = os.path.join(os.getcwd(), "src", "csv_logger", "data", lg.file_name)

                        gd.upload_csv_file(
                            parents=[APP_PARAMETERS['gdrive']['parent_folder_id']],
                            file_path=file_path,
                            folder_name=APP_PARAMETERS['gdrive']['folder_name'])

                        uploaded_file = True
                    
                    # breaks the loop to start trying to connect again
                    break

                except BrokenPipeError as e:
                    # upload file to google drive
                    if uploaded_file == False:
                        file_path = os.path.join(os.getcwd(), "src", "csv_logger", "data", lg.file_name)
                        
                        gd.upload_csv_file(
                            parents=[APP_PARAMETERS['gdrive']['parent_folder_id']],
                            file_path=file_path,
                            folder_name=APP_PARAMETERS['gdrive']['folder_name'])
                        
                        uploaded_file = True
                    
                    # breaks the loop to start trying to connect again
                    break
        
        # BLE peripheral connect failed
        except btle.BTLEException as e:
            pass
        
        except BrokenPipeError as e:
            pass


if __name__ == '__main__':
    main()