import csv
import os
import os.path
from pathlib import Path
from datetime import datetime

class Logger:
    def __init__(self, file_name='data.csv'):
        self.file_name = file_name
        self.data_dict = {}

    def collect_data(self, value):
        ''' collect data and assign to class '''

        self.data_dict['time_stamp'] = datetime.now()
        self.data_dict['value'] = value

    def print_data(self):
        ''' print select data in nicely formatted string '''

        ts = datetime.strftime(self.data_dict['time_stamp'], "%Y-%m-%d %H:%M:%S")
        
        print('-' * 120)
        print("- dataLogger -\n")
        print("time_stamp: {}".format(ts))
        print("value: {}".format(self.data_dict['value']))

    def log_data(self):
        ''' log the data into csv file '''

        field_names = ['time_stamp', 'value']

        if not Path(os.path.abspath(os.getcwd()) + '/src/csv_logger/data/' + self.file_name).exists():
            with open(os.path.abspath(os.getcwd()) + '/src/csv_logger/data/' + self.file_name, 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, fieldnames=field_names, delimiter=';')
                csv_writer.writeheader()

        with open(os.path.abspath(os.getcwd()) + '/src/csv_logger/data/' + self.file_name, 'a', newline='') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=field_names, delimiter=';')
            csv_writer.writerow(self.data_dict)