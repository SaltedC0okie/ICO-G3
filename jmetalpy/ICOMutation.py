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
        self.classroom_slots = classroom_slots

    def execute(self, solution: BinarySolution) -> BinarySolution:
        Check.that(type(solution) is BinarySolution, "Solution type invalid")

        for i in range(solution.number_of_variables):
            for j in range(len(solution.variables[i])):
                rand = random.random()
                if rand <= self.probability:
                    solution.variables[i][j] = not solution.variables[i][j]

                    classroom_is_invalid = bool_list_to_int(solution.variables[i][:self.num_bits_classroom]) >= self.classrooms_length
                    timeslot_is_invalid = bool_list_to_int(solution.variables[i][self.num_bits_classroom:]) >= self.num_slots
                    # print(f"variables len: {len(solution.variables)}")
                    # print(f"classrooms len: {len(self.classrooms)}")
                    # print(f"solution classroom: {bool_list_to_int(solution.variables[i][:self.num_bits_classroom])}")
                    if classroom_is_invalid or timeslot_is_invalid or \
                        (self.classrooms[bool_list_to_int(solution.variables[i][:self.num_bits_classroom])],
                         bool_list_to_timeslot(solution.variables[i][self.num_bits_classroom:])) in self.classroom_slots:
                        # print(f"classroom_slots len: {len(self.classroom_slots)}")
                        solution.variables[i][j] = not solution.variables[i][j]

        return solution

    def get_name(self):
        return 'ICO mutation'