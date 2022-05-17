import copy
import random
from typing import List

from jmetal.core.operator import Crossover
from jmetalpy import TimeSlotSolution


class TimeSlotCrossover(Crossover[TimeSlotSolution, TimeSlotSolution]):
    def __init__(self, probability: float):
        super(TimeSlotCrossover, self).__init__(probability=probability)

    def execute(self, parents: List[TimeSlotSolution]) -> List[TimeSlotSolution]:
        if len(parents) != 2:
            raise Exception('The number of parents is not two: {}'.format(len(parents)))

        offspring = [copy.deepcopy(parents[0]), copy.deepcopy(parents[1])]

        rand = random.random()
        if rand <= self.probability:
            crossover_point = random.randrange(0, parents[0].number_of_variables)

            for i in range(crossover_point, parents[0].number_of_variables):
                offspring[0].variables[i] = copy.deepcopy(parents[1].variables[i])
                offspring[1].variables[i] = copy.deepcopy(parents[0].variables[i])

        return offspring

    def get_number_of_parents(self) -> int:
        return 2

    def get_number_of_children(self) -> int:
        return 2

    def get_name(self):
        return 'TimeSlot crossover'
