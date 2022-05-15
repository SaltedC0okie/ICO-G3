import time

from jmetal.algorithm.multiobjective import MOEAD
from jmetal.operator import SPXCrossover, BitFlipMutation
from jmetal.util.aggregative_function import Tschebycheff, WeightedSum
from jmetal.util.solution import get_non_dominated_solutions
from jmetal.util.termination_criterion import StoppingByEvaluations

from alocate.Progress import Progress
from jmetalpy.Model1Problem import Model1Problem


def ico_model1_allocation(lessons: list, classrooms: list, gangs: dict, metrics: list, progress: Progress,
                          week: int, year: int):

    values = {}
    for lesson in lessons:
        if lesson.week in values.keys():
            values[lesson.week] += 1
        else:
            values[lesson.week] = 1

    busiest_week = max(values, key=values.get)
    busiest_week_lessons = lessons.filter(lambda lesson: lesson.week == busiest_week)

    problem = Model1Problem(busiest_week_lessons, classrooms, gangs, metrics, week, year)

    algorithm = MOEAD(problem=problem,
                     population_size=300,
                     crossover=SPXCrossover(probability=1.0 / problem.number_of_variables),
                     mutation=BitFlipMutation(probability=1.0 / problem.number_of_variables),
                     aggregative_function=WeightedSum(dimension=problem.number_of_objectives),
                     neighbor_size=20,
                     neighbourhood_selection_probability=0.9,
                     max_number_of_replaced_solutions=2,
                     weight_files_path='resources/MOEAD_weights',
                     termination_criterion=StoppingByEvaluations(max=100)
                     )

    start = time.time()
    algorithm.run()
    elapsed_time = time.time() - start

    # print("Elapsed time: ", elapsed_time)

    solutions = algorithm.get_result()
    front = get_non_dominated_solutions(solutions)

    print(front)






