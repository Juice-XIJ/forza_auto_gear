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
blipThrottleDuration = 0.3  # blip the throttle duration. Should be short since keyboard is 100% acceleration output

# === Gear Shift Settings ===
shift_factor = 0.99
offroad_rally_shift_factor = 0.93

# === Test Settings ===
test_car_ordinal = 'analysis_test'

# === Text Settings ===
select_language_txt = ['Select Language:', '选择语言:']
language_txt = ['English', '中文']
default_language = 0

clutch_shortcut_txt = ['Clutch Shortcut:', '离合快捷键:']
upshift_shortcut_txt = ['Upshift Shortcut:', '升档快捷键:']
downshift_shortcut_txt = ['Downshift Shortcut:', '降档快捷键:']
clutch_txt = ['Enable Clutch', '开启离合']
farm_txt = ['Enable Farm', '开启刷图']
offroad_rally_txt = ['Offroad, Rally', '越野，拉力']
car_id = ['Car ID:', '车辆序号:']
car_class = ['Car Class:', '车辆等级:']
car_perf = ['Car Performance:', '车辆性能:']
car_drivetrain = ['Car Drivetrain:', '车辆传动:']
tire_information_txt = ['Tire Information', '轮胎信息']
accel_txt = ['Acceleration', '加速']
brake_txt = ['Brake', '刹车']
shift_point_txt = ['Shift Point', '换挡点']
tree_value_txt = ['Value', '结果']
speed_txt = ['Speed', '速度']
rpm_txt = ['RPM', '转速']
collect_button_txt = ['Collect Data', '收集数据']
analysis_button_txt = ['Analysis', '分析数据']
run_button_txt = ['Run Auto Shift', '运行自动换挡']
pause_button_txt = ['Pause', '暂停']
exit_button_txt = ['Exit', '退出']
clear_log_txt = ['Clear', '清空']

program_info_txt = [
    'If you found any issues, or want to contribute to the program, feel free to visit github: https://github.com/Juice-XIJ/forza_auto_gear',
    '如果您发现任何bugs，或想参加这个project，欢迎访问我的github: https://github.com/Juice-XIJ/forza_auto_gear'
]
