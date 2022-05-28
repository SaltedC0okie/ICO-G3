class TimeSlot:
    def __init__(self, day: int, month: int, year: int, hour: int, minute: int):
        self.day = day
        self.month = month
        self.year = year
        self.hour = hour
        self.minute = minute

    def __str__(self):
        minute = str(self.minute) if self.minute >= 10 else f"0{self.minute}"
        return f"Day {self.day}, month {self.month}, year {self.year}, {self.hour}h{minute}"
