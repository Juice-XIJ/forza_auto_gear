from concurrent.futures.thread import ThreadPoolExecutor

from matplotlib import axes
import gear_helper
import helper
import socket
import time
import numpy as np
import matplotlib.pyplot as plt
from logger import logger
from matplotlib.pyplot import cm
from os import listdir
from os.path import isfile, join
import json
import os

class Forza:
    def __init__(self, port, threadPool: ThreadPoolExecutor, packet_format='dash', clutch = False):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(('127.0.0.1', port))
        logger.info('listening on port {}'.format(port))

        self.packet_format = packet_format
        self.isRunning = False
        self.threadPool = threadPool

        # Constant        
        self.dump_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dump')

        # Car information
        self.minGear = 1
        self.maxGear = 5
        self.clutch = clutch

        self.gear_ratios = {}
        self.rpm_torque_map = {}
        self.shift_point = {}
        self.cuttoff = 4000

        # === Pre-defined operation ===
        self.stop = 'f11' # stop program
        self.close = 'delete' # close program
        self.collect_data = 'f10'
        self.analysis = 'f8'
        self.auto_shift = 'f7'
        
        self.last_upshift = time.time()
        self.last_downshift = time.time()

    def dump_config(self):
        config = {
            # === dump operation setting ===
            'stop': self.stop,
            'close': self.close,
            'collect_data': self.collect_data,
            'analysis': self.analysis,
            'auto_shift': self.auto_shift,

            # === dump data and result ===
            'minGear': self.minGear,
            'maxGear': self
        }

    def test_gear(self):
        logger.info('gear test started')
        self.records = []
        upShiftTime = time.time()
        is100kmRecorded = False
        is200kmRecorded = False
        # helper.nextFdp(self.server_socket, self.packet_format)
        while self.isRunning:
            fdp = helper.nextFdp(self.server_socket, self.packet_format)
            if fdp.speed > 0.1:
                info = {
                    'gear': fdp.gear,
                    'rpm': fdp.current_engine_rpm,
                    'time': time.time(),
                    'speed': fdp.speed * 3.6,
                    'slip': min(1.1, (fdp.tire_slip_ratio_RL + fdp.tire_slip_ratio_RR) / 2),
                    'clutch': fdp.clutch,
                    'power': fdp.power / 1000.0,
                    'torque': fdp.torque,
                    'car_ordinal':fdp.car_ordinal,
                    'speed/rpm': fdp.speed * 3.6 / fdp.current_engine_rpm
                }
                self.records.append(info)

                logger.debug(info)

                # if not is100kmRecorded and self.records[-1]['speed'] >= 100.0:
                #     time_100km_acc = self.records[-1]["time"] - self.records[0]["time"]
                #     is100kmRecorded = True
                #     logger.info(f'rpm {threshold}% - 100km/h acceleration: {time_100km_acc}s')

                # if not is200kmRecorded and self.records[-1]['speed'] >= 200.0:
                #     time_200km_acc = self.records[-1]["time"] - self.records[0]["time"]
                #     is200kmRecorded = True
                #     logger.info(f'rpm {threshold}% - 200km/h acceleration: {time_200km_acc}s')
                
                # rpmp = fdp.current_engine_rpm / fdp.engine_max_rpm
                # curTime = time.time()
                # logger.debug(f'rpmp = {rpmp}%\t ====> cur gear {fdp.gear}')
                # if rpmp > threshold and curTime - upShiftTime > gear_helper.upShiftCoolDown:
                #     gear_helper.upShiftHandle(fdp.gear)
                #     upShiftTime = time.time()

        logger.info('gear test finished')
        return self.records

    def analyze(self):
        self.shift_point = gear_helper.calculateOptimalShiftPoint(self.records, self)

        rpm = np.array([item['rpm'] for item in self.records])  
        time = np.array([item['time'] for item in self.records])
        power = np.array([item['power'] for item in self.records])
        torque = np.array([item['torque'] for item in self.records])
        time0 = self.records[0]['time']
        time = np.where(time > 0, time - time0, 0)

        fig, ax = plt.subplots(2, 2)

        # # gear vs ratio at 0, 0
        self.plot_gear_ratio(ax, 0, 0)

        # torque vs rpm at 0, 1
        self.plot_engine_profile(ax, 0, 1)
        
        # power vs rpm at 1, 0
        ax[1, 0].plot(time, power, label='power', color='b')
        ax[1, 0].set_xlabel('time')
        ax[1, 0].set_ylabel('power (W)', color='b')
        ax[1, 0].tick_params('y', color='b')
        ax0 = ax[1, 0].twinx()
        ax0.plot(time, rpm, label='rpm', color='r')
        ax0.set_ylabel('rpm (r/m)', color='r')
        ax0.tick_params('y', colors='r')

        # torque vs power at 1, 1
        ax[1, 1].plot(time, torque, label='torque', color='b')
        ax[1, 1].set_xlabel('time')
        ax[1, 1].set_ylabel('torque (N/m)', color='b')
        ax[1, 1].tick_params('y', color='b')
        ax0 = ax[1, 1].twinx()
        ax0.plot(time, power, label='power', color='r')
        ax0.set_ylabel('power (W)', color='r')
        ax0.tick_params('y', colors='r')

        fig.tight_layout()
        plt.show()

    def auto_gear(self):        
        logger.info('auto gear started')
        iteration = -1
        while self.isRunning:
            fdp = helper.nextFdp(self.server_socket, self.packet_format)            
            if len(self.shift_point) <= 0:
                if fdp.car_ordinal <= 0:
                    continue
                
                # dump name pattern: xxx_xxx_{car_ordinal}_xxx
                dump = [f for f in listdir(self.dump_folder) if (isfile(join(self.dump_folder, f)) and fdp.car_ordinal in f.split('_'))]
                if len(dump) <= 0:
                    logger.warning(f'dump ({fdp.car_ordinal}) is not found at folder {self.dump_folder}. Please run gear test ({self.collect_data}) and/or analysis ({self.analysis}) first!!')
                    return
                elif len(dump) > 1:
                    logger.warning(f'multiple dumps ({fdp.car_ordinal}) are found at folder {self.dump_folder}: {dump}. The car ordinal should be unique')
                    return
                else:                    
                    with open (os.path.join(self.dump_folder, dump[0]), 'r') as dump:
                        for line in dump:
                            self.records.append(json.loads(line.replace('\n', '').replace('\'', '\"')))

            if self.maxGear >= fdp.gear >= self.minGear:
                iteration = iteration + 1
                slip = (fdp.tire_slip_ratio_RL + fdp.tire_slip_ratio_RR) / 2
                gear = fdp.gear
                speed = fdp.speed * 3.6
                rpm = fdp.current_engine_rpm
                accel = fdp.accel
                fired = False
                if fdp.gear < self.maxGear:
                    target_rpm = self.shift_point[gear]['rpmo'] * 0.99999
                    target_up_speed = int(self.shift_point[gear]['speed'] * 0.985)
                    if rpm > target_rpm and slip < 1 and accel and speed > target_up_speed:
                        logger.debug(f'[{iteration}] up shift triggerred. rpm > target rmp({rpm} > {target_rpm}), speed > target up speed ({speed} > {target_up_speed}), slip {slip}, accel {accel}')
                        gear_helper.upShiftHandle(gear, self)
                        fired = True
                    # elif speed > target_up_speed:
                    #     logger.debug(f'[{iteration}] up shift triggerred. speed > target up speed ({speed} > {target_up_speed})')
                    #     gear_helper.upShiftHandle(gear, self)
                    #     fired = True

                if not fired and gear > 1:
                    target_down_speed = self.shift_point[gear - 1]['speed']
                    if speed + 20 < target_down_speed and slip < 1:
                        logger.debug(f'[{iteration}] down shift triggerred. speed < target down speed ({speed} > {target_down_speed}), fired {fired}')
                        gear_helper.downShiftHandle(gear, self)


        logger.info('auto gear finished')

    def plot_gear_ratio(self, ax: axes.Axes = None, row: int = None, col: int = None):  
        f = []
        legends = []
        gear = np.array([item['gear'] for item in self.records])
        time = np.array([item['time'] for item in self.records])
        ratio = np.array([item['speed/rpm'] for item in self.records])
        time0 = self.records[0]['time']
        time = np.where(time > 0, time - time0, 0)

        f.append(ax[row, col].plot(time, ratio, label='speed/rpm', color='b'))
        legends.append('raw ratio') 

        color = iter(cm.rainbow(np.linspace(0, 1, len(self.gear_ratios))))
        for _, item in self.gear_ratios.items():
            g = item['records'][0]['gear']
            f.append(ax[row, col].hlines(item['ratio'], time[0], time[-1], label=f'gear {g} ratio', color=next(color), linestyles='dashed'))
            legends.append(f'gear {g} ratio')
        
        ax[row, col].set_xlabel('time')
        ax[row, col].set_ylabel('ratio (km/h/rpm)', color='b')
        ax[row, col].tick_params('y', color='b')
        ax[row, col].legend()

        ax0 = ax[row, col].twinx()
        ax0.plot(time, gear, label='gear', color='r')
        ax0.set_ylabel('gear', color='r')
        ax0.tick_params('y', colors='r')
        ax0.legend(loc=4)
    
    def plot_engine_profile(self, ax: axes.Axes = None, row: int = None, col: int = None):
        color = iter(cm.rainbow(np.linspace(0, 1, len(self.gear_ratios))))
        for _, item in self.rpm_torque_map.items():
            g = item['records'][0]['gear']
            data = np.array([[i['rpm'], i['power'], i['torque'], i['speed']] for i in item['records'][item['min_rpm_index']:item['max_rpm_index']]])
            data = np.sort(data, 0)
            c = next(color)
            
            rpms = np.array([item[0] for item in data])
            torque = np.array([item[2] for item in data])

            ax[row, col].plot(rpms, torque, label=f'Gear {g} torque', color=c, linestyle='dashed')
            ax[row, col].set_xlabel('rpm')
            ax[row, col].set_ylabel('Torque (N/m)')
            ax[row, col].tick_params('y')

        ax[row, col].legend(loc=8)
