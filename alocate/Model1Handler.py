import math
from typing import List

from jmetal.core.solution import BinarySolution

from Timeslot.TimeSlot import TimeSlot
from metrics.Metric import Handler


def bool_list_to_int(bool_list: List[bool]) -> int:
    num = 0
    for i in range(len(bool_list)):
        num += bool_list[-i - 1] * (2 ** i)
    return num


def bool_list_to_timeslot(bool_list: List[bool], week: int = 0):
    num = bool_list_to_int(bool_list)
    hours = [(8, 00), (9, 30), (11, 0), (13, 0), (14, 30), (16, 0)]

    if week == 0:
        week = int(num / 30)  # 5*6
        weekday = int(num/6) - week*5
    else:
        weekday = int(num / 6)


    hour_inc, half_hour = hours[num % 6]

    #date_1 = datetime.datetime.strptime(f"{init_month}/{init_day}/{init_year}", "%m/%d/%Y")
    #end_date = date_1 + datetime.timedelta(days=day_inc)

    slot = TimeSlot(week, weekday, hour_inc, half_hour)

    return slot


class Model1Handler(Handler):

    def __init__(self, lessons: list, classrooms: list, gangs: dict, num_slots: int, solution: BinarySolution, week: int = 0):
        self.lessons = lessons
        self.classrooms = classrooms
        self.gangs = gangs
        self.week = week
        self.solution = solution
        self.num_bits_classroom = int(math.log(len(self.classrooms), 2) + 1)
        self.num_slots = num_slots

    def handle_lesson_classroom(self) -> list:  # List[(Lesson, Classroom)]
        schedule = []

        for i, assignment in enumerate(self.solution.variables):
            if len(self.classrooms) > bool_list_to_int(assignment[:self.num_bits_classroom]):
                classroom = self.classrooms[bool_list_to_int(assignment[:self.num_bits_classroom])]
            else:
                classroom = None
            lesson = self.lessons[i]

            schedule.append((lesson, classroom))

        return schedule

    def handle_gangs_lesson_slot(self) -> tuple:  # ( dict[String->Gang], dict[Lesson->TimeSlot] )
        lessons_slots = {}

        for i, assignment in enumerate(self.solution.variables):
            lesson = self.lessons[i]
            if self.num_slots <= bool_list_to_int(assignment[self.num_bits_classroom:]):
                timeslot = bool_list_to_timeslot(assignment[self.num_bits_classroom:], self.week)
            else:
                timeslot = None

            lessons_slots[lesson] = timeslot

        return self.gangs, lessons_slots

    def handle_gangs_everything(self) -> tuple:  # ( dict[String->Gang], dict[Lesson->(TimeSlot, Classroom)] )
        lessons_slots = {}

        for i, assignment in enumerate(self.solution.variables):
            lesson = self.lessons[i]
            if self.num_slots <= bool_list_to_int(assignment[self.num_bits_classroom:]):
                timeslot = bool_list_to_timeslot(assignment[self.num_bits_classroom:], self.week)
            else:
                timeslot = None

            if len(self.classrooms) > bool_list_to_int(assignment[:self.num_bits_classroom]):
                classroom = self.classrooms[bool_list_to_int(assignment[:self.num_bits_classroom])]
            else:
                classroom = None

            lessons_slots[lesson] = (timeslot, classroom)

        return self.gangs, lessons_slots

    def handle_classroom_slot(self) -> list:  # List[(Classroom, TimeSlot)]
        classrooms_slots = []

        for i, assignment in enumerate(self.solution.variables):
            if len(self.classrooms) > bool_list_to_int(assignment[:self.num_bits_classroom]):
                classroom = self.classrooms[bool_list_to_int(assignment[:self.num_bits_classroom])]
            else:
                classroom = None

            if self.num_slots <= bool_list_to_int(assignment[self.num_bits_classroom:]):
                timeslot = bool_list_to_timeslot(assignment[self.num_bits_classroom:], self.week)
            else:
                timeslot = None

            classrooms_slots.append((classroom, timeslot))

        return classrooms_slots
