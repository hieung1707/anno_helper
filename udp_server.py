import logging
import socket
import struct
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from collections import deque
import threading

info = deque(maxlen=50)


log = logging.getLogger('udp_server')

first_time = True
first_ts = time.time()
total_time = 0
total_count = 0
last_ts = 0
diff = 0
is_updating = False


class Visualizer():
    def __init__(self, plot_interval=20):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(2, 1, 1)
        self.ax2 = self.fig.add_subplot(2, 1, 2)
        self.plot_interval = plot_interval

    def animate(self, i):
        global info, is_updating
        # global xs, acc_xs, acc_ys, acc_zs, gyr_xs, gyr_ys, gyr_zs, is_updating
        # Draw x and y lists
        if is_updating:
            return
        # self.ax.clear()
        info_np = np.array(info)
        if len(info) == 0:
            return
        xs = info_np[:, 0]
        acc_xs = info_np[:, 1]
        acc_ys = info_np[:, 2]
        acc_zs = info_np[:, 3]
        gyr_xs = info_np[:, 4]
        gyr_ys = info_np[:, 5]
        gyr_zs = info_np[:, 6]

        self.ax.clear()
        self.ax.plot(xs, acc_xs)
        self.ax.plot(xs, acc_ys)
        self.ax.plot(xs, acc_zs)
        self.ax.set_ylim((-10, 10))

        self.ax2.clear()
        self.ax2.plot(xs, gyr_xs)
        self.ax2.plot(xs, gyr_ys)
        self.ax2.plot(xs, gyr_zs)
        self.ax2.set_ylim((-10, 10))

        # Format plot
        plt.xticks(rotation=45, ha='right')
        plt.subplots_adjust(bottom=0.30)
        plt.title('Sensors')
        plt.ylabel('Sensor log')
        plt.xlabel('timestamp')


    def visualize(self):
        ani = animation.FuncAnimation(self.fig, self.animate, interval=self.plot_interval)
        plt.show()
        # plt.axis([-50, 50, 0, 10000])


def udp_server(host='0.0.0.0', port=5550):
    global total_count, total_time, first_ts, first_time, last_ts, diff, info, is_updating
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    log.info("Listening on udp %s:%s" % (host, port))
    s.bind((host, port))

    while True:
        (data, addr) = s.recvfrom(48)
        curr_time = time.time()
        print(len(data))
        if data and len(data) == 48:
            if first_time:
                first_ts = curr_time
                last_ts = first_ts
                first_time = False
                diff = 0
            total_time = curr_time - first_ts
            total_count = total_count + 1
            diff += 1
            is_updating = True
            acc_x = struct.unpack('d', data[:8])
            acc_y = struct.unpack('d', data[8:16])
            acc_z = struct.unpack('d', data[16:24])
            gyr_x = struct.unpack('d', data[24:32])
            gyr_y = struct.unpack('d', data[32:40])
            gyr_z = struct.unpack('d', data[40:])
            info.append([total_time, acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z])
            is_updating = False
        if curr_time - last_ts >= 1.:
            print(diff, total_count * 1. / total_time, curr_time - last_ts)
            last_ts = curr_time
            diff = 0
            # data = data.decode('utf-8')
            # print('acc X: {}; acc Y: {}; acc Z: {}'.format(data_x, data_y, data_z))
        # elif len(data) != 24 and len(data) != 0:
        #     print(data)


FORMAT_CONS = '%(asctime)s %(name)-12s %(levelname)8s\t%(message)s'
# logging.basicConfig(level=logging.DEBUG, format=FORMAT_CONS)

# viz = Visualizer()
# t1 = threading.Thread(target=udp_server)
# t1.start()
# viz.visualize()
# plt.show()
udp_server()
