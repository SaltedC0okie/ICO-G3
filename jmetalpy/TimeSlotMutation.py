from jmetal.core.operator import Mutation

from Timeslot import TimeSlot
from jmetalpy import TimeSlotSolution


class TimeSlotMutation(Mutation[TimeSlot]):
    def __init__(self, probability: float):
        super(TimeSlotMutation, self).__init__(probability=probability)

    def execute(self, solution: TimeSlotSolution) -> TimeSlotSolution:
        pass

    def get_name(self):
        return 'TimeSlot mutation'
