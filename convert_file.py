import pandas as pd
from datetime import datetime
import regex
import os
import sys


folder_root = "/home/hieung1707/Downloads"


def read_csv(file_path, delimiter=r','):
    # column_names = ['timestamp','x-axis', 'y-axis', 'z-axis','x1-axis', 'y1-axis', 'z1-axis']
    data = pd.read_csv(file_path, delimiter)
    return data


def remove_redundant_data(desired_watch_file, outputfile, skip=0):
    current_skip = 0
    report_file = '{}/VinPearl_report.csv'.format(folder_root)

    report = read_csv(report_file)

    for i in range(len(report)):
        if pd.isna(report.iloc[i]['Data_filename']):
            continue
        if report.iloc[i]['Data_filename'] != desired_watch_file.split('/')[-1]:
            continue
        print("FOUND ONE")
        if current_skip < skip:
            current_skip += 1
            continue
        data_has_decimal = False
        video_has_decimal = False
        data_starttime = report.iloc[i]['Data_starttime'].split('+')[0]
        video_starttime = report.iloc[i]['Video_starttime'].split('+')[0]
        if regex.match('\d+.\d+', data_starttime.split(':')[-1]):
            data_has_decimal = True
        if regex.match('\d+.\d+', video_starttime.split(':')[-1]):
            video_has_decimal = True
        if data_has_decimal:
            datetime_object_0 = datetime.strptime(data_starttime, '%Y-%m-%d %H:%M:%S.%f')
        else:
            datetime_object_0 = datetime.strptime(data_starttime, '%Y-%m-%d %H:%M:%S')
        if video_has_decimal:
            datetime_object_1 = datetime.strptime(video_starttime, '%Y-%m-%d %H:%M:%S.%f')
        else:
            datetime_object_1 = datetime.strptime(video_starttime, '%Y-%m-%d %H:%M:%S')
        if datetime_object_0 < datetime_object_1:
            data = read_csv(desired_watch_file)
            remove_count = 0
            for j in range(len(data)):
                timestamp = datetime.strptime(data.iloc[j]['loggingTime(txt)'], '%Y-%m-%d %H:%M:%S.%f +0700')
                if timestamp < datetime_object_1:
                    remove_count += 1
                else:
                    break
            data.drop(data.index[:remove_count], inplace=True)
            # for j in range(remove_count):
            #     data = data.drop(data.index[0])
            #     print(j)
            temp_file = '{}/temp.csv'.format(folder_root)
            data.to_csv(temp_file,header=data.columns, sep='\t', encoding='utf-8', index=False, float_format='%.6f')
            convert_timestamps_to_annotate(temp_file, outputfile)
            os.remove(temp_file)
        break



def read_videoname_to_name(video_name):
    extension_removed = video_name.split(".")[0]
    date_and_time = extension_removed.split('_')
    date = date_and_time[0][2:]
    time = date_and_time[1]
    time = '{}_{}_{}'.format(time[:2], time[2:4], time[4:6])
    return '{} {}'.format(date, time)


def convert_timestamps_to_annotate(inputfile, outputfile, delimiter='\t'):
    data = read_csv(inputfile, delimiter=delimiter)
    print(data)
    times= [0]
    for idx in range(len(data["loggingTime(txt)"])-1):
        raw_1=data["loggingTime(txt)"][idx]
        raw_2=data["loggingTime(txt)"][idx+1]
        datetime_object_0 = datetime.strptime(raw_1, '%Y-%m-%d %H:%M:%S.%f +0700')
        datetime_object_1 = datetime.strptime(raw_2, '%Y-%m-%d %H:%M:%S.%f +0700')
        diff=datetime_object_1-datetime_object_0
        times.append(times[-1]+diff.total_seconds())

    data["loggingTime(txt)"] = times
    data.to_csv(outputfile,header=data.columns, sep='\t', encoding='utf-8', index=False, float_format='%.6f')


if __name__ == "__main__":
    print(sys.argv)
    skip = 0
    if len(sys.argv) < 3:
        print('error')
        exit(0)
    if len(sys.argv) == 4:
        skip = int(sys.argv[3])
    remove_redundant_data('{}/{}'.format(folder_root, sys.argv[1]), '{}/{}'.format(folder_root, sys.argv[2]), skip)
