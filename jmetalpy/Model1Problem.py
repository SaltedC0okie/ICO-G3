import random
import datetime
from abc import ABC
from typing import List

from jmetal.core.problem import BinaryProblem
from jmetal.core.solution import BinarySolution

from Timeslot.TimeSlot import TimeSlot
from metrics.Metric import Handler

import math


def bool_list_to_int(bool_list: List[bool]) -> int:
    num = 0
    for i in range(len(bool_list)):
        num += bool_list[-i - 1] * (2 ** i)
    return num


# slot = bool_list_to_slot(assignment[len(classrooms):], init_day, init_month, init_year)
def bool_list_to_timeslot(bool_list: List[bool], init_day: str, init_month: str, init_year: str):
    num = bool_list_to_int(bool_list)

    day_inc = int(num / 32)
    hour_inc = int(num % 32 / 2)
    half_hour_inc = int(num % 32 / 2 - hour_inc + 0.5)

    date_1 = datetime.datetime.strptime(f"{init_month}/{init_day}/{init_year}", "%m/%d/%Y")
    end_date = date_1 + datetime.timedelta(days=day_inc)

    slot = TimeSlot(end_date.day, end_date.month, end_date.year, 8 + hour_inc, 30 * half_hour_inc)

    return slot

def bool_list_to_timeslot(bool_list: List[bool]):
    num = bool_list_to_int(bool_list)

    week = int(num / 160)  # 5*32
    weekday = int(num/32) - week*5
    hour_inc = int(num % 32 / 2)
    half_hour_inc = int(num % 32 / 2 - hour_inc + 0.5)

    #date_1 = datetime.datetime.strptime(f"{init_month}/{init_day}/{init_year}", "%m/%d/%Y")
    #end_date = date_1 + datetime.timedelta(days=day_inc)

    slot = TimeSlot(week, weekday, 8 + hour_inc, 30 * half_hour_inc)

    return slot


class Model1Handler(Handler):

    def __init__(self, lessons: list, classrooms: list, gangs: dict, num_slots: int, solution: BinarySolution):
        self.lessons = lessons
        self.classrooms = classrooms
        self.gangs = gangs
        self.solution = solution
        self.num_bits_classroom = int(math.log(len(self.classrooms), 2) + 1)
        self.num_slots = num_slots

    def handle_lesson_classroom(self) -> list:  # List[(Lesson, Classroom)]
        schedule = []

        for i, assignment in enumerate(self.solution.variables):
            print(len(self.classrooms))
            print(assignment)
            print(len(assignment))
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
                timeslot = bool_list_to_timeslot(assignment[self.num_bits_classroom:])
            else:
                timeslot = None

            lessons_slots[lesson] = timeslot

        return self.gangs, lessons_slots

    def handle_gangs_everything(self) -> tuple:  # ( dict[String->Gang], dict[Lesson->(TimeSlot, Classroom)] )
        lessons_slots = {}

        for i, assignment in enumerate(self.solution.variables):
            lesson = self.lessons[i]
            if self.num_slots <= bool_list_to_int(assignment[self.num_bits_classroom:]):
                timeslot = bool_list_to_timeslot(assignment[self.num_bits_classroom:])
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
                timeslot = bool_list_to_timeslot(assignment[self.num_bits_classroom:])
            else:
                timeslot = None

            classrooms_slots.append((classroom, timeslot))

        return classrooms_slots


class Model1Problem(BinaryProblem):

    def __init__(self, lessons: list, classrooms: list, gangs: dict, num_slots: int, metrics: list, week: int, year: int):
        super(BinaryProblem, self).__init__()

        self.lessons = lessons
        self.classrooms = classrooms
        self.gangs = gangs
        self.metrics = metrics

        d = f"{year}-W{week}"
        starting_date = datetime.datetime.strptime(d + '-1', "%Y-W%W-%w")

        self.init_day = starting_date.day
        self.init_month = starting_date.month
        self.init_year = year

        self.number_of_objectives = len(self.metrics)
        self.number_of_variables = len(self.lessons)
        self.number_of_constraints = len(self.lessons)

        self.obj_directions = [m.objective for m in metrics]  # metrics[0].objective
        # self.obj_labels = ['Lower_half']

        self.num_slots = num_slots
        self.num_bits_classroom = int(math.log(len(self.classrooms), 2) + 1)
        self.num_bits_slots = int(math.log(self.num_slots, 2) + 1)

    def evaluate(self, solution: BinaryProblem):
        print("ai")
        for i, metric in enumerate(self.metrics):
            # for j in created_schedule:
            #    metric.calculate(j[0], j[1])
            metric.calculate(Model1Handler(self.lessons, self.classrooms, self.gangs, self.num_slots,
                                           self.init_day, self.init_month, self.init_year, solution))
            solution.objectives[i] = metric.get_percentage()
            metric.reset_metric()



        return solution

    def __evaluate_constraints(self, solution: BinarySolution) -> None:
        passed_assignments = {}
        for i, assignment in enumerate(solution.variables):
            if assignment in passed_assignments:
                solution.constraints[i] = -1
                continue

            if len(self.classrooms) <= bool_list_to_int(assignment[:self.num_bits_classroom]) or \
               self.num_slots <= bool_list_to_int(assignment[self.num_bits_classroom:]):
                solution.constraints[i] = -1
                continue

            solution.constraints[i] = 1



    def create_solution(self) -> BinarySolution:
        new_solution = BinarySolution(self.number_of_variables,
                                      self.number_of_objectives)  # No clue about lower and upper
        new_solution.variables = []
        for i in range(self.number_of_variables):
            bitset = [True if random.random() < 0.5 else False for b in range(self.num_bits_classroom)]
            bitset.extend([True if random.random() < 0.5 else False for b in range(self.num_bits_classroom)])
            new_solution.variables.append(bitset)
        return new_solution

    def get_name(self) -> str:
        return "permutation timetabling";
