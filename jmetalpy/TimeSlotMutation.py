from jmetal.core.operator import Mutation

from timeslot import TimeSlot
from jmetalpy import TimeSlotSolution


class TimeSlotMutation(Mutation[TimeSlot]):
    def __init__(self, probability: float):
        super(TimeSlotMutation, self).__init__(probability=probability)

    def execute(self, solution: TimeSlotSolution) -> TimeSlotSolution:
        for i in range(solution.number_of_variables):
                # TODO

    def get_name(self):
        return 'TimeSlot mutation'
