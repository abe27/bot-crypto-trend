class TimeFrame:
    def __init__(self):
         # initialize timeframe
        self.INTERVAL_1_MINUTE = "1m"
        self.INTERVAL_5_MINUTES = "5m"
        self.INTERVAL_15_MINUTES = "15m"
        self.INTERVAL_30_MINUTES = "30m"
        self.INTERVAL_1_HOUR = "1h"
        self.INTERVAL_2_HOURS = "2h"
        self.INTERVAL_4_HOURS = "4h"
        self.INTERVAL_1_DAY = "1d"
        self.INTERVAL_1_WEEK = "1W"
        self.INTERVAL_1_MONTH = "1M"
        
    def timeframe(self):
        return [
            # self.INTERVAL_1_MINUTE,
            # self.INTERVAL_5_MINUTES,
            # self.INTERVAL_15_MINUTES,
            # self.INTERVAL_30_MINUTES,
            self.INTERVAL_1_HOUR,
            self.INTERVAL_2_HOURS,
            # self.INTERVAL_4_HOURS,
            # self.INTERVAL_1_DAY,
            # self.INTERVAL_1_WEEK,
            # self.INTERVAL_1_MONTH,
        ]