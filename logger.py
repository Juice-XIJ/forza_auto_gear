import logging
import os
import sys

log_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log')
file_handler = logging.FileHandler(os.path.join(log_folder, 'forza5.log'), mode='w')
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

logging.basicConfig(
    level=logging.DEBUG,
    # format='%(asctime)s.%(msecs)03d | \t %(levelname)s:\t %(message)s',
    format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(funcName)s - %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        file_handler,
        console_handler
    ]
)

logger = logging.getLogger('Forza5')
