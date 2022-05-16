from typing import List

from jmetal.core.operator import Crossover
from jmetalpy import TimeSlotSolution


class TimeSlotCrossover(Crossover[TimeSlotSolution, TimeSlotSolution]):
    def __init__(self, probability: float):
        super(TimeSlotCrossover, self).__init__(probability=probability)

    def execute(self, parents: List[TimeSlotSolution]) -> List[TimeSlotSolution]:
        pass

    def get_number_of_parents(self) -> int:
        return 2

    def get_number_of_children(self) -> int:
        return 2

    def get_name(self):
        return 'TimeSlot crossover'