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
from metrics.Metric import Overbooking, Underbooking, BadClassroom, RoomMovements, LessonCollisions


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


def addAssignment(gang_list_of_lessons, classrooms, solution):
    num_bits_classroom = int(math.log(len(classrooms), 2) + 1)

    for i, assignment in enumerate(solution.variables):
        lesson = gang_list_of_lessons[i]
        if num_slots > bool_list_to_int(assignment[num_bits_classroom:]):
            timeslot = bool_list_to_timeslot(assignment[num_bits_classroom:], lesson.week)
        else:
            timeslot = None

        if len(classrooms) > bool_list_to_int(assignment[:num_bits_classroom]):
            classroom = classrooms[bool_list_to_int(assignment[:num_bits_classroom])]
        else:
            classroom = None
        if not lesson.has_assignment():
            lesson.assignment = (classroom, timeslot)


# def repeat(g: Gang, alg_lessons: list, num_of_weeks: int):
#     done_lessons = {}
#     week = alg_lessons[0].week
#     for lesson in g.lessons:
#         exists = False
#         for alg_lesson in alg_lessons:
#             #if lessondone_lessons[] TODO
#             if alg_lesson.subject == lesson.subject and alg_lesson:
#                 pass
#
#         if not exists:
#             pass  # TODO Doesn't exist on busiest week, add naively

if __name__ == '__main__':
    md = Manipulate_Documents(1)
    order = [0, 1, 2, 3, 4, 5, 6, 7]
    lessons, gangs = md.import_lessons_and_gangs2("input_documents/Exemplo_de_horario_primeiro_semestre_ICO.csv",
                                                  order, ["MM", "DD", "YYYY"])
    classrooms = md.import_classrooms2("input_classrooms/Salas.csv")
    metrics = [LessonCollisions()]
    weeks = set()
    for lesson in lessons:
        weeks.add(lesson.week)
    num_of_weeks = len(weeks)
    num_slots = 30 * num_of_weeks  # 6 slots diários vezes 5 dias
    classroom_slots = set()

    # num_lessons_list = []
    # for name, gang in gangs.items():
    #     num_lessons_list.append(len(gang.lessons))
    #
    # max = max(num_lessons_list)
    # for name, gang in gangs.items():
    #     if len(gang.lessons) == max:
    #         aquilo = gang
    #         break
    gangs_passed = {}

    for name, gang in gangs.items():
        gangs_passed["GMKC1"] = gang

        # semana = filter_busiest_week(aquele_gang.lessons)
        # print(f"len(semana) = {len(semana)}")

        problem = Model1Problem(gang.lessons, classrooms, gangs, num_slots, metrics)
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
            termination_criterion=StoppingByEvaluations(max_evaluations=500),
        )
        print("gonna run")
        start = time.time()
        algorithm.run()
        elapsed_time = time.time() - start
        print("Elapsed time: ", elapsed_time)

        solutions = algorithm.get_result()
        front = get_non_dominated_solutions(solutions)

        print(f"length do front: {len(front)}")
        # sol = problem.create_solution()
        # front = [sol]

        metric_percents = []
        for solution in front:
            # TODO - ESCREVI TODO MAS JÁ ESTÁ FEITO
            addAssignment(gang.lessons, classrooms, solution)
            sol_metrics = []
            handler = Model1Handler(gang.lessons, classrooms, gangs, num_slots, solution)
            tuple_dicts = handler.handle_gangs_everything()
            for metric in metrics:
                metric.reset_metric()
                metric.calculate(tuple_dicts)
                sol_metrics.append(metric.get_percentage())
            metric_percents.append(sol_metrics)

        for percents in metric_percents:
            print("")
            print("Objectives:")
            for i in range(len(percents)):
                print(f"{metrics[i].name}- {percents[i]}")

    # one_solution = front[int(len(front)/2)]
    # print(one_solution.objectives)
    # for solution in front:
    #     print("")
    #     print("Objectives:")
    #     for i in range(len(solution.objectives)):
    #         print(f"{metrics[i].name}- {solution.objectives[i]}")
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
