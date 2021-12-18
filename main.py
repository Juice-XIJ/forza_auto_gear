import sys
import os

sys.path.append(r'./forza_motorsport')

from concurrent.futures import ThreadPoolExecutor
import forza
from logger import logger
from pynput.keyboard import Listener
import json

import keyboard_helper

from os import listdir
from os.path import isfile, join
port = 12350
packet_format = 'fh4'

threadPool = ThreadPoolExecutor(max_workers=8, thread_name_prefix="exec")
forza5 = forza.Forza(port, threadPool, packet_format, clutch=True)

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
        records = []
        # prepare records
        if hasattr(forza5, 'records') and len(forza5.records) > 0:
            records = forza5.records
            ordinal = records[0]['car_ordinal']
            with open(f'./forza_auto_gear/dump/{ordinal}', 'w') as dump:
                for item in records:
                    dump.write(f'{item}\n')
        else:
            default_ordinal = '444'
            with open (f'./forza_auto_gear/dump/{default_ordinal}', 'r') as dump:
                for line in dump:
                    records.append(json.loads(line.replace('\n', '').replace('\'', '\"')))
                forza5.records = records

        if len(records) > 0:
            logger.info('Analysis')
            forza5.analyze(records)
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
                forza5.auto_gear()
            threadPool.submit(starting)
if __name__ == "__main__":

    dump = [f for f in listdir(forza5.dump_folder) if isfile(join(forza5.dump_folder, f))]
    with open (os.path.join(forza5.dump_folder, dump[0]), 'r') as dump:
        for line in dump:
            forza5.records.append(json.loads(line.replace('\n', '').replace('\'', '\"')))

    logger.info('Forza Auto Shift Started!!!')
    with Listener(on_press=presskey) as listener:
        listener.join()
    pass