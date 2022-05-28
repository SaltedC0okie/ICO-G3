class TimeSlot:
    def __init__(self, week: int, weekday: int, hour: int, minute: int):
        self.week = week
        self.weekday = weekday
        self.hour = hour
        self.minute = minute

    def __str__(self):
        minute = str(self.minute) if self.minute >= 10 else f"0{self.minute}"
        return f"Week {self.week}, weekday {self.weekday}, {self.hour}h{minute}"

        # self.day = day
        # self.month = month
        # self.year = year
        # self.hour = hour
        # self.minute = minute


