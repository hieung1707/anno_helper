import pandas as pd
import sys
import numpy as np
import glob
import os
import re


# label_dict = {
#     'DG': 1,
#     'LN2': 2,
#     'LC2': 3,
#     'MD': 4
# }
pattern1 = '<LINKED_FILE_DESCRIPTOR.*TIME_ORIGIN=\"(\d+)\".*/>'
pattern2 = '<LINKED_FILE_DESCRIPTOR.* LINK_URL=\"(.*csv)\".*/>'
# pattern2 = '<MEDIA_DESCRIPTOR.*TIME_ORIGIN=\"(\d+)\".*/>'


def get_time_offset(eaf_file):
    eaf = open(eaf_file, 'r')
    lines = eaf.readlines()
    for line in lines:
        result = re.search(pattern1, line)
        if result is not None:
            return int(result.group(1)) * 1. / 1000
        # result = re.search(pattern2, line)
        # if result is not None:
        #     return int('-' + result.group(1)) * 1. / 1000
    eaf.close()
    return 0


def get_csv_link(eaf_file):
    eaf = open(eaf_file, 'r')
    lines = eaf.readlines()
    for line in lines:
        result = re.search(pattern2, line)
        print(result)
        if result is not None:
            return result.group(1)
    eaf.close()
    return ''


def get_labels(timestamps_txt, time_offset, n_samples, df):
    # time_domain = 'accelerometerTimestamp_sinceReboot(s)'
    time_domain = 'loggingTime(txt)'
    txt_file = open(timestamps_txt, "r")
    lines = txt_file.readlines()
    labels1_np = np.zeros(n_samples, dtype=object)
    labels2_np = np.zeros(n_samples, dtype=object)
    for i, line in enumerate(lines):
        if i == 0:
            continue
        line = line.replace('\t\n', '')
        line = line.replace('\n', '')
        info = line.split('\t')
        start = float(info[0])
        end = float(info[1])
        label1 = info[2]
        label2 = info[3]
        # label = label_dict[info[2]]
        filter_df1 = df[time_domain] >= (start + time_offset)
        filter_df2 = df[time_domain] <= (end + time_offset)
        data = df.where(filter_df1 & filter_df2, inplace=False)
        data.dropna(inplace=True, how='all')
        indices = data.index
        if len(indices) == 0:
            continue
        print('Start time: {}; End time: {}'.format(start, end))
        # else:
        #     print(indices[0], indices[-1])
        start_idx = indices[0]
        end_idx = indices[-1]
        labels1_np[start_idx:end_idx] = label1
        labels2_np[start_idx:end_idx] = label2
    labels1_np[labels1_np == 0] = ''
    labels2_np[labels2_np == 0] = ''
    return labels1_np, labels2_np


def get_label_data(input_file, timestamps_txt, output_file, time_offset=0):
    df = pd.read_csv(input_file, delimiter='\t')
    output = df
    # df['accelerometerTimestamp_sinceReboot(s)'] = df['accelerometerTimestamp_sinceReboot(s)'].round(decimals=11)
    # output = df[['accelerometerTimestamp_sinceReboot(s)',
    #              'accelerometerAccelerationX(G)',
    #              'accelerometerAccelerationY(G)',
    #              'accelerometerAccelerationZ(G)',
    #              'motionRotationRateX(rad/s)',
    #              'motionRotationRateY(rad/s)',
    #              'motionRotationRateZ(rad/s)']]
    labels_np = get_labels(timestamps_txt, time_offset, len(output), output)
    output['label'] = labels_np
    output.to_csv(output_file, sep='\t', header=None, encoding='utf-8', index=False)


def extract(input_csv, timestamps_txt, eaf_file, output_csv):
    # input_csv = get_csv_link(eaf_file)
    # print(input_csv)
    # if input_csv == '':
    #     print('input csv missing')
    #     exit(0)
    df = pd.read_csv(input_csv, delimiter='\t')
    output = df
    # output = df[['accelerometerTimestamp_sinceReboot(s)',
    #              'accelerometerAccelerationX(G)',
    #              'accelerometerAccelerationY(G)',
    #              'accelerometerAccelerationZ(G)',
    #              'motionRotationRateX(rad/s)',
    #              'motionRotationRateY(rad/s)',
    #              'motionRotationRateZ(rad/s)']]
    time_offset = get_time_offset(eaf_file=eaf_file)
    print(time_offset)
    labels1_np, labels2_np = get_labels(timestamps_txt, time_offset, len(output), output)
    output['label1'] = labels1_np
    output['label2'] = labels2_np
    output.to_csv(output_csv, sep='\t', header=None, encoding='utf-8', index=False)
    print('DONE')


if __name__ == "__main__":
    """
    Add labels to csv
    Only works with segmented data with 2 label tiers
    Inputs:
    - input csv file
    - timestamp txt file
    - eaf file
    - output csv file
    """

    # Fast conversion --------------------------------
    # folders = glob.glob('/home/hieung1707/Downloads/data_11_11_19/part1/*')
    # label_dir = '/home/hieung1707/labels'
    # if not os.path.exists(label_dir):
    #     os.mkdir(label_dir)
    # for folder in folders:
    #     folder_name = folder.split('/')[-1]
    #     eaf_file = glob.glob('{}/*.eaf'.format(folder))[0]
    #     time_offset = get_time_offset(eaf_file)
    #     print(time_offset)
    #     data_50hz = glob.glob('{}/output1.csv'.format(folder))[0]
    #     data_other = glob.glob('{}/output2.csv'.format(folder))[0]
    #     if not os.path.exists('{}/{}'.format(label_dir, folder_name)):
    #         os.mkdir('{}/{}'.format(label_dir, folder_name))
    #     get_label_data(data_50hz, '{}/{}.txt'.format(folder, folder_name),
    #       '{}/{}/label1.txt'.format(label_dir, folder_name), time_offset)
    #     get_label_data(data_other, '{}/{}.txt'.format(folder, folder_name),
    #       '{}/{}/label2.txt'.format(label_dir, folder_name), time_offset)
    # ---------------------------------------------

    root_folder = '/home/hieung1707/Downloads/synced_data/20190917_085418'
    #
    extract('{}/output.csv'.format(root_folder), '{}/20190917_085418.txt'.format(root_folder), '{}/20190917_085418.eaf'.format(root_folder), '{}/test.csv'.format(root_folder))

