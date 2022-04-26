import logging
import os
import sys
from tkinter.scrolledtext import ScrolledText

import constants


class TextHandler(logging.Handler):

    def __init__(self, text: ScrolledText):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        self.text = text
        self.text.tag_config(logging.getLevelName(logging.DEBUG))
        self.text.tag_config(logging.getLevelName(logging.INFO))
        self.text.tag_config(logging.getLevelName(logging.WARNING), foreground='#fca862')
        self.text.tag_config(logging.getLevelName(logging.ERROR), foreground='#ff3333')
        self.text.tag_config(logging.getLevelName(logging.CRITICAL), foreground='#b30000')
        self.line_limitation = 6000.0
        self.line_check = 6500.0

    def num_lines(self):
        return int(self.text.index('end').split('.')[0]) - 1

    def emit(self, record: logging.LogRecord):
        msg = self.format(record)
        self.text.insert('end', msg + '\n', record.levelname)
        self.text.see('end')
        if self.num_lines() > self.line_check:
            self.text.delete(1.0, self.line_check - self.line_limitation)


class Logger:

    def __init__(self, custom_handler=None):
        """initialization
        """
        log_folder = os.path.join(constants.root_path, 'log')
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)
        file_handler = logging.FileHandler(os.path.join(log_folder, 'forza5.log'), mode='w')

        if custom_handler is None:
            custom_handler = logging.StreamHandler(sys.stdout)

        custom_handler.setLevel(logging.INFO)

        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)03d | \t %(levelname)s:\t %(message)s', datefmt='%Y-%m-%d %H:%M:%S', handlers=[file_handler, custom_handler])

    def __call__(self, name: str):
        """get logger

        Args:
            name (str): logger name

        Returns:
            [logger]: get logger
        """
        return logging.getLogger(name)
