from jmetal.core.solution import Solution
from bitarray import bitarray
from typing import List

class TimeTablingSolution(Solution):
    """Class representing integer solutions"""

    def __init__(
        self, lower_bound: List[int], upper_bound: List[int], number_of_objectives: int, number_of_constraints: int = 0
    ):
        super(TimeTablingSolution, self).__init__(len(lower_bound), number_of_objectives, number_of_constraints)
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def __copy__(self):
        new_solution = TimeTablingSolution(
            self.lower_bound, self.upper_bound, self.number_of_objectives, self.number_of_constraints
        )
        new_solution.objectives = self.objectives[:]
        new_solution.variables = self.variables[:]
        new_solution.constraints = self.constraints[:]

        new_solution.attributes = self.attributes.copy()

        return new_solution


a = bitarray(10)
print(a)
print(a.any())
print(a.count())
print(a.reverse())
print(a.)
print(a)
