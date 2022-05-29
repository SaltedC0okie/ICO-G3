import time

from jmetal.algorithm.multiobjective import NSGAII
from jmetal.operator import SPXCrossover
from jmetal.util.evaluator import SparkEvaluator
from jmetal.util.solution import get_non_dominated_solutions
from jmetal.util.termination_criterion import StoppingByEvaluations

from alocate.Model1Handler import Model1Handler
from file_manager.Manipulate_Documents import Manipulate_Documents
import statistics

from jmetalpy.ICOMutation import ICOMutation
from jmetalpy.Model1Problem import Model1Problem
from metrics.Metric import Overbooking, Underbooking, BadClassroom, RoomMovements


def filter_drenz(gang_lessons: list):
    values = {}
    for lesson in gang_lessons:
        if lesson.week in values.keys():
            values[lesson.week] += 1
        else:
            values[lesson.week] = 1

    dict_distribution = sorted(values.items(), key=lambda item: item[1])
    dict_distribution = dict([(k, v) for k, v in dict_distribution])
    week, num = dict_distribution.popitem()

    #busiest_week = max(values, key=values.get)
    busiest_week_lessons = list(filter(lambda l: l.week == week, gang_lessons))

    return busiest_week_lessons

if __name__ == '__main__':
    md = Manipulate_Documents(1)
    order = [0, 1, 2, 3, 4, 5, 6, 7]
    lessons, gangs = md.import_lessons_and_gangs2("input_documents/Exemplo_de_horario_primeiro_semestre_ICO.csv",
                                                  order, ["MM", "DD", "YYYY"])
    classrooms = md.import_classrooms2("input_classrooms/Salas.csv")
    metrics = [Overbooking(), BadClassroom(), RoomMovements()]
    num_slots = 30  # 6 slots diários vezes 5 dias
    classroom_slots = set()

    num_lessons_list = []
    for name, gang in gangs.items():
        num_lessons_list.append(len(gang.lessons))

    max = max(num_lessons_list)
    for name, gang in gangs.items():
        if len(gang.lessons) == max:
            aquilo = gang
            break

    aquele_gang = aquilo
    gangs = {"GMKC1": aquele_gang}
    semana = filter_drenz(aquele_gang.lessons)
    print(f"len(semana) = {len(semana)}")

    problem = Model1Problem(semana, classrooms, gangs, num_slots, metrics)
    algorithm = NSGAII(
                        problem=problem,
                        population_size=100,
                        offspring_population_size=100,
                        #mutation=BitFlipMutation(0.1),
                        mutation=ICOMutation(probability=0.1,
                                             classrooms=classrooms,
                                             num_slots=num_slots,
                                             classroom_slots=classroom_slots),
                        crossover=SPXCrossover(probability=0.8),
                        termination_criterion=StoppingByEvaluations(max_evaluations=2000),
                    )
    print("gonna run")
    start = time.time()
    algorithm.run()
    elapsed_time = time.time() - start
    print("Elapsed time: ", elapsed_time)

    solutions = algorithm.get_result()
    front = get_non_dominated_solutions(solutions)

    print(f"length do front: {len(front)}")

    metric_percents = []
    for solution in front:
        sol_metrics = []
        handler = Model1Handler(semana, classrooms, gangs, num_slots, solution)
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
