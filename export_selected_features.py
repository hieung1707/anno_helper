import pandas as pd
import sys
import numpy as np
import glob
import os
import re


label_dict = {
    'DG': 1,
    'LN2': 2,
    'LC2': 3,
    'MD': 4
}
pattern1 = '<LINKED_FILE_DESCRIPTOR.*TIME_ORIGIN=\"(\d+)\".*/>'
pattern2 = '<MEDIA_DESCRIPTOR.*TIME_ORIGIN=\"(\d+)\".*/>'


def get_time_offset(eaf_file):
    eaf = open(eaf_file, 'r')
    lines = eaf.readlines()
    for line in lines:
        result = re.search(pattern1, line)
        if result is not None:
            return int(result.group(1)) * 1. / 1000
        result = re.search(pattern2, line)
        if result is not None:
            return int('-' + result.group(1)) * 1. / 1000
    return 0


def get_labels(timestamps_txt, time_offset, n_samples, df):
    time_domain = 'accelerometerTimestamp_sinceReboot(s)'
    txt_file = open(timestamps_txt, "r")
    lines = txt_file.readlines()
    labels_np = np.zeros(n_samples, dtype=np.int16)
    for i, line in enumerate(lines):
        if i == 0:
            continue
        line = line.replace('\t\n', '')
        line = line.replace('\n', '')
        info = line.split('\t')
        start = float(info[0])
        end = float(info[1])
        label = label_dict[info[2]]
        filter_df1 = df[time_domain] >= (start + time_offset)
        filter_df2 = df[time_domain] <= (end + time_offset)
        data = df.where(filter_df1 & filter_df2, inplace=False)
        data.dropna(inplace=True, how='all')
        indices = data.index
        start_idx = indices[0]
        end_idx = indices[-1]
        labels_np[start_idx:end_idx] = label
    return labels_np


def get_label_data(input_file, timestamps_txt, output_file, time_offset=0):

    df = pd.read_csv(input_file, delimiter='\t')
    df['accelerometerTimestamp_sinceReboot(s)'] = df['accelerometerTimestamp_sinceReboot(s)'].round(decimals=11)
    output = df[['accelerometerTimestamp_sinceReboot(s)',
                 'accelerometerAccelerationX(G)',
                 'accelerometerAccelerationY(G)',
                 'accelerometerAccelerationZ(G)',
                 'motionRotationRateX(rad/s)',
                 'motionRotationRateY(rad/s)',
                 'motionRotationRateZ(rad/s)']]
    labels_np = get_labels(timestamps_txt, time_offset, len(output), output)
    output['label'] = labels_np
    output.to_csv(output_file, sep='\t', header=None, encoding='utf-8', index=False)


if __name__ == "__main__":
    # folders = glob.glob('/home/hieung1707/Downloads/data_11_11_19/part2/*')
    # label_dir = '/home/hieung1707/labels'
    # if not os.path.exists(label_dir):
    #     os.mkdir(label_dir)
    # for folder in folders:
    #     folder_name = folder.split('/')[-1]
    #     eaf_file = glob.glob('{}/*.eaf'.format(folder))[0]
    #     time_offset = get_time_offset(eaf_file)
    #     print(time_offset)
    #     data_50hz = glob.glob('{}/W01*.csv'.format(folder))[0]
    #     data_other = glob.glob('{}/W02*.csv'.format(folder))[0]
    #     if not os.path.exists('{}/{}'.format(label_dir, folder_name)):
    #         os.mkdir('{}/{}'.format(label_dir, folder_name))
    #     get_label_data(data_50hz, '{}/{}.txt'.format(folder, folder_name), '{}/{}/label1.txt'.format(label_dir, folder_name), time_offset)
    #     get_label_data(data_other, '{}/{}.txt'.format(folder, folder_name), '{}/{}/label2.txt'.format(label_dir, folder_name), time_offset)

    argv = sys.argv
    """
    argv_1: input csv file
    argv_2: timestamp file
    argv_3: output csv_file
    """
    if len(argv) < 4:
        print('not enough arguments')
        exit(0)
    input_file = argv[1]
    timestamps_txt = argv[2]
    output_file = argv[3]
    df = pd.read_csv(input_file, delimiter='\t')
    output = df[['accelerometerTimestamp_sinceReboot(s)',
                 'accelerometerAccelerationX(G)',
                 'accelerometerAccelerationY(G)',
                 'accelerometerAccelerationZ(G)',
                 'motionRotationRateX(rad/s)',
                 'motionRotationRateY(rad/s)',
                 'motionRotationRateZ(rad/s)']]
    print(len(output))
    labels_np = get_labels(timestamps_txt, len(output), output)
    print(labels_np.shape)
    output['label'] = labels_np
    output.to_csv(output_file, sep='\t')

