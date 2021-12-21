import logging
import os
import sys

import constants


class Logger:
    def __init__(self):
        """initialization
        """
        log_folder = os.path.join(constants.root_path, 'log')
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)
        file_handler = logging.FileHandler(os.path.join(log_folder, 'forza5.log'), mode='w')
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)


        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s.%(msecs)03d | \t %(levelname)s:\t %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                file_handler,
                console_handler
            ]
        )

    def __call__(self, name: str):
        """get logger

        Args:
            name (str): logger name

        Returns:
            [logger]: get logger
        """
        return logging.getLogger(name)

logger = Logger()('forza5')
