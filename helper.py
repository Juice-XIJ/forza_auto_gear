import json
import os
import sys

sys.path.append(r'./forza_motorsport')
import numpy as np
from fdp import ForzaDataPacket
from matplotlib import axes
from matplotlib.pyplot import cm

from logger import logger


def nextFdp(server_socket, format):
    message, _ = server_socket.recvfrom(1024)
    return ForzaDataPacket(message, packet_format=format)

def plot_gear_ratio(forza, ax: axes.Axes = None, row: int = None, col: int = None):
    gear = np.array([item['gear'] for item in forza.records])
    time = np.array([item['time'] for item in forza.records])
    ratio = np.array([item['speed/rpm'] for item in forza.records])
    time0 = forza.records[0]['time']
    time = np.where(time > 0, time - time0, 0)

    ax[row, col].plot(time, ratio, label='speed/rpm', color='b')

    color = iter(cm.rainbow(np.linspace(0, 1, len(forza.gear_ratios))))
    for _, item in forza.gear_ratios.items():
        g = item['records'][0]['gear']
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

def plot_torque_rpm(forza, ax: axes.Axes = None, row: int = None, col: int = None):
    color = iter(cm.rainbow(np.linspace(0, 1, len(forza.gear_ratios))))
    for _, item in forza.rpm_torque_map.items():
        g = item['records'][0]['gear']
        data = np.array([[i['rpm'], i['torque']] for i in item['records'][item['min_rpm_index']:item['max_rpm_index']]])
        data = np.sort(data, 0)
        c = next(color)
        
        rpms = np.array([item[0] for item in data])
        torque = np.array([item[1] for item in data])

        ax[row, col].plot(rpms, torque, label=f'Gear {g} torque', color=c)
        ax[row, col].set_xlabel('rpm (r/m)')
        ax[row, col].set_ylabel('Torque (N/m)')
        ax[row, col].tick_params('y')

    ax[row, col].legend(loc=8)
    ax[row, col].set_title('Torque vs rpm')
    ax[row, col].grid(visible=True, color='grey', linestyle='--')

def plot_torque_speed(forza, ax: axes.Axes = None, row: int = None, col: int = None):
    color = iter(cm.rainbow(np.linspace(0, 1, len(forza.gear_ratios))))
    for _, item in forza.rpm_torque_map.items():
        g = item['records'][0]['gear']
        data = np.array([[i['speed'], i['torque']] for i in item['records'][item['min_rpm_index']:item['max_rpm_index']]])
        data = np.sort(data, 0)
        c = next(color)
        
        speeds = np.array([item[0] for item in data])
        torque = np.array([item[1] for item in data])

        ax[row, col].plot(speeds, torque, label=f'Gear {g} torque', color=c)
        ax[row, col].set_xlabel('speed (km/h)')
        ax[row, col].set_ylabel('Torque (N/m)')
        ax[row, col].tick_params('y')

    ax[row, col].legend(loc='upper right')
    ax[row, col].set_title('Torque vs Speed')
    ax[row, col].grid(visible=True, color='grey', linestyle='--')

def plot_rpm_speed(forza, ax: axes.Axes = None, row: int = None, col: int = None):
    color = iter(cm.rainbow(np.linspace(0, 1, len(forza.gear_ratios))))
    for _, item in forza.rpm_torque_map.items():
        g = item['records'][0]['gear']
        data = np.array([[i['speed'], i['rpm']] for i in item['records'][item['min_rpm_index']:item['max_rpm_index']]])
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


def dump_config(forza):
    try:
        logger.debug(f'{dump_config.__name__} started')
        forza.ordinal = forza.records[0]['car_ordinal']
        config = {
            # === dump operation setting ===
            'stop': forza.stop,
            'close': forza.close,
            'collect_data': forza.collect_data,
            'analysis': forza.analysis,
            'auto_shift': forza.auto_shift,

            # === dump data and result ===
            'ordinal': forza.ordinal,
            'minGear': forza.minGear,
            'maxGear': forza.maxGear,
            'gear_ratios': {key: {'ratio': value['ratio'], 'c': value['c']} for key, value in forza.gear_ratios.items()},
            'rpm_torque_map': {key: {'min_rpm_index': value['min_rpm_index'], 'max_rpm_index': value['max_rpm_index']} for key, value in forza.rpm_torque_map.items()},
            'shift_point': {key: {'rpmo': value['rpmo'], 'speed': value['speed']} for key, value in forza.shift_point.items()},
            'records': forza.records,
        }

        with open(os.path.join(forza.config_folder, f'{forza.ordinal}.json'), "w") as f:
            def convert(n):
                if isinstance(n, np.int32) or isinstance(n, np.int64):
                    return n.item()
            json.dump(config, f, default=convert, indent=4)
    finally:
        logger.debug(f'{dump_config.__name__} ended')

def load_config(forza, path):
    try:
        logger.debug(f'{load_config.__name__} started')
        with open(os.path.join(forza.config_folder, path), "r") as f:
            config = json.loads(f.read())
        
        if 'stop' in config:
            forza.stop = config['stop']
        
        if 'close' in config:
            forza.close = config['close']

        if 'collect_data' in config:
            forza.collect_data = config['collect_data']

        if 'analysis' in config:
            forza.analysis = config['analysis']

        if 'auto_shift' in config:
            forza.auto_shift = config['auto_shift']

        if 'ordinal' in config:
            forza.ordinal = str(config['ordinal'])

        if 'minGear' in config:
            forza.minGear = config['minGear']

        if 'maxGear' in config:
            forza.maxGear = config['maxGear']

        if 'gear_ratios' in config:
            forza.gear_ratios = {int(key): {'ratio': value['ratio'], 'c': value['c']} for key, value in config['gear_ratios'].items()}

        if 'rpm_torque_map' in config:
            forza.rpm_torque_map = {int(key): {'min_rpm_index': value['min_rpm_index'], 'max_rpm_index': value['max_rpm_index']} for key, value in config['rpm_torque_map'].items()}

        if 'shift_point' in config:
            forza.shift_point = {int(key): {'rpmo': value['rpmo'], 'speed': value['speed']} for key, value in config['shift_point'].items()}

        if 'records' in config:
            forza.records = config['records']
    finally:
        logger.debug(f'{load_config.__name__} ended')
