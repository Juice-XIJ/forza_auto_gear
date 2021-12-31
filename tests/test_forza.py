import os
import sys

sys.path.append(r'.')

from concurrent.futures import ThreadPoolExecutor

import constants
import forza
import helper

threadPool = ThreadPoolExecutor(max_workers=8, thread_name_prefix="exec")
forza5 = forza.Forza(threadPool, packet_format=constants.packet_format, enable_clutch=constants.enable_clutch)


def test_analysis():
    helper.load_config(forza5, os.path.join(constants.root_path, 'example', f'{constants.example_car_ordinal}.json'))
    forza5.analyze(performance_profile=False, is_gui=False)

    # gear 1 => ( ] => torque is larger than 0 at the beginning, but has negative values at the end
    assert forza5.rpm_torque_map[1]['min_rpm_index'] == 0
    assert forza5.rpm_torque_map[1]['max_rpm_index'] == 141

    # gear 2 => ( ) => torque is larger than 0 all the time during the gear 2
    assert forza5.rpm_torque_map[2]['min_rpm_index'] == 0
    assert forza5.rpm_torque_map[2]['max_rpm_index'] == 143

    # gear 3 => [ ) => torque is less than 0 at the beginning but larger than 0 at the end
    assert forza5.rpm_torque_map[3]['min_rpm_index'] == 9
    assert forza5.rpm_torque_map[3]['max_rpm_index'] == 269

    # gear 4 => [ ] => torque is less than 0 at the beginning and the end
    assert forza5.rpm_torque_map[4]['min_rpm_index'] == 9
    assert forza5.rpm_torque_map[4]['max_rpm_index'] == 424

    # gear 5. Last => last gear
    assert forza5.rpm_torque_map[5]['min_rpm_index'] == 9
    assert forza5.rpm_torque_map[5]['max_rpm_index'] == 594
