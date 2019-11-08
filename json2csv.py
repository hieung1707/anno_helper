import json, os


def convert_json_2_csv(read_folder, json_headers, csv_headers):
    if read_folder[-1] != '/':
        read_folder+='/'

    # for each json file
    for filename in os.listdir(read_folder):
        if filename.split('.')[-1] != 'json':
            continue

        # open json file
        with open(read_folder + filename) as file:

            # read json file into 'data'
            data = json.load(file)

            # write to csv
            with open(read_folder + filename[:-5] + '_frjson.csv', 'w') as write_file:

                # write header first
                write_file.write(','.join(csv_headers) + '\n')

                # for each sample dict
                for sample in data:

                    thisline = ''
                    # for each column
                    for column_name in json_headers:
                        thisline += sample[column_name] + ','

                    thisline = thisline[:-1]
                    write_file.write(thisline + '\n')


if __name__ == '__main__':
    # prepare columns' name (headers)
    csv_headers = ['loggingTime(txt)', 'loggingSample(N)', 'accelerometerTimestamp_sinceReboot(s)',
                   'accelerometerAccelerationX(G)', 'accelerometerAccelerationY(G)', 'accelerometerAccelerationZ(G)',
                   'motionTimestamp_sinceReboot(s)', 'motionYaw(rad)', 'motionRoll(rad)', 'motionPitch(rad)',
                   'motionRotationRateX(rad/s)', 'motionRotationRateY(rad/s)', 'motionRotationRateZ(rad/s)',
                   'motionUserAccelerationX(G)', 'motionUserAccelerationY(G)', 'motionUserAccelerationZ(G)',
                   'motionAttitudeReferenceFrame(txt)', 'motionQuaternionX(R)', 'motionQuaternionY(R)',
                   'motionQuaternionZ(R)', 'motionQuaternionW(R)', 'motionGravityX(G)', 'motionGravityY(G)',
                   'motionGravityZ(G)', 'pedometerStartDate(txt)', 'pedometerNumberofSteps(N)',
                   'pedometerAverageActivePace(s/m)', 'pedometerCurrentPace(s/m)', 'pedometerCurrentCadence(steps/s)',
                   'pedometerDistance(m)', 'pedometerFloorAscended(N)', 'pedometerFloorDescended(N)',
                   'pedometerEndDate(txt)', 'altimeterTimestamp_sinceReboot(s)', 'altimeterReset(bool)',
                   'altimeterRelativeAltitude(m)', 'altimeterPressure(kPa)', 'batteryState', 'batteryLevel', 'label']

    json_headers = ['loggingTime', 'logSampleNr', 'accelerometerTimestamp_sinceReboot', 'accelerometerAccelerationX',
                    'accelerometerAccelerationY', 'accelerometerAccelerationZ', 'motionTimestamp_sinceReboot',
                    'motionYaw', 'motionRoll', 'motionPitch', 'motionRotationRateX', 'motionRotationRateY',
                    'motionRotationRateZ',
                    'motionUserAccelerationX', 'motionUserAccelerationY', 'motionUserAccelerationZ',
                    'motionAttitudeReferenceFrame', 'motionQuaternionX', 'motionQuaternionY', 'motionQuaternionZ',
                    'motionQuaternionW', 'motionGravityX', 'motionGravityY', 'motionGravityZ', 'pedometerStartDate',
                    'pedometerNumberOfSteps', 'pedometerAverageActivePace', 'pedometerCurrentPace',
                    'pedometerCurrentCadence', 'pedometerDistance', 'pedometerFloorsAscended',
                    'pedometerFloorsDescended', 'pedometerEndDate', 'altimeterTimestamp_sinceReboot', 'altimeterReset',
                    'altimeterRelativeAltitude',
                    'altimeterPressure', 'batteryState', 'batteryLevel', 'label']

    read_folder = 'data/sensors/'

    convert_json_2_csv(read_folder, json_headers, csv_headers)