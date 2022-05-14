import copy
import time
from jmetal.core.solution import PermutationSolution

from classroom.Classroom import Classroom
from jmetalpy.JMP import JMP
from lesson.Lesson import Lesson


def sorted_lessons(schedule: list) -> list:
    '''
    Sort lessons by day, start time and number of enrolled students

    :return list[Lesson]:
    '''
    return sorted(schedule, key=lambda x: (
        x[0].number_of_enrolled_students, time.strptime(x[0].day, '%m/%d/%Y'),
        time.strptime(x[0].start, '%H:%M:%S')))


def sorted_classrooms(classrooms: list) -> list:
    '''
    Sort classrooms by normal capacity

    :return list[Classroom]:
    '''
    return sorted(classrooms, key=lambda x: (x.normal_capacity, x.rarity, len(x.get_characteristics())))


def new_schedule_is_better(old_metric_results: list, JMP_metric_results: list, metrics, len_variables):
    new_solution = PermutationSolution(len_variables, len(metrics))
    new_solution.objectives = JMP_metric_results
    old_solution = PermutationSolution(len_variables, len(metrics))
    old_solution.objectives = old_metric_results

    front = [new_solution, old_solution]
    return JMP().get_best_result(front, metrics) == new_solution


def assign_lessons30(lessons30, lesson, classroom):
    if lesson.time_blocks[0] in lessons30.keys():
        lessons30[lesson.time_blocks[0]].append((lesson, classroom))  # schedule.append((lesson, classroom))
    else:
        lessons30[lesson.time_blocks[0]] = [(lesson, classroom)]


def get_classroom_score(lesson: Lesson, classroom: Classroom, characs: float, len_characs: float,
                        len_characs_div: float, rarity: float, overbooking: float, underbooking: float):
    score = 0

    if lesson.get_requested_characteristics() in classroom.get_characteristics(): score += characs
    score += (len_characs - len(classroom.get_characteristics())) / len_characs_div
    score += (1 - classroom.get_rarity()) * rarity
    if lesson.number_of_enrolled_students > classroom.normal_capacity:
        score += (classroom.normal_capacity / lesson.number_of_enrolled_students) * overbooking
    else:
        score += overbooking
    if lesson.number_of_enrolled_students < classroom.normal_capacity:
        score += (lesson.number_of_enrolled_students / classroom.normal_capacity) * underbooking
    else:
        score += underbooking

    return score


def preparing_classrooms_to_jmp(main_classrooms: list, block: str, half_hour: list) -> list:
    temp_classrooms = [item[1] for item in half_hour]
    classrooms = copy.deepcopy(temp_classrooms)

    for i in range(len(half_hour)):
        if classrooms[i] is not None:
            classrooms[i].set_available(half_hour[i][0].time_blocks)

    classrooms = [classroom for classroom in classrooms if classroom is not None]

    classrooms.extend([main_classrooms[i] for i in range(len(main_classrooms))
                       if main_classrooms[i] not in temp_classrooms and main_classrooms[i].is_available(
            [block])])

    return classrooms

def add_if_not_exists(classrooms: set, classroom: Classroom) -> bool:
    if classroom in classrooms:
        return False
    else:
        classrooms.add(classroom)
        return True

def check_for_collisions(lessons30):
    collisions = 0
    for block, half_hour in lessons30.items():
        classrooms = set()
        for lesson, classroom in half_hour:
            if not add_if_not_exists(classrooms, classroom):
                collisions += 1
    return collisions