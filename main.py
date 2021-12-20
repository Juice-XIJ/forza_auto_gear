import os
import sys

sys.path.append(r'./forza_motorsport')

from concurrent.futures import ThreadPoolExecutor

from pynput.keyboard import Listener

import constants
import forza
import helper
import keyboard_helper
from logger import logger

threadPool = ThreadPoolExecutor(max_workers=8, thread_name_prefix="exec")
forza5 = forza.Forza(threadPool, constants.packet_format, clutch=constants.enable_clutch)

dir_path = os.path.dirname(os.path.abspath(__file__))

def on_press(key):
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
            logger.info(f'load config {constants.default_car_ordinal}.json for analysis')
            helper.load_config(forza5, os.path.join(dir_path, 'config', f'{constants.default_car_ordinal}.json'))
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
    logger.info('Forza Auto Gear Shifting Started!!!')

    # create folders if not existed
    log_path = os.path.join(dir_path, 'log')
    if not os.path.exists(log_path):
        os.makedirs(log_path)
        logger.debug(f'log folder {log_path} created')
    if not os.path.exists(forza5.config_folder):
        os.makedirs(forza5.config_folder)
        logger.debug(f'config folder {forza5.config_folder} created')

    # listen to keyboard press event
    with Listener(on_press=on_press) as listener:
        listener.join()
