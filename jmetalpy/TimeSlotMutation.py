import random

from jmetal.core.operator import Mutation

from timeslot import TimeSlot
from jmetalpy import TimeSlotSolution


def mutate(variables, solution):
    lesson, classroom, timeslot = variables

    # mutate time
    if random.random() <= 0.5:
        rand = random.random()
        if rand <= 1 / 3:
            timeslot.day = solution.init_day + random.randint(0, 4)
        elif rand <= 2 / 3:
            timeslot.hour = 8 + random.randint(16)
        else:
            timeslot.minute = 0
            if random.random() <= 0.5:
                timeslot.minute = 30

    # mutate classroom
    else:
        classroom = solution.classrooms[random.randint(0, len(solution.classrooms))]

    return lesson, classroom, timeslot


class TimeSlotMutation(Mutation[TimeSlot]):
    def __init__(self, probability: float):
        super(TimeSlotMutation, self).__init__(probability=probability)

    def execute(self, solution: TimeSlotSolution) -> TimeSlotSolution:
        for i in range(solution.number_of_variables):
            if random.random() <= self.probability:
                variables = solution.variables[i]
                solution.variables[i] = mutate(variables, solution)

        return solution

    def get_name(self):
        return 'TimeSlot mutation'
