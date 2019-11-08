import pandas as pd
import argparse

report = pd.read_csv('VinPearl_report.csv')
print(report.head())

video_names = open('video_names.txt', 'r').readlines()

parser = argparse.ArgumentParser(description='Map video and data filename.')
parser.add_argument('camera_id', type=int, help='Camera_ID')

args = parser.parse_args()

camera_id = 'P_00{}'.format(args.camera_id)

names = report[report['Camera_ID'] == camera_id][['Video_filename', 'Data_filename']]
print(names)

names.to_csv('mapped_data.csv')