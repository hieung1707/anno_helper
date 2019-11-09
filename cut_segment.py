import glob
import sys
import pandas as pd
import re
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import resample
# from resampy import resample
from scipy.interpolate import interp1d


time_offset = 0
pattern = '.*LINKED_FILE_DESCRIPTOR.* LINK_URL=\"./(.*)\".*TIME_ORIGIN=\"(\d+)\".*'
titles = {
    'DG': 'Dọn Giường',
    'LC2': 'Lau cửa kính',
    'LN2': 'Lau nhà'
}


def get_time_offset_and_linked_csv(eaf_file):
    eaf = open(eaf_file, 'r')
    lines = eaf.readlines()
    for line in lines:
        result = re.search(pattern, line)
        if result is not None:
            return result.group(1), result.group(2)
    return '', 0


# def resample(signal, org_freq, desired_freq):
#     ratio = org_freq * 1. / desired_freq
#     ratio_count = 0
#     new_signal = []
#     for i in range(len(signal)):
#         if i >= ratio_count:
#             new_signal.append(signal[i])
#             ratio_count += ratio
#     return np.array(new_signal)


def interpolate(time, signal, downsampled_time):
    f = interp1d(time, signal)
    return f(downsampled_time)


def plot_subplot_interpolate(subplot, times, acc_x, acc_y, acc_z, org_freq, new_freq):
    if org_freq != new_freq:
        times1 = resample(times, org_freq, new_freq)
    else:
        times1 = times
    print(times1.shape)
    plt.subplot(subplot)
    plt.plot(times1, interpolate(times, acc_x, times1))
    plt.plot(times1, interpolate(times, acc_y, times1))
    plt.plot(times1, interpolate(times, acc_z, times1))


def plot_subplot_skip(subplot, times, acc_x, acc_y, acc_z, org_freq, new_freq, shared_ax, lim_y):
    ax = plt.subplot(subplot, sharex=shared_ax)
    time_plot = resample(times, org_freq, new_freq)
    ax.plot(time_plot, resample(acc_x, org_freq, new_freq))
    ax.plot(time_plot, resample(acc_y, org_freq, new_freq))
    ax.plot(time_plot, resample(acc_z, org_freq, new_freq))
    ax.set_title('{}Hz'.format(new_freq))
    ax.set_ylim(lim_y)
    return ax


if __name__ == "__main__":
    skip = 0
    skip_count = 0
    argv = sys.argv
    """
    argv 1: folder containing eaf file
    argv 2: output file, currently unused
    argv 3: skip n - 1 segments from the start (optional)
    """

    if len(argv) < 3:
        print('not enough arguments')
        exit()
    folder = argv[1]
    output_file = argv[2]
    if len(argv) == 4:
        skip_count = argv[3]
    txt_files = glob.glob('{}/*.txt'.format(folder))
    csv_files = glob.glob('{}/*.csv'.format(folder))
    eaf_files = glob.glob('{}/*.eaf'.format(folder))
    if len(txt_files) == 0:
        print('no timestamp file')
        exit()
    if len(csv_files) == 0:
        print('no csv file')
        exit()
    if len(eaf_files) == 0:
        print('no eaf file')
        exit()
    _, time_offset = get_time_offset_and_linked_csv(eaf_files[0])
    time_offset = int(time_offset) * 1. / 1000

    csv_files = glob.glob('{}/*.csv'.format(folder))
    txt_file = open(txt_files[0], "r")
    lines = txt_file.readlines()
    for i, line in enumerate(lines):
        if i == 0:
            continue
        labels = []
        line = line.replace('\t\n', '')
        info = line.split('\t')
        start = float(info[0])
        end = float(info[1])
        info_len = len(info)
        if info_len >= 3:
            labels.append(info[2])
        if info_len == 4:
            labels.append(info[3])
        else:
            labels.append('')
        if labels[0] in ['DG'] or labels[1] in ['LN2', 'LC2']:
            if skip < skip_count:
                skip += 1
                continue
            title = ''
            if labels[0] in titles.keys():
                title = titles[labels[0]]
            else:
                title = titles[labels[1]]
            print(title)
            segment = []
            desired_duration = 5

            df = pd.read_csv(csv_files[0], delimiter='\t')
            filter_df1 = df['loggingTime(txt)'] < end + time_offset
            filter_df2 = df['loggingTime(txt)'] > start + time_offset
            df.where(filter_df1&filter_df2, inplace=True)
            df.dropna(inplace=True)
            df.reset_index(drop=True, inplace=True)
            start_time = df.iloc[0]['loggingTime(txt)']
            # filter_time = df['loggingTime(txt)'] <= start_time + desired_duration
            # df.where(filter_time, inplace=True)
            # df.dropna(inplace=True)
            # df.reset_index(drop=True, inplace=True)
            times = df['loggingTime(txt)'].to_numpy() - start_time
            acc_x = df['accelerometerAccelerationX(G)'].to_numpy()
            acc_y = df['accelerometerAccelerationY(G)'].to_numpy()
            acc_z = df['accelerometerAccelerationZ(G)'].to_numpy()
            lim_y = (np.min([np.min(acc_x), np.min(acc_y), np.min(acc_z)]) - 1, np.max([np.max(acc_x), np.max(acc_y), np.max(acc_z)]) + 1)

            fig = plt.figure()
            fig.suptitle(title)
            ax1 = plt.subplot(511)
            ax1.plot(times, acc_x)
            ax1.plot(times, acc_y)
            ax1.plot(times, acc_z)
            ax1.set_ylim(lim_y)
            ax1.set_title('{}Hz'.format(100))
            plot_subplot_skip(512, times, acc_x, acc_y, acc_z, 100, 50, ax1, lim_y)
            plot_subplot_skip(513, times, acc_x, acc_y, acc_z, 100, 40, ax1, lim_y)
            plot_subplot_skip(514, times, acc_x, acc_y, acc_z, 100, 30, ax1, lim_y)
            plot_subplot_skip(515, times, acc_x, acc_y, acc_z, 100, 20, ax1, lim_y)
            plt.show()
            # plt.subplot(512)
            # plot_subplot(512, times, acc_x, acc_y, acc_z, 100, 50)
            # plot_subplot(513, times, acc_x, acc_y, acc_z, 100, 40)
            # plot_subplot(514, times, acc_x, acc_y, acc_z, 100, 30)
            # plot_subplot(515, times, acc_x, acc_y, acc_z, 100, 20)
            # plt.subplot(512)
            # plt.plot(resample(times, 100, 50), resample(acc_x, 100, 50))
            # plt.plot(resample(times, 100, 50), resample(acc_y, 100, 50))
            # plt.plot(resample(times, 100, 50), resample(acc_z, 100, 50))
            # plt.subplot(513)
            # plt.plot(resample(times, 100, 40), resample(acc_x, 100, 40))
            # plt.plot(resample(times, 100, 40), resample(acc_y, 100, 40))
            # plt.plot(resample(times, 100, 40), resample(acc_z, 100, 40))
            # plt.subplot(514)
            # plt.plot(resample(times, 100, 30), resample(acc_x, 100, 30))
            # plt.plot(resample(times, 100, 30), resample(acc_y, 100, 30))
            # plt.plot(resample(times, 100, 30), resample(acc_z, 100, 30))
            # plt.subplot(515)
            # plt.plot(resample(times, 100, 20), resample(acc_x, 100, 20))
            # plt.plot(resample(times, 100, 20), resample(acc_y, 100, 20))
            # plt.plot(resample(times, 100, 20), resample(acc_z, 100, 20))
            # plt.show()
            break
