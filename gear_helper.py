import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from scipy.ndimage.measurements import label

import keyboard_helper
from logger import logger

figure_threadPool = ThreadPoolExecutor(max_workers=3, thread_name_prefix="exec")

# === Keyboard ===
clutch = 'i' # clutch
upshift = 'e' # up shift
downshift = 'q' # down shift
acceleration = 'w' # acceleration

# === Delay Setings ===
delayClutchtoShift = 0 # delay between pressing clutch and shift
delayShifttoClutch = 0.033 # delay between pressing shift and releasing clutch
downShiftCoolDown = 0.4 # cooldown after down shift
upShiftCoolDown = 0.2 # cooldown after up shift
blipThrottleDuration = 0.1 # blip the throttle duration. Should be short since keyboard is 100% acceleration output

# === Optimal Shift Point ===
# speed = rpm * 60 * (dia of tire * PI ) / gear ratio / other ratio
# dia of tire, other ratio and PI are constants, said C. So we have:
# speed = C * rpm * gR (gear ratio)
# The best shift point is using: https://glennmessersmith.com/shiftpt.html
#
# Now we want to shift from Gear G1 to Gear G2 (continued) at r (rpm), the gear ratio is gR1 and gR2 while at G1 and G2.
# Let's said getTorque(r) return the Torque while rpm is r.
# We have: delta = getTorque(r) * gR1 - getTorque(r * gR2 / gR1) * gR2
# The goal is to make sure the delta is closed to 0. Then the r is the optimal shift point, said orpm.
# We cannot get the gR1 or gR2 directly but we know we could get C * gR from speed / rpm, said S/R, while at Gear G. 
# Then we could calculate gRn at Gn by (Sn / Rn), said gR(G) is the ration at Gear G
# Meanwhile the C doesn't influence the delta, we have:
# delta(r, G) = getTorque(r) * gR(G) - getTorque(r * gR(G + 1) / gR(G)) * gR(G + 1)
# and delta(r, G) -> 0
def set_car_properties(records: dict, forza):
    gears = np.array([item['gear'] for item in records])
    gear_list = np.unique(gears)
    forza.minGear = gear_list.min()
    forza.maxGear = gear_list.max()
    forza.cutoff = np.max([record['rpm'] for record in records]) - 50

def get_rpm_torque_map(records: dict, forza):
    res = {}
    
    # find rpm range
    for g in range(forza.minGear, forza.maxGear + 1):
        torques = np.array([item['torque'] for item in records[g]])

        # first min_rpm_index that torque > 0 and max_rpm_index point that torque < 0 and after min_rpm_index
        min_rpm_index = np.argmax(torques > 0)
        max_rpm_index = np.argmax(torques[min_rpm_index:] < 0) + min_rpm_index

        res[g] = {
            'min_rpm_index': min_rpm_index,
            'max_rpm_index': max_rpm_index
        }

        lower_rpm = records[g][min_rpm_index]['rpm'] 
        upper_rpm = records[g][max_rpm_index]['rpm']
        logger.info(f'For Gear {g}, the min_rpm_index: {min_rpm_index}, max_rpm_index: {max_rpm_index}, rpm range: {lower_rpm} ~ {upper_rpm}')
        
        # import matplotlib.pyplot as plt
        # rpms = np.array([item['rpm'] for item in rpm_to_torque[g]])
        # plt.plot(range(len(torques)), rpms, color='b')
        # plt.plot(range(min_rpm_index, max_rpm_index), rpms[min_rpm_index: max_rpm_index], color='r')
        # plt.title(f'Gear {g}')
        # plt.show()
    return res

def get_gear_ratio_map(records: dict):
    res = {}

    for gear, items in records.items():
        var = 99999
        ratio = -1
        for index in range(0, len(items) - 20, 5):
            t = items[index:index + 20]
            ratios = [item['speed/rpm'] for item in t]
            tmp_var = np.var(ratios)
            if tmp_var < var:
                ratio = np.average(ratios)
                var = tmp_var
        
        logger.info(f'Gear ratio at Gear {gear} is {ratio}')
        res[gear] = {
            'ratio': ratio,
        }

    return res

def get_torque(r, record_by_gear):
    rpms = np.array([item['rpm'] for item in record_by_gear])

    # find the closest rpm vs r in rpms list
    r_index = np.abs(rpms - r).argmin()
    return record_by_gear[r_index]['torque']

def get_gear_ratio(g, gear_ratios: dict):
    return gear_ratios[g]['ratio']

def calculateOptimalShiftPoint(forza):
    # result, (gear, record)
    res = {}

    # records by gears
    records_by_gears = {}    
    for items in forza.records:
        if items['gear'] not in records_by_gears.keys():
            records_by_gears[items['gear']] = []
        records_by_gears[items['gear']].append(items)

    # set car properties
    set_car_properties(forza.records, forza)

    # get gear ratio
    forza.gear_ratios = get_gear_ratio_map(records_by_gears)

    # search optimal rpm from gear G to gear G + 1
    forza.rpm_torque_map = get_rpm_torque_map(records_by_gears, forza)
    for gear, tuple in forza.gear_ratios.items():
        if gear == forza.maxGear:
            break
        
        rpm_torque = forza.rpm_torque_map[gear]
        rpm_to_torque = records_by_gears[gear]
        rpm_to_torque1 = records_by_gears[gear + 1]

        min_dt_torque = 99999
        rpmo = -1
        ratio = tuple['ratio']
        # search optimal rpm. Starting from max rpm.
        max_rpm = int(rpm_to_torque[rpm_torque['max_rpm_index']]['rpm'])
        min_rpm = int(rpm_to_torque[rpm_torque['min_rpm_index']]['rpm'])
        for r in range(max_rpm, min_rpm, -50):
            # delta(r, G) = getTorque(r) * gR(G) - getTorque(r * gR(G + 1) / gR(G)) * gR(G + 1)
            ratio1 = get_gear_ratio(gear + 1, forza.gear_ratios)
            delta = get_torque(r, rpm_to_torque) * ratio - ratio1 * get_torque(r * ratio1 / ratio, rpm_to_torque1)
            if abs(delta) < min_dt_torque:
                rpmo = r
                min_dt_torque = delta 

        logger.info(f'Optimal shift point from {gear} to {gear + 1} is at rpm ({min_rpm} ~ {max_rpm}) = {rpmo} r/m, speed = {rpmo * ratio} km/h, delta output torque = {min_dt_torque}')
        res[gear] = {
            'rpmo': rpmo,
            'speed': rpmo * ratio
        }
    
    return res

def blipThrottle():
    keyboard_helper.pressdown_str(acceleration)
    time.sleep(blipThrottleDuration)
    keyboard_helper.pressup_str(acceleration)

def upShiftHandle(gear, forza):
    cur = time.time()
    if gear < forza.maxGear and cur - forza.last_upshift >= upShiftCoolDown:
        logger.info(f'[UpShift] up shift fired. gear < maxGear ({gear}, {forza.maxGear}) and gap >= upShiftCoolDown ({cur - forza.last_upshift}, {upShiftCoolDown})')
        forza.last_upshift = cur
        if forza.clutch:
            def press():
                keyboard_helper.pressdown_str(clutch)
                logger.debug(f'[UpShift] clutch {clutch} down on {gear}')
            forza.threadPool.submit(press)

        time.sleep(delayClutchtoShift)
        # up shift and delay
        keyboard_helper.press_str(upshift)
        logger.debug(f'[UpShift] upshift {upshift} down and up on {gear}')
        
        time.sleep(delayShifttoClutch)
        if forza.clutch:
            # release clutch
            keyboard_helper.pressup_str(clutch)
            logger.debug(f'[UpShift] clutch {clutch} up on {gear}')
    else:
        logger.debug(f'[UpShift] skip up shift. gear >= maxGear ({gear}, {forza.maxGear}) or gap < upShiftCoolDown ({cur - forza.last_upshift}, {upShiftCoolDown})')

def downShiftHandle(gear, forza):
    cur = time.time()
    if gear > forza.minGear and cur - forza.last_downshift >= downShiftCoolDown:
        logger.info(f'[DownShift] down shift fired. gear > minGear ({gear}, {forza.minGear}) or gap >= downShiftCoolDown ({cur - forza.last_downshift}, {downShiftCoolDown})')
        forza.last_downshift = cur

        if forza.clutch:
            # press and hold clutch, then delay
            keyboard_helper.pressdown_str(clutch)
            logger.debug(f'[DownShift] clutch {clutch} down on {gear}')

            # blip throttle
            forza.threadPool.submit(blipThrottle)

        time.sleep(delayClutchtoShift)
        # down shift and delay
        keyboard_helper.press_str(downshift)
        logger.debug(f'[DownShift] downshift {upshift} down and up on {gear}')

        time.sleep(delayShifttoClutch)
        if forza.clutch:
            # release clutch
            keyboard_helper.pressup_str(clutch)
            logger.debug(f'[DownShift] clutch {clutch} up on {gear}')
    else:
        logger.debug(f'[DownShift] skip down shift. gear <= minGear ({gear}, {forza.minGear}) or gap < downShiftCoolDown ({cur - forza.last_downshift}, {downShiftCoolDown})')
