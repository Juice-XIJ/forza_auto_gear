class CarInfo():
    def __init__(self):
        # === Pre-defined operation ===
        self.stop = 'f11' # stop program
        self.close = 'delete' # close program
        self.collect_data = 'f10'
        self.analysis = 'f8'
        self.auto_shift = 'f7'

        # === Car information ===
        self.ordinal = ''
        self.minGear = 1
        self.maxGear = 5
        
        self.gear_ratios = {}
        self.rpm_torque_map = {}
        self.shift_point = {}
        self.records = []

    def get_gear_raw_records(self, g):
        return [item for item in self.records if item['gear'] == g]