import os
import csv
import logging


class DataLogger:
    def __init__(self, header: list) -> None:
        self.filename = 'data.csv'
        self.header = header

        # setup logging
        self.logger = logging.getLogger('csv_logger')

    @property
    def filename(self) -> None:
        return self.filename

    @filename.setter
    def filename(self, filename: str) -> None:
        self.filepath = os.path.abspath(os.path.join('src', 'csv_logger', 'data', filename))

    def append_row(self, row: list) -> None:
        try:
            with open(self.filepath, 'a', newline='') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(row)
        except IOError as e:
            self.logger.error(f"An error occurred while saving the data: {e}")
            raise e