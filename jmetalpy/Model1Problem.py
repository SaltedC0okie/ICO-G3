import random
import datetime
import math

from jmetal.core.problem import BinaryProblem
from jmetal.core.solution import BinarySolution

from alocate.Model1Handler import Model1Handler, bool_list_to_int


class Model1Problem(BinaryProblem):

    def __init__(self, lessons: list, classrooms: list, gangs: dict, num_slots: int, metrics: list):
        super(BinaryProblem, self).__init__()

        self.lessons = lessons
        self.classrooms = classrooms
        self.gangs = gangs
        self.metrics = metrics

        # d = f"{year}-W{week}"
        # starting_date = datetime.datetime.strptime(d + '-1', "%Y-W%W-%w")

        # self.init_day = starting_date.day
        # self.init_month = starting_date.month
        # self.init_year = year

        self.number_of_objectives = len(self.metrics)
        self.number_of_variables = len(self.lessons)
        self.number_of_constraints = len(self.lessons)

        self.obj_directions = [m.objective for m in metrics]  # metrics[0].objective
        # self.obj_labels = ['Lower_half']

        self.num_slots = num_slots
        self.num_bits_classroom = int(math.log(len(self.classrooms), 2) + 1)
        self.num_bits_slots = int(math.log(self.num_slots, 2) + 1)

        self.obj_directions = [self.MINIMIZE for i in range(len(metrics))]
        self.obj_labels = ['Sum', 'No. of Objects']

    def evaluate(self, solution: BinarySolution):
        handle_everything = Model1Handler(self.lessons,
                                          self.classrooms,
                                          self.gangs,
                                          self.num_slots,
                                          solution
                                          ).handle_gangs_everything()
        for i, metric in enumerate(self.metrics):
            # for j in created_schedule:
            #    metric.calculate(j[0], j[1])
            metric.calculate(handle_everything)
            solution.objectives[i] = metric.get_total_metric_value()
            metric.reset_metric()

        self.__evaluate_constraints(solution)

        return solution

    def __evaluate_constraints(self, solution: BinarySolution) -> None:
        passed_assignments = set()
        for i, assignment in enumerate(solution.variables):
            a_num = bool_list_to_int(assignment)
            if a_num in passed_assignments:
                solution.constraints[i] = -1
                continue

            if len(self.classrooms) <= bool_list_to_int(assignment[:self.num_bits_classroom]) or \
                    self.num_slots <= bool_list_to_int(assignment[self.num_bits_classroom:]):
                solution.constraints[i] = -1
                continue

            passed_assignments.add(a_num)
            solution.constraints[i] = 1

    def create_solution(self) -> BinarySolution:
        new_solution = BinarySolution(self.number_of_variables,
                                      self.number_of_objectives,
                                      self.number_of_constraints)
        new_solution.variables = []
        for i in range(self.number_of_variables):
            bitset_classroom = [True if random.random() < 0.5 else False for b in range(self.num_bits_classroom)]
            while bool_list_to_int(bitset_classroom) >= len(self.classrooms):
                bitset_classroom = [True if random.random() < 0.5 else False for b in range(self.num_bits_classroom)]

            bitset_timeslot = [True if random.random() < 0.5 else False for b in range(self.num_bits_slots)]
            while bool_list_to_int(bitset_timeslot) >= self.num_slots:
                bitset_timeslot = [True if random.random() < 0.5 else False for b in range(self.num_bits_slots)]

            bitset_classroom.extend(bitset_timeslot)
            bitset = bitset_classroom
            new_solution.variables.append(bitset)
        return new_solution

    def get_name(self) -> str:
        return "permutation timetabling";
