from classroom.Classroom import Classroom


class Lesson:

    def __init__(self, course: str, subject: str, shift: str, gang: str, number_of_enrolled_students: int,
                 week_day: str, start: str, end: str, day: str, requested_characteristics: str):

        self.course = course
        self.subject = subject
        self.shift = shift
        self.gang = gang
        self.number_of_enrolled_students = number_of_enrolled_students
        self.week_day = week_day
        self.start = start
        self.end = end
        self.day = day
        self.requested_characteristics = requested_characteristics
        # self.classroom = Classroom('Edifício Sedas Nunes (ISCTE-IUL)', 'Auditório 4', 250, 125, ["cenas", "mais cenas"])


    def get_requested_characteristics(self) -> list:
        '''
        Returns classroom characteristics requested by the lesson
        :return:
        '''
        return self.requested_characteristics

    def get_number_of_enrolled_students(self) -> int:
        '''
        Returns number of enrolled students in the lesson
        :return:
        '''
        return self.number_of_enrolled_students

    def get_row(self) -> list:
        """
        Returns a list of strings with the correct order and informations to use on the export function in the Manipulate_Documents class.
        :return:
        """
        return [self.course, self.subject, self.shift, self.gang, str(self.number_of_enrolled_students),
                self.week_day, self.start, self.end, self.day, self.requested_characteristics]

    def generate_time_blocks(self) -> list:  # Retorna lista de blocos de tempo da aula numa lista de strings
        """
        Returns a list of strings with the following format: "10/16/2015_09:30:00-10:00:00", one for every 30 minutes that is inside the time interval of the lesson.
        :return:
        """
        if self.day == "" or self.start == "" or self.end == "":
            return []
        start_split = self.start.split(":")
        start_hour = int(start_split[0])
        start_minute = int(start_split[1])
        end_split = self.end.split(":")
        end_hour = int(end_split[0])
        end_minute = int(end_split[1])

        cur_hour = int(start_hour)
        cur_minute = int(start_minute)
        next_hour = None
        next_minute = None

        time_blocks = []
        while cur_hour < end_hour or (cur_hour == end_hour and cur_minute < end_minute):
            if cur_minute == 0:
                next_hour = cur_hour
                next_minute = 30
            else:
                next_hour = cur_hour + 1
                next_minute = 0

            time_blocks.append(self.datetime_to_string(self.day,
                                                       self.time_to_string(cur_hour) + ":" + self.time_to_string(
                                                           cur_minute) + ":00",
                                                       self.time_to_string(next_hour) + ":" + self.time_to_string(
                                                           next_minute) + ":00"))

            cur_hour = next_hour
            cur_minute = next_minute

        return time_blocks

    def time_to_string(self, time: int) -> str:
        """
        Takes a number that represents either hours or minutes and turns it into a string. If it's a single digit, it puts a 0 in the beginning.
        :param time:
        :return:
        """
        if not isinstance(time, int): return ""
        if time < 0: return ""
        return str(time) if time > 9 else "0" + str(time)

    # "10/16/2015_09:30:00-10:00:00"
    def datetime_to_string(self, date: str, start: str, end: str) -> str:
        """
        Takes a string with the date, the beginning and finishing hour of this lesson and turns it into a string with this format: "10/16/2015_09:30:00-10:00:00"
        :param day:
        :param start:
        :param end:
        :return:
        """
        if not isinstance(date, str) or not isinstance(start, str) or not isinstance(end, str): return ""
        return date + "_" + start + "-" + end

    def string_to_datetime(self, block: str) -> (str, str, str):
        """
        Takes a string with this format: "10/16/2015_09:30:00-10:00:00" and returns in string format the date and the beginning and finishing hour
        :param block:
        :return:
        """
        if not isinstance(block, str): return ("", "", "")
        if "_" not in block or "-" not in block: return ("", "", "")
        if block.find("_") > block.find("-"): return ("", "", "")

        split = block.split("_")
        time_split = split[1].split("-")

        return (split[0], time_split[0], time_split[1])

    def __str__(self):
        return "(" + self.subject + " | " + self.day + " | " + self.start + "-" + self.end + ")"

    def __repr__(self):
        return str(self)
