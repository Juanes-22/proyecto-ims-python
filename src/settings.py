import os
from dotenv import load_dotenv


# load environmental variables
load_dotenv()

APP_CONFIG = {
    'BLE_CONFIG': {
        'mac_address': 'de:9c:c4:f3:2c:b6',
        'service_uuid': '68D2E014-B38D-11EC-B909-0242AC120002',
        'char_uuid': '68D2E015-B38D-11EC-B909-0242AC120002',
    }, 
    'UBIDOTS_CONFIG': {
        'token': os.getenv('UBIDOTS_TOKEN'),
        'device_label': 'beaglebone-green-wireless',
        'variable_label': 'strain-gauge-reading',
        'broker': 'industrial.api.ubidots.com',
        'publish_interval_sec': 2
    },
    'CSV_LOGGER_CONFIG': {
        'log_interval_sec': 0.1
    },
    'GDRIVE_CONFIG': {
        'parent_folder_id': os.getenv('GDRIVE_PARENT_FOLDER_ID'),
        'folder_name': 'Mediciones'
    }
}
