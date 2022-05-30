import math
import random
import time

from jmetal.algorithm.multiobjective import NSGAII
from jmetal.operator import SPXCrossover
from jmetal.util.evaluator import SparkEvaluator
from jmetal.util.solution import get_non_dominated_solutions
from jmetal.util.termination_criterion import StoppingByEvaluations

from Gang.Gang import Gang
from Timeslot.TimeSlot import TimeSlot
from alocate.Model1Handler import Model1Handler, bool_list_to_int, bool_list_to_timeslot
from file_manager.Manipulate_Documents import Manipulate_Documents
import statistics

from jmetalpy.ICOMutation import ICOMutation
from jmetalpy.Model1Problem import Model1Problem
from metrics.Metric import Overbooking, Underbooking, BadClassroom, RoomMovements, LessonCollisions, ClassroomCollisions


def filter_busiest_week(gang_lessons: list):
    values = {}
    for lesson in gang_lessons:
        if lesson.week in values.keys():
            values[lesson.week] += 1
        else:
            values[lesson.week] = 1

    # dict_distribution = sorted(values.items(), key=lambda item: item[1])
    # dict_distribution = dict([(k, v) for k, v in dict_distribution])
    # week, num = dict_distribution.popitem()

    # busiest_week = max(values, key=values.get)
    week = list(values.keys())[random.randint(0, len(values))]
    busiest_week_lessons = list(filter(lambda l: l.week == week, gang_lessons))

    return busiest_week_lessons

# def get_closest_solution(front: list):
#     sum_total = [sum(s.objectives)/len(s.objectives) for s in front]
#     index_min = min(range(len(sum_total)), key=sum_total.__getitem__)
#     return front[index_min]

def get_closest_solution(front: list):
    total_sums = []
    for sol in front:
        sums = []
        for i, objective in enumerate(sol.objectives):
            sums.append(sum([objective - sol.objectives[j] for j in range(i+1, len(sol.objectives))]))

        total_sums.append(sums)

    index_min = min(range(len(total_sums)), key=total_sums.__getitem__)
    return front[index_min]

def addAssignments(gang_list_of_lessons, classrooms, solution, num_slots):
    num_bits_classroom = int(math.log(len(classrooms), 2) + 1)

    for i, assignment in enumerate(solution.variables):
        lesson = gang_list_of_lessons[i]
        if num_slots > bool_list_to_int(assignment[num_bits_classroom:]):
            timeslot = bool_list_to_timeslot(assignment[num_bits_classroom:])
        else:
            timeslot = None

        if len(classrooms) > bool_list_to_int(assignment[:num_bits_classroom]):
            classroom = classrooms[bool_list_to_int(assignment[:num_bits_classroom])]
        else:
            classroom = None
        if not lesson.has_assignment():
            lesson.assignment = (classroom, timeslot)


def novo_algoritmo(lessons, gangs, classrooms, metrics):

    # Count number of weeks in semester
    weeks = set()
    for lesson in lessons:
        weeks.add(lesson.week)
    num_of_weeks = len(weeks)
    num_slots = 30 * num_of_weeks  # 6 slots diários vezes 5 dias

    # Initializing variables for the loop by course class
    classroom_slots = set()
    iter = 0
    len_gangs = len(gangs)
    for name, gang in gangs.items():
        iter += 1
        print(f"num: {iter} of {len_gangs}, New gang: ", gang.name)
        print(f"num_of_lessons={len(gang.lessons)}")

        # Make problem and run alg
        gangs_weird = {name: gang}
        problem = Model1Problem(gang.lessons, classrooms, gangs_weird, num_slots, metrics)

        algorithm = NSGAII(
            problem=problem,
            population_size=100,
            offspring_population_size=100,
            # mutation=BitFlipMutation(0.1),
            mutation=ICOMutation(probability=0.1,
                                 classrooms=classrooms,
                                 num_slots=num_slots,
                                 classroom_slots=classroom_slots),
            crossover=SPXCrossover(probability=0.8),
            termination_criterion=StoppingByEvaluations(max_evaluations=200)
        )
        # print("gonna run")
        start = time.time()
        algorithm.run()
        elapsed_time = time.time() - start
        # print("Elapsed time: ", elapsed_time)

        # Make front
        solutions = algorithm.get_result()
        front = get_non_dominated_solutions(solutions)
        # print(f"length do front: {len(front)}")

        # Get possible best solution (with no extremes)
        closest_solution = get_closest_solution(front)

        # Assign the solution classrooms and timeslots to the lessons of the gang
        addAssignments(gang.lessons, classrooms, closest_solution, num_slots)

        # Update used Classrooms on timeslot
        for lesson in gang.lessons:
            classroom_slots.add(lesson.assignment)

    ## Determine Mémétrics:
#
    ## Make dict with lesson, timeslot and classroom
    #lesson_timeslot_classroom_dict = {lesson: (lesson.assignment[1], lesson.assignment[0]) for lesson in lessons}
#
    ## Make tuple with both dicts
    #tuple_dicts = (gangs, lesson_timeslot_classroom_dict)
#
    ## Evaluate metrics for the entire algorithm
    #metric_percents = []
    #for metric in metrics:
    #    metric.reset_metric()
    #    metric.calculate(tuple_dicts)
    #    metric_percents.append(metric.get_percentage())

    """
    # Print the metrics
    print("")
    print("Objectives:")
    for i in range(len(metric_percents)):
        print(f"{metrics[i].name}- {metric_percents[i]}")
    """


    # for lesson, t in lesson_timeslot_classroom_dict.items():
    #     print(f"{lesson} -> ({t[0]}, {t[1]})")

# if __name__ == '__main__':
#     md = Manipulate_Documents(1)
#     order = [0, 1, 2, 3, 4, 5, 6, 7]
#     lessons, gangs = md.import_lessons_and_gangs2("input_documents/Exemplo_de_horario_primeiro_semestre_ICO.csv",
#                                                   order, ["MM", "DD", "YYYY"])
#     classrooms = md.import_classrooms2("input_classrooms/Salas.csv")
#     metrics = [LessonCollisions()]
#     weeks = set()
#     for lesson in lessons:
#         weeks.add(lesson.week)
#     num_of_weeks = len(weeks)
#     num_slots = 30*num_of_weeks  # 6 slots diários vezes 5 dias
#     classroom_slots = set()
#
#      num_lessons_list = []
#     for name, gang in gangs.items():
#          num_lessons_list.append(len(gang.lessons))
#
#      max = max(num_lessons_list)
#      for name, gang in gangs.items():
#          if len(gang.lessons) == max:
#              aquilo = gang
#              break
#
#
#
#         aquele_gang = aquilo
#         gangs = {"GMKC1": aquele_gang}
#         semana = filter_busiest_week(aquele_gang.lessons)
#         print(f"len(semana) = {len(semana)}")
#
#         problem = Model1Problem(aquele_gang.lessons, classrooms, gangs, num_slots, metrics)
#         algorithm = NSGAII(
#             problem=problem,
#             population_size=100,
#             offspring_population_size=100,
#             # mutation=BitFlipMutation(0.1),
#             mutation=ICOMutation(probability=0.1,
#                                  classrooms=classrooms,
#                                  num_slots=num_slots,
#                                  classroom_slots=classroom_slots),
#             crossover=SPXCrossover(probability=0.8),
#             termination_criterion=StoppingByEvaluations(max_evaluations=500),
#         )
#         print("gonna run")
#         start = time.time()
#         algorithm.run()
#         elapsed_time = time.time() - start
#         print("Elapsed time: ", elapsed_time)
#
#         solutions = algorithm.get_result()
#         front = get_non_dominated_solutions(solutions)
#
#         print(f"length do front: {len(front)}")
#         # sol = problem.create_solution()
#         # front = [sol]
#
#         metric_percents = []
#         for solution in front:
#             sol_metrics = []
#             handler = Model1Handler(aquele_gang.lessons, classrooms, gangs, num_slots, solution)
#             tuple_dicts = handler.handle_gangs_everything()
#             for metric in metrics:
#                 metric.reset_metric()
#                 metric.calculate(tuple_dicts)
#                 sol_metrics.append(metric.get_percentage())
#             metric_percents.append(sol_metrics)
#
#         for percents in metric_percents:
#             print("")
#             print("Objectives:")
#             for i in range(len(percents)):
#                 print(f"{metrics[i].name}- {percents[i]}")
#
#
#     # one_solution = front[int(len(front)/2)]
#     # print(one_solution.objectives)
#     # for solution in front:
#     #     print("")
#     #     print("Objectives:")
#     #     for i in range(len(solution.objectives)):
#     #         print(f"{metrics[i].name}- {solution.objectives[i]}")
