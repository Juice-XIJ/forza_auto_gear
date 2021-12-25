import os
import sys

sys.path.append(r'./forza_motorsport')

import warnings
from concurrent.futures import ThreadPoolExecutor

from pynput.keyboard import Listener

import constants
import forza
import helper

# suppress matplotlib warning while running in threads
warnings.filterwarnings("ignore", category=UserWarning)
threadPool = ThreadPoolExecutor(max_workers=8, thread_name_prefix="exec")
forza5 = forza.Forza(threadPool, packet_format=constants.packet_format, clutch=constants.enable_clutch)


def on_press(key):
    """on press callback

    Args:
        key: key
    """
    if key == constants.collect_data:
        if forza5.isRunning:
            forza5.logger.info('stopping gear test')

            def stopping():
                forza5.isRunning = False

            threadPool.submit(stopping)
        else:
            forza5.logger.info('starting gear test')

            def starting():
                forza5.isRunning = True
                forza5.test_gear()

            threadPool.submit(starting)
    elif key == constants.analysis:
        if len(forza5.records) <= 0:
            forza5.logger.info(f'load config {constants.example_car_ordinal}.json for analysis as an example')
            helper.load_config(forza5,
                               os.path.join(constants.root_path, 'example', f'{constants.example_car_ordinal}.json'))
        forza5.logger.info('Analysis')
        threadPool.submit(forza5.analyze)
    elif key == constants.auto_shift:
        if forza5.isRunning:
            forza5.logger.info('stopping auto gear')

            def stopping():
                forza5.isRunning = False

            threadPool.submit(stopping)
        else:
            forza5.logger.info('starting auto gear')

            def starting():
                forza5.isRunning = True
                forza5.run()

            threadPool.submit(starting)
    elif key == constants.stop:
        forza5.isRunning = False
        forza5.logger.info('stopped')
    elif key == constants.close:
        forza5.isRunning = False
        threadPool.shutdown(wait=False)
        forza5.logger.info('bye~')
        exit()


if __name__ == "__main__":
    try:
        forza5.logger.info('Forza Auto Gear Shifting Started!!!')
        # listen to keyboard press event
        with Listener(on_press=on_press) as listener:
            listener.join()
    finally:
        forza5.isRunning = False
        threadPool.shutdown(wait=False)
        forza5.logger.info('Forza Auto Gear Shifting Ended!!!')
