import os
import sys

sys.path.append(r'./forza_motorsport')

import json
from concurrent.futures import ThreadPoolExecutor
from os import listdir
from os.path import isfile, join

from pynput.keyboard import Listener

import forza
import helper
import keyboard_helper
from logger import logger

port = 12350
packet_format = 'fh4'

threadPool = ThreadPoolExecutor(max_workers=8, thread_name_prefix="exec")
forza5 = forza.Forza(port, threadPool, packet_format, clutch=True)

car_ordinal = '444'
dir_path = os.path.dirname(os.path.abspath(__file__))

def presskey(key):
    t = keyboard_helper.get_key_name(key)
    if t == forza5.collect_data:
        if forza5.isRunning:
            logger.info('stopping gear test')
            def stopping():
                forza5.isRunning = False
            threadPool.submit(stopping)
        else:
            logger.info('starting gear test')
            def starting():
                forza5.isRunning = True
                forza5.test_gear()
            threadPool.submit(starting)
    elif t == forza5.analysis:
        if len(forza5.records) <= 0:
            logger.info(f'load config {car_ordinal}.json for analysis')
            helper.load_config(forza5, os.path.join(dir_path, 'config', f'{car_ordinal}.json'))
        logger.info('Analysis')
        forza5.analyze()
        helper.dump_config(forza5)
    elif t == forza5.auto_shift:
        if forza5.isRunning:
            logger.info('stopping auto gear')
            def stopping():
                forza5.isRunning = False
            threadPool.submit(stopping)
        else:
            logger.info('starting auto gear')
            def starting():
                forza5.isRunning = True
                forza5.run()
            threadPool.submit(starting)

if __name__ == "__main__":
    # forza5.load_config(os.path.join(forza5.config_folder, '3250.json'))
    logger.info('Forza Auto Shift Started!!!')
    with Listener(on_press=presskey) as listener:
        listener.join()
    pass

def convert_dump_to_config():
    dump_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dump')
    for dump in [f for f in listdir(dump_folder) if isfile(join(dump_folder, f))]:
        with open (os.path.join(dump_folder, dump), 'r') as dump:
            forza5.records = []
            for line in dump:
                forza5.records.append(json.loads(line.replace('\n', '').replace('\'', '\"')))
            forza5.analyze()
            forza5.dump_config()
