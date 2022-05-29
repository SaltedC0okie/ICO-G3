import math
import random

from jmetal.core.operator import Mutation
from jmetal.core.solution import BinarySolution
from jmetal.util.ckecking import Check

from alocate.Model1Handler import bool_list_to_int, bool_list_to_timeslot


class ICOMutation(Mutation[BinarySolution]):

    def __init__(self, probability: float, classrooms: list, num_slots: int, classroom_slots: set):
        super(ICOMutation, self).__init__(probability=probability)
        self.classrooms = classrooms
        self.classrooms_length = len(classrooms)
        self.num_bits_classroom = int(math.log(len(classrooms), 2) + 1)
        self.num_slots = num_slots

    def execute(self, solution: BinarySolution) -> BinarySolution:
        Check.that(type(solution) is BinarySolution, "Solution type invalid")

        for i in range(solution.number_of_variables):
            for j in range(len(solution.variables[i])):
                rand = random.random()
                if rand <= self.probability:
                    solution.variables[i][j] = not solution.variables[i][j]
                    if bool_list_to_int(solution.variables[i][:self.num_bits_classroom]) >= self.classrooms_length or \
                       bool_list_to_int(solution.variables[i][self.num_bits_classroom:]) >= self.num_slots or \
                        (self.classrooms[self.num_bits_classroom:], bool_list_to_timeslot(solution.variables[i][:self.num_bits_classroom])) not in self.classrooms_length:
                        solution.variables[i][j] = not solution.variables[i][j]

        return solution

    def get_name(self):
        return 'ICO mutation'