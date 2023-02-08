import os
import csv
import logging


class DataLogger:
    def __init__(self, header: list, filename: str='data.csv') -> None:
        self._header = header
        self._filename = filename
        self._filepath = os.path.abspath(os.path.join('src', 'csv_logger', 'data', self._filename))

        # setup logging
        self._logger = logging.getLogger('csv_logger')
        self._logger.info(f"Data logger initialized with header: {header} and filename: {filename}")

    @property
    def filename(self) -> str:
        return self._filename

    @filename.setter
    def filename(self, filename: str) -> None:
        self._filename = filename
        self._filepath = os.path.abspath(os.path.join('src', 'csv_logger', 'data', self._filename))
        self._logger.info(f"Filename set: {filename}")

    @property
    def filepath(self) -> str:
        return self._filepath

    def append_row(self, row: list) -> None:
        try:
            mode = 'a' if os.path.isfile(self._filepath) else 'w'
            with open(self._filepath, mode, newline='') as file:
                writer = csv.writer(file, delimiter=';')
                if mode == 'w':
                    writer.writerow(self._header)
                writer.writerow(row)
        except IOError as e:
            self._logger.error(f"An error occurred while saving the data: {e}")
            raise e
