import os

# repo path
root_path = os.path.dirname(os.path.abspath(__file__))

# socket information
ip = '127.0.0.1'
port = 12350

# data format
packet_format = 'fh4'

# clutch setup
enable_clutch = True

# default car config
example_car_ordinal = 'example'

# === short-cut ===
stop = 'pause' # stop program
close = 'end' # close program
collect_data = 'f10'
analysis = 'f8'
auto_shift = 'f7'

# === Keyboard ===
clutch = 'i' # clutch
upshift = 'e' # up shift
downshift = 'q' # down shift
acceleration = 'w' # acceleration

# === Delay Settings ===
delayClutchtoShift = 0 # delay between pressing clutch and shift
delayShifttoClutch = 0.06 # delay between pressing shift and releasing clutch
downShiftCoolDown = 0.3 # cooldown after down shift
upShiftCoolDown = 0.2 # cooldown after up shift
blipThrottleDuration = 0.1 # blip the throttle duration. Should be short since keyboard is 100% acceleration output