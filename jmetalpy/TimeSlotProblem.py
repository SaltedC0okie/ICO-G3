import random
import datetime
from abc import ABC
from typing import List

from jmetal.core.problem import BinaryProblem, Problem
from jmetal.core.solution import BinarySolution

from jmetalpy.TimeSlotSolution import TimeSlotSolution
from metrics.Metric import TimeSlotHandler
from timeslot.TimeSlot import TimeSlot


class TimeSlotProblem(Problem):

    def __init__(self, lessons: list, classrooms: list, gangs: dict, metrics: list, week: int, year: int):
        super(TimeSlotProblem, self).__init__()

        super().__init__()
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
        self.number_of_variables = max(len(self.lessons), len(self.classrooms))

        self.obj_directions = [m.objective for m in metrics]

    def evaluate(self, solution: TimeSlotSolution):
        handler = TimeSlotHandler(solution.variables)

        for i, metric in enumerate(self.metrics):
            metric.calculate(handler)
            solution.objectives[i] = metric.get_percentage()
            metric.reset_metric()

        return solution

    def create_solution(self) -> BinarySolution:
        new_solution = TimeSlotSolution(self.lessons,
                                        self.classrooms,
                                        self.number_of_variables,
                                        self.number_of_objectives)

        new_solution.variables = []
        if len(self.lessons) < len(self.classrooms):
            for i in range(len(self.lessons)):
                minute = 0
                if random.random() < 0.5:
                    minute=30
                timeslot = TimeSlot(minute, hour, self.init_day + random.randint(0, 4), self.init_month, self.init_year)
                new_solution.variables.append((self.lessons[i], self.classrooms[random.randint(0, len(self.classrooms))], timeslot))

        else:
            pass

        lessons_index = random.shuffle(range(len(self.lessons)))
        for i in range(self.number_of_variables):
            # TODO



            bitset = [True if random.random() < 0.5 else False for b in range(len(self.classrooms))]
            bitset.extend([True if random.random() < 0.5 else False for b in range(self.num_slots)])
            new_solution.variables.append()
        return new_solution

    def get_name(self) -> str:
        return "permutation timeslot"
