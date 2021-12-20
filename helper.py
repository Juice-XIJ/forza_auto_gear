import json
import os
import sys
from socket import socket

from car_info import CarInfo

sys.path.append(r'./forza_motorsport')
import numpy as np
from fdp import ForzaDataPacket
from matplotlib import axes
from matplotlib.pyplot import cm

from logger import logger


def nextFdp(server_socket: socket, format: str):
    """next fdp

    Args:
        server_socket (socket): socket
        format (str): format

    Returns:
        [ForzaDataPacket]: fdp
    """
    message, _ = server_socket.recvfrom(1024)
    return ForzaDataPacket(message, packet_format=format)

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

        ax[row, col].plot(rpms, torque * ratio, label=f'Gear {g} torque', color=c)
        ax[row, col].set_xlabel('rpm (r/m)')
        ax[row, col].set_ylabel('Torque (N/m)')
        ax[row, col].tick_params('y')

    ax[row, col].legend(loc=8)
    ax[row, col].set_title('Torque vs rpm')
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

        ax[row, col].plot(speeds, torque * ratio, label=f'Gear {g} torque', color=c)
        ax[row, col].set_xlabel('speed (km/h)')
        ax[row, col].set_ylabel('Torque (N/m)')
        ax[row, col].tick_params('y')

    ax[row, col].legend(loc='upper right')
    ax[row, col].set_title('Torque vs Speed')
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

    ax[row, col].legend(loc='upper right')
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

def dump_config(forza: CarInfo):
    """dump config

    Args:
        forza (CarInfo): car info
    """
    try:
        logger.debug(f'{dump_config.__name__} started')
        forza.ordinal = forza.records[0]['car_ordinal']
        config = {
            # === dump data and result ===
            'ordinal': forza.ordinal,
            'minGear': forza.minGear,
            'maxGear': forza.maxGear,
            'gear_ratios': forza.gear_ratios,
            'rpm_torque_map': forza.rpm_torque_map,
            'shift_point': forza.shift_point,
            'records': forza.records,
        }

        with open(os.path.join(forza.config_folder, f'{forza.ordinal}.json'), "w") as f:
            json.dump(config, f, default=convert, indent=4)
    finally:
        logger.debug(f'{dump_config.__name__} ended')

def load_config(forza: CarInfo, path: str):
    """load config as carinfo

    Args:
        forza (CarInfo): car info
        path (str): config path
    """
    try:
        logger.debug(f'{load_config.__name__} started')
        with open(os.path.join(forza.config_folder, path), "r") as f:
            config = json.loads(f.read())

        if 'ordinal' in config:
            forza.ordinal = str(config['ordinal'])

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
    finally:
        logger.debug(f'{load_config.__name__} ended')
