import json
import locale
import os
import socket
import sys

from car_info import CarInfo

sys.path.append(r'./forza_motorsport')
import numpy as np
from fdp import ForzaDataPacket
from matplotlib import axes
from matplotlib.pyplot import cm

import constants
import keyboard_helper
from constants import ConfigVersion


def nextFdp(server_socket: socket, format: str):
    """next fdp

    Args:
        server_socket (socket): socket
        format (str): format

    Returns:
        [ForzaDataPacket]: fdp
    """
    try:
        message, _ = server_socket.recvfrom(1024)
        return ForzaDataPacket(message, packet_format=format)
    except BaseException:
        return None


def plot_gear_ratio(forza: CarInfo, ax: axes.Axes = None, row: int = None, col: int = None):
    """plot gear ratio vs gear

    Args:
        forza (CarInfo): car info
        ax (axes.Axes, optional): figure axes. Defaults to None.
        row (int, optional): position of row. Defaults to None.
        col (int, optional): position of column. Defaults to None.
    """
    gear = np.array([item['gear'] for item in forza.records])
    time = np.array([item['time'] for item in forza.records])
    ratio = np.array([item['speed/rpm'] for item in forza.records])
    time0 = forza.records[0]['time']
    time = np.where(time > 0, time - time0, 0)

    ax[row, col].plot(time, ratio, label='speed/rpm', color='b')

    color = iter(cm.rainbow(np.linspace(0, 1, len(forza.gear_ratios))))
    for g, item in forza.gear_ratios.items():
        ax[row, col].hlines(item['ratio'], time[0], time[-1], label=f'gear {g} ratio', color=next(color), linestyles='dashed')

    ax[row, col].set_xlabel('time')
    ax[row, col].set_ylabel('ratio (km/h/rpm)', color='b')
    ax[row, col].tick_params('y', color='b')
    ax[row, col].legend()
    ax[row, col].set_title('Gear Ratio (speed/rpm)')

    ax0 = ax[row, col].twinx()
    ax0.plot(time, gear, label='gear', color='r')
    ax0.set_ylabel('gear', color='r')
    ax0.tick_params('y', colors='r')
    ax0.legend(loc=4)


def plot_torque_rpm(forza: CarInfo, ax: axes.Axes = None, row: int = None, col: int = None):
    """plot output torque vs rpm

    Args:
        forza (CarInfo): car info
        ax (axes.Axes, optional): figure axes. Defaults to None.
        row (int, optional): position of row. Defaults to None.
        col (int, optional): position of column. Defaults to None.
    """
    color = iter(cm.rainbow(np.linspace(0, 1, len(forza.gear_ratios))))
    for g, item in forza.rpm_torque_map.items():
        raw_records = forza.get_gear_raw_records(g)
        data = np.array([[i['rpm'], i['torque']] for i in raw_records[item['min_rpm_index']:item['max_rpm_index']]])
        data = np.sort(data, 0)
        c = next(color)

        rpms = np.array([item[0] for item in data])
        torque = np.array([item[1] for item in data])
        ratio = forza.gear_ratios[g]['ratio']

        ax[row, col].plot(rpms, torque / ratio, label=f'Gear {g} torque', color=c)
        ax[row, col].set_xlabel('rpm (r/m)')
        ax[row, col].set_ylabel('Torque (N/m)')
        ax[row, col].tick_params('y')

    ax[row, col].legend(loc='lower left')
    ax[row, col].set_title('Output Torque vs rpm')
    ax[row, col].grid(visible=True, color='grey', linestyle='--')


def plot_torque_speed(forza: CarInfo, ax: axes.Axes = None, row: int = None, col: int = None):
    """plot output torque vs speed

    Args:
        forza (CarInfo): car info
        ax (axes.Axes, optional): figure axes. Defaults to None.
        row (int, optional): position of row. Defaults to None.
        col (int, optional): position of column. Defaults to None.
    """
    color = iter(cm.rainbow(np.linspace(0, 1, len(forza.gear_ratios))))
    for g, item in forza.rpm_torque_map.items():
        raw_records = forza.get_gear_raw_records(g)
        data = np.array([[i['speed'], i['torque']] for i in raw_records[item['min_rpm_index']:item['max_rpm_index']]])
        data = np.sort(data, 0)
        c = next(color)

        speeds = np.array([item[0] for item in data])
        torque = np.array([item[1] for item in data])
        ratio = forza.gear_ratios[g]['ratio']

        ax[row, col].plot(speeds, torque / ratio, label=f'Gear {g} torque', color=c)
        ax[row, col].set_xlabel('speed (km/h)')
        ax[row, col].set_ylabel('Torque (N/m)')
        ax[row, col].tick_params('y')

    ax[row, col].legend(loc='upper right')
    ax[row, col].set_title('Output Torque vs Speed')
    ax[row, col].grid(visible=True, color='grey', linestyle='--')


def plot_rpm_speed(forza: CarInfo, ax: axes.Axes = None, row: int = None, col: int = None):
    """plot rpm vs speed

    Args:
        forza (CarInfo): car info
        ax (axes.Axes, optional): figure axes. Defaults to None.
        row (int, optional): position of row. Defaults to None.
        col (int, optional): position of column. Defaults to None.
    """
    color = iter(cm.rainbow(np.linspace(0, 1, len(forza.gear_ratios))))
    for g, item in forza.rpm_torque_map.items():
        raw_records = forza.get_gear_raw_records(g)
        data = np.array([[i['speed'], i['rpm']] for i in raw_records[item['min_rpm_index']:item['max_rpm_index']]])
        data = np.sort(data, 0)
        c = next(color)

        speeds = np.array([item[0] for item in data])
        rpm = np.array([item[1] for item in data])

        ax[row, col].plot(speeds, rpm, label=f'Gear {g} rpm', color=c)
        ax[row, col].set_xlabel('speed (km/h)')
        ax[row, col].set_ylabel('rpm (r/m)')
        ax[row, col].tick_params('y')

    ax[row, col].legend(loc='lower right')
    ax[row, col].set_title('rpm vs Speed')
    ax[row, col].grid(visible=True, color='grey', linestyle='--')


def convert(n: object):
    """variables to json serializable

    Args:
        n (object): object to parse

    Returns:
        serializable value
    """
    if isinstance(n, np.int32) or isinstance(n, np.int64):
        return n.item()


def dump_settings(forza: CarInfo):
    """
        write following variables from forza to settings.json:
        clutch
        upshift
        downshift

    Args:
        forza (CarInfo): car info
    """
    json_data = {
        'clutch':       forza.clutch,
        'upshift':      forza.upshift,
        'downshift':    forza.downshift,
    }

    settings_path = os.path.join(forza.config_folder, constants.setting_filename)
    forza.logger.info(f'saving program settings to {settings_path}')
    with open(settings_path, "w") as f:
        json.dump(json_data, f, default=convert, indent=4)


def dump_config(forza: CarInfo, config_version: ConfigVersion = constants.default_config_version):
    """dump config

    Args:
        forza (CarInfo): car info
    """
    try:
        forza.logger.debug(f'{dump_config.__name__} started')
        config_name = get_config_name(forza, config_version)
        forza.logger.info(f'saving config {config_name}')
        config = {
            # === dump data and result ===
            'version': config_version.name,
            'ordinal': forza.ordinal,
            'perf': forza.car_perf,
            'class': forza.car_class,
            'drivetrain': forza.car_drivetrain,
            'minGear': forza.minGear,
            'maxGear': forza.maxGear,
            'gear_ratios': forza.gear_ratios,
            'rpm_torque_map': forza.rpm_torque_map,
            'shift_point': forza.shift_point,
            'records': forza.records,
        }

        with open(os.path.join(forza.config_folder, config_name), "w") as f:
            json.dump(config, f, default=convert, indent=4)
    finally:
        forza.logger.debug(f'{dump_config.__name__} ended')


def get_config_version(forza: CarInfo, filename):
    """get config file version

    Args:
        forza (CarInfo): forza
        filename (_type_): config file name

    Returns:
        config version: config version
    """
    try:
        with open(os.path.join(forza.config_folder, filename), "r") as f:
            config = json.loads(f.read())

        if 'version' in config:
            if config['version'] == str(ConfigVersion.v2):
                return ConfigVersion.v2
            elif config['version'] == str(ConfigVersion.v1):
                return ConfigVersion.v1
            else:
                return ConfigVersion[config['version']]
        else:
            return ConfigVersion.v1
    except Exception as e:
        forza.logger.warning(f'failed to get version of {filename}: {e}')
        return ConfigVersion.v1


def get_config_name(forza: CarInfo, config_version: ConfigVersion = constants.default_config_version):
    """get config name

    Args:
        forza (CarInfo): carinfo
        config_version (ConfigVersion, optional): config version. Defaults to constants.default_config_version.

    Returns:
        str: config name
    """
    if config_version == ConfigVersion.v2:
        return f'{forza.ordinal}-{forza.car_perf}-{forza.car_drivetrain}.json'
    elif config_version == ConfigVersion.v1:
        return f'{forza.ordinal}.json'
    else:
        forza.logger.warning(f'Invalid config version {str(config_version)}')


def load_settings(forza: CarInfo):
    """
        overwrite following variables in forza:
        clutch
        upshift
        downshift

    Args:
        forza (CarInfo): car info
    """
    forza.logger.debug(f'{load_settings.__name__} started')
    settings_path = os.path.join(forza.config_folder, constants.setting_filename)
    try:
        valid_keys = keyboard_helper.keybind.keys()
        if os.path.exists(settings_path):
            forza.logger.info(f'loading program settings from {settings_path}')
            with open(settings_path, "r") as f:
                settings = json.loads(f.read())

            if 'clutch' in settings:
                clutch_shortcut = settings['clutch']
                if clutch_shortcut in valid_keys:
                    forza.clutch = clutch_shortcut
                else:
                    forza.logger.warning(f'clutch shortcut {clutch_shortcut} in {settings_path} is not valid')

            if 'upshift' in settings:
                upshift_shortcut = settings['upshift']
                if upshift_shortcut in valid_keys:
                    forza.upshift = upshift_shortcut
                else:
                    forza.logger.warning(f'upshift shortcut {upshift_shortcut} in {settings_path} is not valid')

            if 'downshift' in settings:
                downshift_shortcut = settings['downshift']
                if downshift_shortcut in valid_keys:
                    forza.downshift = downshift_shortcut
                else:
                    forza.logger.warning(f'downshift shortcut {downshift_shortcut} in {settings_path} is not valid')
    except Exception as e:
        forza.logger.warning(f'failed to load settings {settings_path}: {e}')
    finally:
        forza.logger.debug(f'{load_settings.__name__} ended')


def load_config(forza: CarInfo, path: str):
    """load config as carinfo

    Args:
        forza (CarInfo): car info
        path (str): config path
    """
    try:
        forza.logger.debug(f'{load_config.__name__} started')
        with open(os.path.join(forza.config_folder, path), "r") as f:
            config = json.loads(f.read())

        if 'ordinal' in config:
            forza.ordinal = int(config['ordinal'])

        if 'perf' in config:
            forza.car_perf = int(config['perf'])

        if 'class' in config:
            forza.car_class = int(config['class'])

        if 'drivetrain' in config:
            forza.car_drivetrain = int(config['drivetrain'])

        if 'minGear' in config:
            forza.minGear = config['minGear']

        if 'maxGear' in config:
            forza.maxGear = config['maxGear']

        if 'gear_ratios' in config:
            forza.gear_ratios = {int(key): value for key, value in config['gear_ratios'].items()}

        if 'rpm_torque_map' in config:
            forza.rpm_torque_map = {int(key): value for key, value in config['rpm_torque_map'].items()}

        if 'shift_point' in config:
            forza.shift_point = {int(key): value for key, value in config['shift_point'].items()}

        if 'records' in config:
            forza.records = config['records']
    except BaseException as e:
        forza.logger.exception(e)
    finally:
        forza.logger.debug(f'{load_config.__name__} ended')


def rgb(r, g, b):
    """generate rbg in hex

    Args:
        r
        g
        b

    Returns:
        rgb in hex
    """
    return "#%s%s%s" % tuple([hex(int(c * 255))[2:].rjust(2, "0") for c in (r, g, b)])


def get_sys_lang():
    try:
        lang = locale.getdefaultlocale()[0]
        return 1 if 'zh' in lang else 0
    except Exception:
        return constants.default_language


def create_socket(forza: CarInfo):
    forza.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    forza.server_socket.settimeout(1)
    forza.server_socket.bind((forza.ip, forza.port))
    forza.logger.info(f'listening on IP {forza.ip}, Port {forza.port}')


def close_socket(forza: CarInfo):
    forza.server_socket.close()
    forza.logger.info('socket closed')
