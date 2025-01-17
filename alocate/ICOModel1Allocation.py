import math
import time

from jmetal.algorithm.multiobjective.moead import MOEAD
from jmetal.algorithm.multiobjective import NSGAII
from jmetal.algorithm.multiobjective.nsgaiii import NSGAIII, UniformReferenceDirectionFactory
from jmetal.core.solution import BinarySolution
from jmetal.operator import SPXCrossover, BitFlipMutation, DifferentialEvolutionCrossover, NullCrossover
from jmetal.util.aggregative_function import Tschebycheff, WeightedSum
from jmetal.util.evaluator import SparkEvaluator
from jmetal.util.observer import ProgressBarObserver
from jmetal.util.solution import get_non_dominated_solutions
from jmetal.util.termination_criterion import StoppingByEvaluations

from alocate.Model1Handler import bool_list_to_timeslot, bool_list_to_int
from alocate.Progress import Progress
from file_manager.Manipulate_Documents import Manipulate_Documents
from jmetalpy.ICOMutation import ICOMutation
from jmetalpy.Model1Problem import Model1Problem, Model1Handler
from metrics.Metric import *


def ico_model1_allocation(lessons: list, classrooms: list, gangs: dict, metrics: list, progress: Progress = None):

    values = {}
    for lesson in lessons:
        if lesson.week in values.keys():
            values[lesson.week] += 1
        else:
            values[lesson.week] = 1

    busiest_week = max(values, key=values.get)
    busiest_week_lessons = list(filter(lambda l: l.week == busiest_week, lessons))
    #busiest_week_lessons = lessons.filter(lambda lesson: lesson.week == busiest_week)

    print(f"busiest week: {busiest_week}")

    problem = Model1Problem(busiest_week_lessons, classrooms, gangs, len(busiest_week), metrics)

    #algorithm = MOEAD(problem=problem,
    #                 population_size=300,
    #                 crossover=SPXCrossover(probability=1.0 / problem.number_of_variables),
    #                 mutation=BitFlipMutation(probability=1.0 / problem.number_of_variables),
    #                 aggregative_function=WeightedSum(),
    #                 neighbor_size=20,
    #                 neighbourhood_selection_probability=0.9,
    #                 max_number_of_replaced_solutions=2,
    #                 weight_files_path='resources/MOEAD_weights',
    #                 termination_criterion=StoppingByEvaluations(50)
    #                 )

    algorithm = NSGAII(
                    problem=problem,
                    population_size=100,
                    offspring_population_size=100,
                    mutation=BitFlipMutation(probability=1.0 / problem.number_of_variables),  # (probability=1.0 / problem.number_of_variables),
                    crossover=SPXCrossover(probability=1.0 / problem.number_of_variables),
                    termination_criterion=StoppingByEvaluations(max_evaluations=200)
                )

    #progress_bar = ProgressBarObserver(max=25000)
    #algorithm.observable.register(progress_bar)
    start = time.time()

    print("gonna run")
    algorithm.run()
    elapsed_time = time.time() - start

    print("Elapsed time: ", elapsed_time)

    solutions = algorithm.get_result()
    front = get_non_dominated_solutions(solutions)

    print(front)

    num_slots = len(busiest_week)*35*5
    one_solution = front[int(len(front)/2)]

    m1h = Model1Handler(lessons, classrooms, gangs, num_slots, one_solution, busiest_week)

    for week_num in range(len(busiest_week)):
        pass


def ico_model1_allocation_whole_schedule(lessons: list, classrooms: list, gangs: dict, metrics: list, progress: Progress = None):


    #values = set()
    #for lesson in lessons:
    #    values.add(lesson.week)

    # num_slots = len(values)*160 # TODO TEMPORÁRIO
    num_slots = 160
    num_bits_classroom = int(math.log(len(classrooms), 2) + 1)

    problem = Model1Problem(lessons, classrooms, gangs, num_slots, metrics)

    # algorithm = MOEAD(
    #     problem=problem,
    #     population_size=300,
    #     crossover=SPXCrossover(probability=0.8),
    #     mutation=ICOMutation(probability=1 / len(lessons),
    #                          classrooms_length=len(classrooms),
    #                          num_bits_classroom=num_bits_classroom,
    #                          num_slots=num_slots),
    #     aggregative_function=Tschebycheff(dimension=problem.number_of_objectives),
    #     neighbor_size=20,
    #     neighbourhood_selection_probability=0.9,
    #     max_number_of_replaced_solutions=2,
    #     weight_files_path='resources/MOEAD_weights',
    #     termination_criterion=StoppingByEvaluations(max_evaluations=100)
    # )

    algorithm = NSGAII(
                    problem=problem,
                    population_size=100,
                    offspring_population_size=100,
                    #mutation=BitFlipMutation(0.1),
                    mutation=ICOMutation(probability=1/len(lessons),
                                         classrooms_length=len(classrooms),
                                         num_bits_classroom=num_bits_classroom,
                                         num_slots=num_slots),
                    crossover=SPXCrossover(probability=0.8),
                    termination_criterion=StoppingByEvaluations(max_evaluations=200)
                )
    # algorithm = NSGAIII(
    #                 problem=problem,
    #                 population_size=100,
    #                 #mutation=BitFlipMutation(0.1),
    #                 mutation=ICOMutation(probability=1/len(lessons),
    #                                      classrooms_length=len(classrooms),
    #                                      num_bits_classroom=num_bits_classroom,
    #                                      num_slots=num_slots),
    #                 crossover=SPXCrossover(probability=0.8),
    #                 reference_directions=UniformReferenceDirectionFactory(problem.number_of_objectives, n_points=99),
    #                 termination_criterion=StoppingByEvaluations(max_evaluations=5000),
    #                 population_evaluator=SparkEvaluator(processes=12)
    #             )



    progress_bar = ProgressBarObserver(max=10)
    algorithm.observable.register(progress_bar)

    print("gonna run")
    start = time.time()
    algorithm.run()
    elapsed_time = time.time() - start
    print("Elapsed time: ", elapsed_time)

    solutions = algorithm.get_result()
    front = get_non_dominated_solutions(solutions)

    print(f"length do front: {len(front)}")

    one_solution = front[int(len(front)/2)]
    print(one_solution.objectives)
    for solution in front:
        print("")
        print("Objectives:")
        for i in range(len(solution.objectives)):
            print(f"{metrics[i].name}- {solution.objectives[i]}")


    return front
    #return make_lessons30(one_solution, lessons, classrooms), one_solution


def make_lessons30(solution1: BinarySolution, lessons1, classrooms1):
    lessons30 = {}
    num_bits_classroom = int(math.log(len(classrooms1), 2) + 1)
    for i, lesson in enumerate(lessons1):
        timeslot = bool_list_to_timeslot(solution1.variables[i][num_bits_classroom:])
        if timeslot not in lessons30:
            if bool_list_to_int(solution1.variables[i][:num_bits_classroom]) < len(classrooms1):
                lessons30[timeslot] = [(lesson,
                                        classrooms1[bool_list_to_int(solution1.variables[i][:num_bits_classroom])])]
            else:
                lessons30[timeslot] = [(lesson, None)]
        else:
            if bool_list_to_int(solution1.variables[i][:num_bits_classroom]) < len(classrooms1):
                lessons30[timeslot].append(
                    (lesson, classrooms1[bool_list_to_int(solution1.variables[i][:num_bits_classroom])])
                )
            else:
                lessons30[timeslot].append((lesson, None))

    return lessons30


if __name__ == '__main__':
    md = Manipulate_Documents(1)
    headers = ["Degree", "Subject", "Shift", "Grade", "Enrolled", "Day_Week", "Starts", "Ends", "Day", "Requested_Char",
               "Classroom", "Capacity", "Actual_Char"]

    s_headers = ["Course", "Subject", "Shift", "Class", "Enrolled", "Week", "Duration",
                 "Requested_Char", "Classroom", "Capacity", "Actual_Char"]
    order = [0, 1, 2, 3, 4, 5, 6, 7]

    lessons2, gangs2 = md.import_lessons_and_gangs2("../input_documents/Exemplo_de_horario_primeiro_semestre_ICO.csv",
                                                    order, ["MM", "DD", "YYYY"])
    classrooms2 = md.import_classrooms2()

    metrics2 = [LessonInconsistency()]

    # RoomlessLessons(), Overbooking(), Underbooking(), BadClassroom(), Gaps(), RoomMovements(), BuildingMovements(),
    # ClassroomInconsistency(), ClassroomCollisions(), GangLessonVolume(), GangLessonDistribution(),
    # LessonInconsistency()
    ico_model1_allocation_whole_schedule(lessons2, classrooms2, gangs2, metrics2, 2015)

