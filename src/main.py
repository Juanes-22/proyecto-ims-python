import os
import os.path
import time
from datetime import datetime

from bluepy import btle

import setup_logging
from settings import APP_CONFIG
from ble.central import BLECentral
from mqtt.client import MQTTClient
from gdrive.client import GoogleDrive
from csv_logger.logger import DataLogger


def main() -> None:
    print("""
    Project: IMS IoT gauge
    Author: Juan Garcia
    Email: <juane.garciam@upb.edu.co>
    Repository: <https://github.com/Juanes-22/proyecto-ims-python>
    """)
   
    # setup ubidots
    ubi = MQTTClient(
        broker=APP_CONFIG['UBIDOTS_CONFIG']['broker'],
        username=APP_CONFIG['UBIDOTS_CONFIG']['token'],
        password="",
    )

    ubi.wait_for_connection()

    # setup CSV data logger for gauge readings
    lg = DataLogger(
        header=['time_stamp', 'value']
    )
    
    # set up google drive api for csv upload
    gd = GoogleDrive(
        credentials_json_path=os.path.abspath(os.path.join("src", "gdrive", "credentials.json"))
    )

    time.sleep(3)

    # main loop
    while True:
        try:
            uploaded_file = False
            csv_created = False

            # setup BLE
            ble = BLECentral()

            # try to connect to BLE peripheral
            ble.connect_to_peripheral(
                mac_address=APP_CONFIG['BLE_CONFIG']['mac_address'],
                service_uuid=APP_CONFIG['BLE_CONFIG']['service_uuid']
            )

            logger_start_time = time.time()
            ubidots_start_time = time.time()
            
            # BLE connection is stablished, data reception starts
            while True:
                try:
                    # read gauge reading from BLE peripheral
                    gauge_reading = ble.read_gauge_reading(
                        char_uuid=APP_CONFIG['BLE_CONFIG']['char_uuid']
                    )
                    
                    if not csv_created:
                        # setup csv file name
                        timestamp = datetime.now()
                        formated_timestamp = datetime.strftime(timestamp, "%Y-%m-%d %H %M %S")
                        lg.filename = f"{formated_timestamp}.csv"

                        csv_created = True
                    
                    # log gauge reading to CSV file
                    if( time.time() - logger_start_time >= APP_CONFIG['CSV_LOGGER_CONFIG']['log_interval_sec'] ):
                        timestamp = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")                        
                        lg.append_row([timestamp, gauge_reading])

                        logger_start_time = time.time()

                    # publish data to ubidots MQTT broker
                    if( time.time() - ubidots_start_time >= APP_CONFIG['UBIDOTS_CONFIG']['publish_interval_sec'] ):
                        ubi.publish(
                            payload='{"value": ' + str(gauge_reading) + '}',
                            topic=f"/v1.6/devices/{APP_CONFIG['UBIDOTS_CONFIG']['device_label']}/{APP_CONFIG['UBIDOTS_CONFIG']['variable_label']}"
                        )
            
                        ubidots_start_time = time.time()
                
                # BLE peripheral disconnected
                except btle.BTLEException as e:
                    # upload file to google drive
                    if uploaded_file == False:
                        gd.upload_csv_file(
                            parents=[APP_CONFIG['GDRIVE_CONFIG']['parent_folder_id']],
                            file_path=lg.filepath,
                            folder_name=APP_CONFIG['GDRIVE_CONFIG']['folder_name'])

                        uploaded_file = True
                    
                    time.sleep(5)

                    # breaks the loop to start trying to connect again
                    break

                except BrokenPipeError as e:
                    # upload file to google drive
                    if uploaded_file == False:
                        gd.upload_csv_file(
                            parents=[APP_CONFIG['GDRIVE_CONFIG']['parent_folder_id']],
                            file_path=lg.filepath,
                            folder_name=APP_CONFIG['GDRIVE_CONFIG']['folder_name'])
                        
                        uploaded_file = True
                    
                    time.sleep(5)

                    # breaks the loop to start trying to connect again
                    break
        
        # BLE peripheral connect failed
        except btle.BTLEException as e:
            pass
        
        except BrokenPipeError as e:
            pass

        except Exception as e:
            time.sleep(5)
            pass


if __name__ == '__main__':
    main()
