from typing import List

from jmetal.core.solution import Solution

from timeslot import TimeSlot


class TimeSlotSolution(Solution[TimeSlot]):
    def __init__(
            self,
            lessons: list,
            classrooms: list,
            number_of_variables: int,
            number_of_objectives: int,
            number_of_constraints: int = 0
    ):
        super(TimeSlotSolution, self).__init__(number_of_variables, number_of_objectives, number_of_constraints)

        self.lessons = lessons
        self.classrooms = classrooms


    def __copy__(self):
        new_solution = TimeSlotSolution(
            self.number_of_variables, self.number_of_objectives, self.number_of_constraints
        )
        new_solution.objectives = self.objectives[:]
        new_solution.variables = self.variables[:]
        new_solution.constraints = self.constraints[:]

        new_solution.attributes = self.attributes.copy()

        return new_solution
