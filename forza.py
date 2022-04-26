import sys
import os
import time
from concurrent.futures.thread import ThreadPoolExecutor
from os import listdir
from os.path import isfile, join

import matplotlib.pyplot as plt

sys.path.append(r'./forza_motorsport')
from fdp import ForzaDataPacket

import constants
from constants import ConfigVersion
import gear_helper
import helper
import keyboard_helper
from car_info import CarInfo
from logger import Logger


class Forza(CarInfo):

    def __init__(self, threadPool: ThreadPoolExecutor, logger: Logger = None, packet_format='fh4', enable_clutch=False):
        """initialization

        Args:
            threadPool (ThreadPoolExecutor): threadPool
            packet_format (str, optional): packet_format. Defaults to 'fh4'.
            enable_clutch (bool, optional): enable_clutch. Defaults to False.
        """
        super().__init__()

        # === socket ===
        self.ip = constants.ip
        self.port = constants.port

        # === logger ===
        self.logger = (Logger()('Forza5')) if logger is None else logger

        self.packet_format = packet_format
        self.isRunning = False
        self.threadPool = threadPool
        self.enable_clutch = enable_clutch
        self.farming = False
        self.shift_point_factor = constants.shift_factor

        # shortcuts
        self.clutch = constants.clutch
        self.upshift = constants.upshift
        self.downshift = constants.downshift
        self.boundKeys = lambda: [self.clutch, self.upshift, self.downshift]

        # constant
        self.config_folder = os.path.join(constants.root_path, 'config')

        # create folders if not existed
        if not os.path.exists(self.config_folder):
            os.makedirs(self.config_folder)

        # === car data ===
        self.gear_ratios = {}
        self.rpm_torque_map = {}
        self.shift_point = {}
        self.records = []

        self.last_upshift = time.time()
        self.last_downshift = time.time()

    def test_gear(self, update_car_gui_func=None):
        """collect gear information

        Args:
            update_car_gui_func (optional): callback to update car gui. Defaults to None.
        """
        try:
            self.logger.debug(f'{self.test_gear.__name__} started')
            helper.create_socket(self)
            self.records = []
            while self.isRunning:
                fdp = helper.nextFdp(self.server_socket, self.packet_format)
                if fdp is None:
                    continue

                if fdp.speed > 0.1:
                    self.__update_forza_info(fdp)
                    if update_car_gui_func is not None:
                        update_car_gui_func(fdp)
                    info = {
                        'gear': fdp.gear,
                        'rpm': fdp.current_engine_rpm,
                        'time': time.time(),
                        'speed': fdp.speed * 3.6,
                        'slip': min(1.1, (fdp.tire_slip_ratio_RL + fdp.tire_slip_ratio_RR) / 2),
                        'clutch': fdp.clutch,
                        'power': fdp.power / 1000.0,
                        'torque': fdp.torque,
                        'speed/rpm': fdp.speed * 3.6 / fdp.current_engine_rpm
                    }
                    self.records.append(info)
                    self.logger.debug(info)
        except BaseException as e:
            self.logger.exception(e)
        finally:
            self.isRunning = False
            helper.close_socket(self)
            self.logger.debug(f'{self.test_gear.__name__} finished')

    def analyze(self, performance_profile: bool = True, is_gui: bool = False):
        """analyze data

        Args:
            performance_profile (bool, optional): plot figures or not. Defaults to True.
            is_guid (bool, optional): is gui. Defaults to False
        """
        try:
            self.logger.debug(f'{self.analyze.__name__} started')
            self.shift_point = gear_helper.calculate_optimal_shift_point(self)
            helper.dump_config(self)

            if performance_profile:
                plt.close()
                if is_gui:
                    plt.ion()

                fig, ax = plt.subplots(2, 2)
                fig.tight_layout()

                # # gear vs ratio at 0, 0
                helper.plot_gear_ratio(self, ax, 0, 0)

                # torque vs rpm at 0, 1
                helper.plot_torque_rpm(self, ax, 0, 1)

                # torque vs speed at 1, 0
                helper.plot_torque_speed(self, ax, 1, 0)

                # rpm vs speed at 1, 1
                helper.plot_rpm_speed(self, ax, 1, 1)
                plt.show()
        except BaseException as e:
            self.logger.exception(e)
            self.logger.info("something went wrong. please re-test the car")
        finally:
            self.logger.debug(f'{self.analyze.__name__} ended')

    def __update_forza_info(self, fdp: ForzaDataPacket):
        """update forza info while running

        Args:
            fdp (ForzaDataPacket): datapackage
        """
        if len(self.shift_point) <= 0 or self.ordinal != fdp.car_ordinal or self.car_perf != fdp.car_performance_index or self.car_class != fdp.car_class or self.car_drivetrain != fdp.drivetrain_type:
            self.ordinal = fdp.car_ordinal
            self.car_perf = fdp.car_performance_index
            self.car_class = fdp.car_class
            self.car_drivetrain = fdp.drivetrain_type
            return self.__try_auto_load_config(fdp)
        else:
            return True

    def __try_auto_load_config(self, fdp: ForzaDataPacket):
        """auto load config while driving

        Args:
            fdp (ForzaDataPacket): fdp

        Returns:
            [bool]: success or failure
        """
        try:
            self.logger.debug(f'{self.__try_auto_load_config.__name__} started')
            configs = [f for f in listdir(self.config_folder) if (isfile(join(self.config_folder, f)) and str(fdp.car_ordinal) in f)]
            if len(configs) <= 0:
                self.logger.warning(f'config ({fdp.car_ordinal}) is not found at folder {self.config_folder}. Please run gear test ({constants.collect_data}) and/or analysis ({constants.analysis}) first!!')
                return False
            elif len(configs) > 0:
                self.logger.info(f'found ({fdp.car_ordinal}) config(s): {configs}')

                # latest config version: ordinal-perf-drivetrain.json, v2
                filename = helper.get_config_name(self)
                if filename in configs:
                    if self.__try_loading_config(filename):
                        # remove legacy config if necessary
                        if len(configs) > 1:
                            self.__cleanup_legacy_config(configs)

                        return True
                    else:
                        return False

                # if latest config version not existed. like only ordinal.json, v1
                filename = helper.get_config_name(self, ConfigVersion.v1)
                if filename in configs:
                    if self.__try_loading_config(filename):
                        self.car_perf = fdp.car_performance_index
                        self.car_class = fdp.car_class
                        self.car_drivetrain = fdp.drivetrain_type

                        # dump to latest config version
                        helper.dump_config(self)
                        self.__cleanup_legacy_config(configs)
                        return True
                    else:
                        return False

                # unknown config
                self.logger.warning(f'unknown ({fdp.car_ordinal}) config(s) {self.config_folder}: {configs}')
                return False
        finally:
            self.logger.debug(f'{self.__try_auto_load_config.__name__} ended')

    def __cleanup_legacy_config(self, configs, latest_version: ConfigVersion = constants.default_config_version):
        """cleanup legacy configs

        Args:
            configs (list): list of configs
            latest_version (ConfigVersion, optional): config version. Defaults to constants.default_config_version.
        """
        for config in configs:
            version = helper.get_config_version(self, config)
            if version != latest_version:
                try:
                    self.logger.warning(f'removing legacy config {config}')
                    path = os.path.join(self.config_folder, config)
                    os.remove(path)
                except Exception as e:
                    self.logger.warning(f'failed to remove legacy config {config}: {e}')

    def __try_loading_config(self, config):
        """try to load config

        Args:
            config (str): config file name

        Returns:
            bool: success or failure
        """
        self.logger.info(f'loading config {config}')
        helper.load_config(self, os.path.join(self.config_folder, config))
        if len(self.shift_point) <= 0:
            self.logger.warning(f'Config is invalid. Please run gear test ({constants.collect_data}) and/or analysis ({constants.analysis}) to create a new one!!')
            return False
        self.logger.info(f'loaded config {config}')
        return True

    def shifting(self, iteration, fdp):
        """shifting func

        Args:
            iteration (int): iteration
            fdp (ForzaDataPacket): fdp

        Returns:
            [int]: iteration
        """
        gear = fdp.gear
        if fdp.speed > 0.1 and gear >= self.minGear:
            iteration = iteration + 1

            # exp or sp farming to avoid afk detection
            if self.farming and iteration % 800 == 0:
                self.threadPool.submit(keyboard_helper.press_brake, self)

            # prepare shifting params
            slip = (fdp.tire_slip_ratio_RL + fdp.tire_slip_ratio_RR) / 2
            angle_slip = (fdp.tire_slip_angle_RL + fdp.tire_slip_angle_RR) / 2
            speed = fdp.speed * 3.6
            rpm = fdp.current_engine_rpm
            accel = fdp.accel
            fired = False
            self.logger.debug(f'[{iteration}] at gear {gear}. rpm {rpm}, speed {speed}, angle slip {angle_slip}, slip {slip}, accel {accel}')

            # up shift logic
            if gear < self.maxGear and accel:
                target_rpm = self.shift_point[gear]['rpmo'] * self.shift_point_factor
                target_up_speed = int(self.shift_point[gear]['speed'] * self.shift_point_factor)

                # RWD logic
                if self.car_drivetrain == 1:
                    # at low gear (<= 3)
                    if gear <= 3 and angle_slip >= 1:
                        self.logger.debug(f'[{iteration}] up shift triggerred since RWD at gear {gear}. rpm {rpm}, speed {speed}, angle slip {angle_slip}, slip {slip}, accel {accel}')
                        gear_helper.up_shift_handle(gear, self)
                        fired = True
                    else:
                        fired = self.__up_shift(rpm, target_rpm, speed, target_up_speed, slip, iteration, gear, fdp)
                else:
                    fired = self.__up_shift(rpm, target_rpm, speed, target_up_speed, slip, iteration, gear, fdp)

            # down shift logic
            if not fired and gear > self.minGear:
                lower_gear = gear - 1 if gear - 1 <= len(self.shift_point) else len(self.shift_point) - 1
                target_down_speed = self.shift_point[lower_gear]['speed'] * self.shift_point_factor

                # RWD logic
                if self.car_drivetrain == 1:
                    # don't down shift to gear 1, 2 when RWD
                    if gear >= 4:
                        self.__down_shift(speed, target_down_speed, slip, iteration, gear, fdp)
                else:
                    self.__down_shift(speed, target_down_speed, slip, iteration, gear, fdp)

        return iteration

    def __up_shift(self, rpm, target_rpm, speed, target_up_speed, slip, iteration, gear, fdp):
        """up shift

        Args:
            rpm (float): rpm
            target_rpm (float): target rpm to up shifting
            speed (float): speed
            target_up_speed (float): target speed to up shifting
            slip (float): total combined slip of rear tires
            iteration (int): package iteration
            gear (int): current gear
            fdp (ForzaPackage): Forza Package

        Returns:
            _type_: _description_
        """
        if rpm > target_rpm and slip < 1 and speed > target_up_speed:
            self.logger.debug(f'[{iteration}] up shift triggerred. rpm > target rmp({rpm} > {target_rpm}), speed > target up speed ({speed} > {target_up_speed}), slip {slip}')
            gear_helper.up_shift_handle(gear, self)
            return True
        else:
            return False

    def __down_shift(self, speed, target_down_speed, slip, iteration, gear, fdp):
        """down shift

        Args:
            speed (float): speed
            target_down_speed (float): target speed to down shifting
            slip (float): total combined slip of rear tires
            iteration (int): package iteration
            gear (int): current gear
            fdp (ForzaPackage): Forza Package
        """
        if speed < target_down_speed * 0.95 and slip < 1:
            self.logger.debug(f'[{iteration}] down shift triggerred. speed < target down speed ({speed} < {target_down_speed}), slip {slip}')
            gear_helper.down_shift_handle(gear, self)

    def run(self, update_tree_func=lambda *args: None, update_car_gui_func=lambda *args: None):
        """run the auto shifting

        Args:
            update_tree_func (, optional): update tree view callback. Defaults to None.
            update_car_gui_func (, optional): update car gui callback. Defaults to None.
        """
        try:
            self.logger.debug(f'{self.run.__name__} started')
            helper.create_socket(self)
            iteration = -1
            reset_car = 0
            reset_time = time.time()
            while self.isRunning:
                fdp = helper.nextFdp(self.server_socket, self.packet_format)

                # fdp is not car information
                if fdp is None or fdp.car_ordinal <= 0:
                    continue

                self.threadPool.submit(update_car_gui_func, fdp)

                # try to load config if:
                # 1. self.shift_point is empty
                # or
                # 2. fdp.car_ordinal is different from self.ordinal => means car switched
                if not self.__update_forza_info(fdp):
                    return
                else:
                    self.threadPool.submit(update_tree_func)

                # enable reset car if exp or sp farming is True
                if self.farming and fdp.car_ordinal > 0 and fdp.speed < 20 and time.time() - reset_time > 10:
                    reset_car = reset_car + 1
                    # reset car position
                    if reset_car == 200:
                        reset_car = 0
                        self.threadPool.submit(keyboard_helper.resetcar, self)
                        reset_time = time.time()
                    continue
                else:
                    reset_car = 0

                # shifting
                iteration = self.shifting(iteration, fdp)
        except BaseException as e:
            self.logger.exception(e)
        finally:
            self.isRunning = False
            helper.close_socket(self)
            self.logger.debug(f'{self.run.__name__} finished')
