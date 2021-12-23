import os

# REPO PATH
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

# SOCKET INFORMATION
IP = '127.0.0.1'
PORT = 12350

# DATA FORMAT
PACKET_FORMAT = 'fh4'

# CLUTCH SETUP
ENABLE_CLUTCH = True

# DEFAULT CAR CONFIG
EXAMPLE_CAR_ORDINAL = 'example'

# === SHORT-CUT ===
STOP = 'pause' # STOP PROGRAM
CLOSE = 'end' # CLOSE PROGRAM
COLLECT_DATA = 'F10'
ANALYSIS = 'F8'
AUTO_SHIFT = 'F7'

# === KEYBOARD ===
CLUTCH = 'I' # CLUTCH
UPSHIFT = 'E' # UP SHIFT
DOWNSHIFT = 'Q' # DOWN SHIFT
ACCELERATION = 'W' # ACCELERATION

# === DELAY SETTINGS ===
DELAYCLUTCHTOSHIFT = 0 # DELAY BETWEEN PRESSING CLUTCH AND SHIFT
DELAYSHIFTTOCLUTCH = 0.033 # DELAY BETWEEN PRESSING SHIFT AND RELEASING CLUTCH
DOWNSHIFTCOOLDOWN = 0.4 # COOLDOWN AFTER DOWN SHIFT
UPSHIFTCOOLDOWN = 0.2 # COOLDOWN AFTER UP SHIFT
BLIPTHROTTLEDURATION = 0.1 # BLIP THE THROTTLE DURATION. SHOULD BE SHORT SINCE KEYBOARD IS 100% ACCELERATION OUTPUT


# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': True,
#     'root': {
#         'level': 'WARNING',
#         'handlers': ['sentry'],
#     },
#     'formatters': {
#         'verbose': {
#             'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
#         },
#     },
#     'handlers': {
#         'sentry': {
#             'level': 'ERROR',

#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#             'formatter': 'verbose'
#         }
#     },
#     'loggers': {
#         'django.db.backends': {
#             'level': 'ERROR',
#             'handlers': ['console'],
#             'propagate': False,
#         },
#         'raven': {
#             'level': 'DEBUG',
#             'handlers': ['console'],
#             'propagate': False,
#         },
#         'sentry.errors': {
#             'level': 'DEBUG',
#             'handlers': ['console'],
#             'propagate': False,
#         },
#     },
# }