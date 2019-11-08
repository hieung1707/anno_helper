import pandas as pd
from datetime import datetime
import sys


def read_csv(file_path):
    data = pd.read_csv(file_path, delimiter=r",")
    return data


if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv) < 3:
        print('error')
        exit(0)

    data=read_csv(sys.argv[1])
    times=[0]
    for idx in range(len(data["loggingTime(txt)"])-1):
        raw_1=data["loggingTime(txt)"][idx]
        raw_2=data["loggingTime(txt)"][idx+1]
        datetime_object_0 = datetime.strptime(raw_1, '%Y-%m-%d %H:%M:%S.%f +0700')
        datetime_object_1 = datetime.strptime(raw_2, '%Y-%m-%d %H:%M:%S.%f +0700')
        diff=datetime_object_1-datetime_object_0
        times.append(times[-1]+diff.total_seconds())

    data["loggingTime(txt)"] = times

    print(data)
    data.to_csv(sys.argv[2],sep='\t', encoding='utf-8', index=False)