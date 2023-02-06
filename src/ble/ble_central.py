from bluepy import btle
import logging

class BLECentral:
    def __init__(self) -> None:
        self.peripheral = None
        self.service = None

    def connect_to_peripheral(self, mac_address: str, service_uuid: str) -> None:
        try:
            logging.info("\t[BLE] Connecting...")
            self.peripheral = btle.Peripheral(mac_address)

            logging.info("\t[BLE] Discovering Services...")
            _ = self.peripheral.services
            self.service = self.peripheral.getServiceByUUID(service_uuid)
            
            logging.info("\t[BLE] Discovering Characteristics...")
            _ = self.service.getCharacteristics()
        
        except btle.BTLEException as e:
            logging.error(f"\t[BLE] {e}")
            raise e
        
        except BrokenPipeError as e:
            logging.error(f"\t[BLE] {e}")
            raise e
            
    def read_gauge_reading(self, char_uuid: str) -> float:
        try:
            """Returns temperature from BLE Service in celsius"""
            if self.service == None or self.peripheral == None:
                raise btle.BTLEException("Service or peripheral not created yet")

            gauge_reading_char = self.service.getCharacteristics(char_uuid)[0]
            gauge_reading = gauge_reading_char.read()
            gauge_reading = byte_array_to_int(gauge_reading)
            logging.info(f"\t[BLE] Gauge value: {round(gauge_reading, 2)}")
            return gauge_reading
        
        except btle.BTLEException as e:
            logging.error(f"\t[BLE] {e}")
            raise e
        
        except BrokenPipeError as e:
            logging.error(f"\t[BLE] {e}")
            raise e

    def read_temperature(self) -> float:
        try:
            """Returns temperature from BLE Service in celsius"""
            if self.service == None or self.peripheral == None:
                raise btle.BTLEException("Service or peripheral not created yet")

            temperature_char = self.service.getCharacteristics("2A6E")[0]
            temperature = temperature_char.read()
            temperature = byte_array_to_int(temperature) / 100
            logging.info(f"\t[BLE] Temperature: {round(temperature, 2)}°C")
            return temperature
        
        except btle.BTLEException as e:
            logging.error(f"\t[BLE] {e}")
            raise e
        
        except BrokenPipeError as e:
            logging.error(f"\t[BLE] {e}")
            raise e

    def read_humidity(self) -> float:
        try:
            """Returns humidity from BLE Service in porcentage"""
            if self.service == None or self.peripheral == None:
                raise btle.BTLEException("Service or peripheral not created yet")

            humidity_char = self.service.getCharacteristics("2A6F")[0]
            humidity = humidity_char.read()
            humidity = byte_array_to_int(humidity) / 100
            logging.info(f"\t[BLE] Humidity: {round(humidity, 2)}%")
            return humidity
        
        except btle.BTLEException as e:
            logging.error(f"\t[BLE] {e}")
            raise e
        
        except BrokenPipeError as e:
            logging.error(f"\t[BLE] {e}")
            raise e

    def read_pressure(self) -> float:
        try:
            """Returns pressure from BLE Service in kPa"""
            if self.service == None or self.peripheral == None:
                raise btle.BTLEException("Service or peripheral not created yet")

            pressure_char = self.service.getCharacteristics("2A6D")[0]
            pressure = pressure_char.read()
            pressure = byte_array_to_int(pressure) / 10
            logging.info(f"\t[BLE] Barometric Pressure: {round(pressure, 2)} kPa")
            return pressure / 1000
        
        except btle.BTLEException as e:
            logging.error(f"\t[BLE] {e}")
            raise e

        except BrokenPipeError as e:
            logging.error(f"\t[BLE] {e}")
            raise e


def byte_array_to_int(value: list) -> int:
    """Converts list of bytes to int"""

    # Raw data is hexstring of int values, as a series of bytes,
    # in little endian byte order values are converted from bytes -> bytearray -> int
    # e.g., b'\xb8\x08\x00\x00' -> bytearray(b'\xb8\x08\x00\x00') -> 232

    value = bytearray(value)
    return int.from_bytes(value, byteorder="little")


def byte_array_to_char(value: list) -> list:
    """Converts list of bytes to list of char"""

    # e.g., b'2660,2058,1787,4097\x00' -> 2659,2058,1785,4097
    
    return value.decode("utf-8")