import logging
import sys

file_handler = logging.FileHandler(r'./forza_auto_gear/log/forza5.log', mode='w')
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

logger = logging.getLogger('Forza5')