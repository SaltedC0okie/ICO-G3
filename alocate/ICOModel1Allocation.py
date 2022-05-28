import time

from jmetal.algorithm.multiobjective import MOEAD
from jmetal.operator import SPXCrossover, BitFlipMutation
from jmetal.util.aggregative_function import Tschebycheff, WeightedSum
from jmetal.util.observer import ProgressBarObserver
from jmetal.util.solution import get_non_dominated_solutions
from jmetal.util.termination_criterion import StoppingByEvaluations

from alocate.Progress import Progress
from file_manager.Manipulate_Documents import Manipulate_Documents
from jmetalpy.Model1Problem import Model1Problem
from metrics.Metric import *


def ico_model1_allocation(lessons: list, classrooms: list, gangs: dict, metrics: list, year: int, progress: Progress = None):

    values = {}
    for lesson in lessons:
        if lesson.week in values.keys():
            values[lesson.week] += 1
        else:
            values[lesson.week] = 1

    busiest_week = max(values, key=values.get)
    busiest_week_lessons = lessons.filter(lambda lesson: lesson.week == busiest_week)

    print(f"busiest week: {busiest_week}")

    problem = Model1Problem(busiest_week_lessons, classrooms, gangs, metrics, year)

    algorithm = MOEAD(problem=problem,
                     population_size=300,
                     crossover=SPXCrossover(probability=1.0 / problem.number_of_variables),
                     mutation=BitFlipMutation(probability=1.0 / problem.number_of_variables),
                     aggregative_function=WeightedSum(dimension=problem.number_of_objectives),
                     neighbor_size=20,
                     neighbourhood_selection_probability=0.9,
                     max_number_of_replaced_solutions=2,
                     weight_files_path='resources/MOEAD_weights',
                     termination_criterion=StoppingByEvaluations(max=50)
                     )

    progress_bar = ProgressBarObserver(max=25000)
    algorithm.observable.register(progress_bar)
    start = time.time()

    print("gonna run")
    algorithm.run()
    elapsed_time = time.time() - start

    print("Elapsed time: ", elapsed_time)

    solutions = algorithm.get_result()
    front = get_non_dominated_solutions(solutions)

    print(front)


if __name__ == '__main__':
    md = Manipulate_Documents()
    headers = ["Degree", "Subject", "Shift", "Grade", "Enrolled", "Day_Week", "Starts", "Ends", "Day", "Requested_Char",
               "Classroom", "Capacity", "Actual_Char"]

    s_headers = ["Course", "Subject", "Shift", "Class", "Enrolled", "Week", "Duration",
                 "Requested_Char", "Classroom", "Capacity", "Actual_Char"]
    order = []
    for i in range(len(s_headers)):
        order.append(i)

    lessons, gangs = md.import_lessons_and_gangs2("E:/E_Documents/Git/ICO-G3/input_documents/Exemplo_de_horario_primeiro_semestre_ICO.csv",
                                                  order, ["MM", "DD", "YYYY"])
    classrooms = md.import_classrooms2()

    metrics = [RoomlessLessons(), Overbooking(), BadClassroom(), Gaps(), RoomMovements(), ClassroomInconsistency(),
               ClassroomCollisions(), GangLessonVolume(), GangLessonDistribution(), LessonInconsistency()]

    ico_model1_allocation(lessons, classrooms, gangs, metrics, 2015)







