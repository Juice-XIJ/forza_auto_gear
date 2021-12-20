class CarInfo():
    def __init__(self):
        """initialization
        """
        # === Car information ===
        self.ordinal = ''
        self.minGear = 1
        self.maxGear = 5

        self.gear_ratios = {}
        self.rpm_torque_map = {}
        self.shift_point = {}
        self.records = []

    def get_gear_raw_records(self, g: int):
        """get raw records for gear

        Args:
            g (int): gear

        Returns:
            [list]: list of recrods for gear
        """
        return [item for item in self.records if item['gear'] == g]