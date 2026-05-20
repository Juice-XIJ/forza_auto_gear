import enum
import os
from pynput.keyboard import Key


# config version
class ConfigVersion(enum.Enum):
    v1 = 1,
    v2 = 2


default_config_version = ConfigVersion.v2

# repo path
root_path = os.path.dirname(os.path.abspath(__file__))
setting_filename = 'settings.json'

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
perf_sticker_background = "#FFFFFF"

# car info relx, rely
car_info_leftbound_relx = 0.08
car_info_rightbound_relx = 0.9
car_info_topbound_rely = 0.195
car_info_bottombound_rely = 0.815
car_info_line_gap = 0.065

# car drivetrain
car_drivetrain_list = [
    ('FWD', '前驱'),
    ('RWD', '后驱'),
    ('AWD', '四驱'),
    ('N', 'N')
]

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

# car class mapping
car_class_list = ['D', 'C', 'B', 'A', 'S1', 'S2', 'X', "N"]
car_class_color = ['#3dafd1', '#edc786', '#f28240', '#e22b2a', '#8729e2', '#3256ba', '#46ce67', text_color]

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
downShiftCoolDown = 0.35  # cooldown after down shift
upShiftCoolDown = 0.35  # cooldown after up shift
blipThrottleDuration = 0.12  # blip the throttle duration. Should be short since keyboard is 100% acceleration output

# === Gear Shift Settings ===
shift_factor = 0.97
offroad_rally_shift_factor = 0.93

# === Test Settings ===
test_car_ordinal = 'analysis_test'

# === Text Settings ===
# All UI strings are loaded from locales/{en,zhcn}.json via i18n.t.
# constants.foo_txt[lang_index] continues to work as before.
from i18n import t as _t  # noqa: E402  (intentional late import after constants above)

select_language_txt = _t('select_language_txt')
language_txt = _t('language_txt')
default_language = 0

clutch_shortcut_txt = _t('clutch_shortcut_txt')
upshift_shortcut_txt = _t('upshift_shortcut_txt')
downshift_shortcut_txt = _t('downshift_shortcut_txt')
clutch_txt = _t('clutch_txt')
farm_txt = _t('farm_txt')
offroad_rally_txt = _t('offroad_rally_txt')
car_id = _t('car_id')
car_class = _t('car_class')
car_perf = _t('car_perf')
car_drivetrain = _t('car_drivetrain')
tire_information_txt = _t('tire_information_txt')
accel_txt = _t('accel_txt')
brake_txt = _t('brake_txt')
shift_point_txt = _t('shift_point_txt')
tree_value_txt = _t('tree_value_txt')
speed_txt = _t('speed_txt')
rpm_txt = _t('rpm_txt')
collect_button_txt = _t('collect_button_txt')
analysis_button_txt = _t('analysis_button_txt')
run_button_txt = _t('run_button_txt')
pause_button_txt = _t('pause_button_txt')
exit_button_txt = _t('exit_button_txt')
clear_log_txt = _t('clear_log_txt')

program_info_txt = _t('program_info_txt')
