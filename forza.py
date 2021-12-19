import json
import os
import socket
import time
from concurrent.futures.thread import ThreadPoolExecutor
from os import listdir
from os.path import isfile, join

import matplotlib.pyplot as plt
import numpy as np
from fdp import ForzaDataPacket

import gear_helper
import helper
from logger import logger


class Forza:
    def __init__(self, port, threadPool: ThreadPoolExecutor, packet_format='fh4', clutch = False):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(('127.0.0.1', port))
        logger.info('listening on port {}'.format(port))

        self.packet_format = packet_format
        self.isRunning = False
        self.threadPool = threadPool
        self.clutch = clutch

        # Constant        
        self.config_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')

        # === Pre-defined operation ===
        self.stop = 'f11' # stop program
        self.close = 'delete' # close program
        self.collect_data = 'f10'
        self.analysis = 'f8'
        self.auto_shift = 'f7'

        # === Car information ===
        self.ordinal = ''
        self.minGear = 1
        self.maxGear = 5
        
        self.gear_ratios = {}
        self.rpm_torque_map = {}
        self.shift_point = {}
        self.records = []
        
        self.last_upshift = time.time()
        self.last_downshift = time.time()

    def test_gear(self):
        try:
            logger.debug(f'{self.test_gear.__name__} started')
            self.records = []
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
                        'car_ordinal':str(fdp.car_ordinal),
                        'speed/rpm': fdp.speed * 3.6 / fdp.current_engine_rpm
                    }
                    self.records.append(info)
                    logger.debug(info)

            if len(self.records) > 0:
                self.ordinal = self.records[0]['car_ordinal']
            return self.records
        except BaseException as e:
            logger.exception(e)
        finally:
            self.isRunning = False        
            logger.debug(f'{self.test_gear.__name__} finished')

    def analyze(self, performance_profile=True):
        try:
            logger.debug(f'{self.analyze.__name__} started')
            self.shift_point = gear_helper.calculateOptimalShiftPoint(self.records, self)

            if performance_profile:
                fig, ax = plt.subplots(2, 2)

                # # gear vs ratio at 0, 0
                helper.plot_gear_ratio(self, ax, 0, 0)

                # torque vs rpm at 0, 1
                helper.plot_torque_rpm(self, ax, 0, 1)
                
                # torque vs speed at 1, 0
                helper.plot_torque_speed(self, ax, 1, 0)

                # rpm vs speed at 1, 1
                helper.plot_rpm_speed(self, ax, 1, 1)

                fig.tight_layout()
                plt.show()
        except BaseException as e:
            logger.exception(e)
        finally:
            logger.debug(f'{self.analyze.__name__} ended')

    def __try_auto_load_config(self, fdp: ForzaDataPacket):
        try:
            logger.debug(f'{self.__try_auto_load_config.__name__} started')
            # config name pattern: xxx_xxx_{car_ordinal}_xxx
            config = [f for f in listdir(self.config_folder) if (isfile(join(self.config_folder, f)) and str(fdp.car_ordinal) in os.path.splitext(f)[0].split('_'))]
            if len(config) <= 0:
                logger.warning(f'config ({fdp.car_ordinal}) is not found at folder {self.config_folder}. Please run gear test ({self.collect_data}) and/or analysis ({self.analysis}) first!!')
                return False
            elif len(config) > 1:
                logger.warning(f'multiple configs ({fdp.car_ordinal}) are found at folder {self.config_folder}: {config}. The car ordinal should be unique')
                return False
            else:
                logger.info(f'loading config {config}')
                self.load_config(os.path.join(self.config_folder, config[0]))
                if len(self.shift_point) <= 0:
                    logger.warning(f'Config is invalid. Please run gear test ({self.collect_data}) and/or analysis ({self.analysis}) to create a new one!!')
                    return False
                logger.info(f'loaded config {config}')
                return True
        finally:
            logger.debug(f'{self.__try_auto_load_config.__name__} ended')

    def run(self):
        try:     
            logger.debug(f'{self.run.__name__} started')
            iteration = -1
            while self.isRunning:
                fdp = helper.nextFdp(self.server_socket, self.packet_format)

                # fdp is not car information
                if fdp.car_ordinal <= 0:
                    continue

                # try to load config if:
                # 1. self.shift_point is empty
                # or
                # 2. fdp.car_ordinal is different from self.ordinal => means car switched
                if len(self.shift_point) <= 0 or self.ordinal != fdp.car_ordinal:
                    if self.__try_auto_load_config(fdp):
                        continue
                    else:
                        return

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

                    if not fired and gear > 1:
                        target_down_speed = self.shift_point[gear - 1]['speed']
                        if speed + 20 < target_down_speed and slip < 1:
                            logger.debug(f'[{iteration}] down shift triggerred. speed < target down speed ({speed} > {target_down_speed}), fired {fired}')
                            gear_helper.downShiftHandle(gear, self)
        except BaseException as e:
            logger.exception(e)
        finally:
            self.isRunning = False
            logger.debug(f'{self.run.__name__} finished')