import random
import datetime
from abc import ABC
from typing import List

from jmetal.core.problem import BinaryProblem
from jmetal.core.solution import BinarySolution

from Timeslot.TimeSlot import TimeSlot
from metrics.Metric import Handler


def bool_list_to_int(self, bool_list: List[bool]):
    num = 0
    for i in range(len(bool_list)):
        num += bool_list[-i - 1] * (2 ** i)
    return num


# slot = bool_list_to_slot(assignment[len(classrooms):], init_day, init_month, init_year)
def bool_list_to_timeslot(self, bool_list: List[bool], init_day: int, init_month: int, init_year: int):
    num = 0
    for i in range(len(bool_list)):
        num += bool_list[-i - 1] * (2 ** i)

    day_inc = int(num / 32)
    hour_inc = int(num % 32 / 2)
    half_hour_inc = int(hour_inc - int(hour_inc) + 0.5)

    date_1 = datetime.datetime.strptime(f"{init_month}/{init_day}/{init_year}", "%m/%d/%y")
    end_date = date_1 + datetime.timedelta(days=day_inc)

    slot = TimeSlot(end_date.day, end_date.month, end_date.year, 8 + hour_inc, 30 * half_hour_inc)

    return slot


class Model1Handler(Handler):

    def __init__(self, lessons: list, classrooms: list, gangs: dict, init_day: int, init_month: int,
                 init_year: int, solution: BinarySolution):
        self.lessons = lessons
        self.classrooms = classrooms
        self.gangs = gangs
        self.init_day = init_day
        self.init_month = init_month
        self.init_year = init_year
        self.solution = solution

    def handle_lesson_classroom(self) -> list:  # List[(Lesson, Classroom)]
        schedule = []

        for i, assignment in enumerate(self.solution.variables):
            classroom = self.classrooms[bool_list_to_int(assignment[:len(self.classrooms)])]
            lesson = self.lessons[i]

            schedule.append((lesson, classroom))

        return schedule

    def handle_gangs_lesson_slot(self) -> tuple:  # ( dict[String->Gang], dict[Lesson->TimeSlot] )
        lessons_slots = {}

        for i, assignment in enumerate(self.solution.variables):
            lesson = self.lessons[i]
            timeslot = bool_list_to_timeslot(assignment[len(self.classrooms):],
                                             self.init_day,
                                             self.init_month,
                                             self.init_year)

            lessons_slots[lesson] = timeslot

        return self.gangs, lessons_slots

    def handle_gangs_everything(self) -> tuple:  # ( dict[String->Gang], dict[Lesson->(TimeSlot, Classroom)] )
        lessons_slots = {}

        for i, assignment in enumerate(self.solution.variables):
            lesson = self.lessons[i]
            timeslot = bool_list_to_timeslot(assignment[len(self.classrooms):],
                                             self.init_day,
                                             self.init_month,
                                             self.init_year)
            classroom = self.classrooms[bool_list_to_int(assignment[:len(self.classrooms)])]

            lessons_slots[lesson] = (timeslot, classroom)

        return self.gangs, lessons_slots

    def handle_classroom_slot(self) -> list:  # List[(Classroom, TimeSlot)]
        classrooms_slots = []

        for i, assignment in enumerate(self.solution.variables):
            classroom = self.classrooms[bool_list_to_int(assignment[:len(self.classrooms)])]
            timeslot = bool_list_to_timeslot(assignment[len(self.classrooms):],
                                             self.init_day,
                                             self.init_month,
                                             self.init_year)

            classrooms_slots.append((classroom, timeslot))

        return classrooms_slots


class Model1Problem(BinaryProblem):

    def __init__(self, lessons: list, classrooms: list, gangs: dict, metrics: list, week: int, year: int):
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

    def evaluate(self, solution: BinaryProblem):

        for i, metric in enumerate(self.metrics):
            # for j in created_schedule:
            #    metric.calculate(j[0], j[1])
            metric.calculate(Model1Handler(self.lessons, self.classrooms, self.gangs,
                                           self.init_day, self.init_month, self.init_year, solution))
            solution.objectives[i] = metric.get_percentage()
            metric.reset_metric()

        return solution

    def __evaluate_constraints(self, solution: BinarySolution) -> None:
        pass  # TODO

    def create_solution(self) -> BinarySolution:
        new_solution = BinarySolution(self.number_of_variables,
                                      self.number_of_objectives)  # No clue about lower and upper
        new_solution.variables = []
        for i in range(self.number_of_variables):
            bitset = [True if random.random() < 0.5 else False for b in range(len(self.classrooms))]
            bitset.extend([True if random.random() < 0.5 else False for b in range(self.num_slots)])
            new_solution.variables.append(bitset)
        return new_solution

    def get_name(self) -> str:
        return "permutation timetabling";
