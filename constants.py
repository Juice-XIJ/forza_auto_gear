import os
from pynput.keyboard import Key

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

# === UI settings ===
background_color = "#1a181a"
text_color = "#a1a1a1"

# tire canvas info: Position: [start_x1_factor, start_y1_factor, s radius]
x_padding_left = 0.025
x_padding_right = 0.025
y_padding_top = 0.075
y_padding_bot = 0.025
width = 0.1
height = 0.25
x_dis = 0.1
y_dis = 0.1
radius = 12
tire_canvas_relx = 0.5
tire_canvas_rely = 0.5
tire_canvas_relwidth = width * 2 + x_dis + x_padding_left + x_padding_right
tire_canvas_relheight = height * 2 + y_dis + y_padding_top + y_padding_bot
tires = {
    "FL": [x_padding_left, y_padding_top, x_padding_left + width, y_padding_top + height, radius],
    "FR": [x_padding_left + width + x_dis, y_padding_top, x_padding_left + width * 2 + x_dis, y_padding_top + height, radius],
    "RL": [x_padding_left, y_padding_top + height + y_dis, x_padding_left + width, y_padding_top + height * 2 + y_dis, radius],
    "RR": [x_padding_left + width + x_dis, y_padding_top + height + y_dis, x_padding_left + width * 2 + x_dis, y_padding_top + height * 2 + y_dis, radius]
}

# === short-cut ===
stop = Key.pause  # stop program
close = Key.end  # close program
collect_data = Key.f10
analysis = Key.f8
auto_shift = Key.f7

# === Keyboard ===
clutch = 'i'  # clutch
upshift = 'e'  # up shift
downshift = 'q'  # down shift
acceleration = 'w'  # acceleration
brake = 's'  # brake
boundKeys = [stop.name, close.name, collect_data.name, analysis.name, auto_shift.name]

# === Delay Settings ===
delayClutchtoShift = 0  # delay between pressing clutch and shift
delayShifttoClutch = 0.06  # delay between pressing shift and releasing clutch
downShiftCoolDown = 0.3  # cooldown after down shift
upShiftCoolDown = 0.2  # cooldown after up shift
blipThrottleDuration = 0.1  # blip the throttle duration. Should be short since keyboard is 100% acceleration output

# === Gear Shift Settings ===
shift_factor = 0.99
