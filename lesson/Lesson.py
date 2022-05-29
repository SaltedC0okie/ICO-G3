from Gang.Gang import Gang
from classroom.Classroom import Classroom
import re


class Lesson:

    def __init__(self, dateformat_list: list, course: str, subject: str, shift: str, gangs: list, number_of_enrolled_students: int,
                 week: str, duration: str, requested_characteristics: str):
        self.course = course
        self.subject = subject
        self.shift = shift
        self.gang_list = gangs
        self.number_of_enrolled_students = number_of_enrolled_students
        self.week = week
        self.duration = duration
        self.requested_characteristics = requested_characteristics
        self.dateformat_list = dateformat_list
        self.assignment = None

    def get_requested_characteristics(self) -> str:
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
        return [self.course, self.subject, self.shift,  ",".join([g.name for g in self.gang_list]), str(self.number_of_enrolled_students),
                self.week, self.duration, self.requested_characteristics]

    #TODO
    def get_row_str(self) -> str:
        """
        Returns a list of strings with the correct order and informations to use on the export function in the Manipulate_Documents class.
        :return:
        """
        course = self.course if "," not in self.course else "\"" + self.course + "\""
        subject = self.subject if "," not in self.subject else "\"" + self.subject + "\""
        shift = self.shift if "," not in self.shift else "\"" + self.shift + "\""
        gang = self.gang if "," not in self.gang else "\"" + self.gang + "\""
        req_characs = self.requested_characteristics if "," not in self.requested_characteristics else "\"" + self.requested_characteristics + "\""

        return course + "," + subject + "," + shift + "," + gang + "," + str(self.number_of_enrolled_students) + "," + \
               self.week_day + "," + self.start + "," + self.end + "," + self.day + "," + req_characs

    def generate_time_blocks(self) -> list:  # Retorna lista de blocos de tempo da aula numa lista de strings
        """
        Returns a list of strings with the following format: "10/16/2015_09:30:00-10:00:00", one for every 30 minutes that is inside the time interval of the lesson.
        :return:
        """
        if self.day == "" or self.start == "" or self.end == "":
            return []

        start_split = re.split('\W+', self.start)
        start_hour = int(start_split[0])
        start_minute = int(start_split[1])
        end_split = re.split('\W+', self.end)
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
        :param date:
        :param day:
        :param start:
        :param end:
        :return:
        """
        month_index = self.dateformat_list.index('MM')
        day_index = self.dateformat_list.index('DD')
        year_index = self.dateformat_list.index('YYYY')
        date_split = re.split('\W+', date)
        date = date_split[month_index] + '/' + date_split[day_index] + '/' + date_split[year_index]
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

        return split[0], time_split[0], time_split[1]

    def has_assignment(self):
        return self.assignment is not None

    def __str__(self):
        return "<" + self.subject + " | " + str(
            self.number_of_enrolled_students) + " | " + str(self.number_of_enrolled_students) + ">"

    def __repr__(self):
        return str(self)
