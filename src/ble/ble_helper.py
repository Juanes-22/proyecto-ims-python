from bluepy import btle


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


def read_gauge_reading(service: btle.Service, char_uuid: str) -> float:
    """Returns temperature from BLE Service in celsius"""
    gauge_reading_char = service.getCharacteristics(char_uuid)[0]
    gauge_reading = gauge_reading_char.read()
    gauge_reading = byte_array_to_int(gauge_reading)
    logging.info(f"Gauge value: {round(gauge_reading, 2)}")
    return gauge_reading


def read_temperature(service: btle.Service) -> float:
    """Returns temperature from BLE Service in celsius"""
    temperature_char = service.getCharacteristics("2A6E")[0]
    temperature = temperature_char.read()
    temperature = byte_array_to_int(temperature) / 100
    logging.info(f"Temperature: {round(temperature, 2)}°C")
    return temperature


def read_humidity(service: btle.Service) -> float:
    """Returns humidity from BLE Service in porcentage"""
    humidity_char = service.getCharacteristics("2A6F")[0]
    humidity = humidity_char.read()
    humidity = byte_array_to_int(humidity) / 100
    logging.info(f"Humidity: {round(humidity, 2)}%")
    return humidity


def read_pressure(service: btle.Service) -> float:
    """Returns pressure from BLE Service in kPa"""
    pressure_char = service.getCharacteristics("2A6D")[0]
    pressure = pressure_char.read()
    pressure = byte_array_to_int(pressure) / 10
    logging.info(f"Barometric Pressure: {round(pressure, 2)} kPa")
    return pressure / 1000
