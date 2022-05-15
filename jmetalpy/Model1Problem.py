import random
import datetime
from abc import ABC
from typing import List

from jmetal.core.problem import BinaryProblem
from jmetal.core.solution import BinarySolution



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
            metric.calculate(self.lessons,
                  self.classrooms,
                  self.gangs,
                  self.init_day,
                  self.init_month,
                  self.init_year,
                  solution)
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
