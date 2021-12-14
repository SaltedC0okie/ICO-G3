from alocate.Algorithm_Utils import sorted_lessons, sorted_classrooms, assign_lessons30, new_schedule_is_better
from jmetalpy.JMP import JMP
from swrlAPI.SWRL_API import query_result


def overbooking_with_jmp_algorithm(overbooking_percentage: int, schedule: list, classrooms: list,
                                   metrics: list) -> dict:
    """
    This Algorithm iterates by the schedule and classroom and tries to allocate lessons to classroom if
    every requirement gets fulfilled by the conditions. Then uses JMetalPy to improve some problematic zones of
    our schedule.

    :param metrics:
    :param classrooms:
    :param schedule:
    :param overbooking_percentage: percentage of overbooking inputed by the user
    :return:
    """
    lessons_list = sorted_lessons(schedule)
    classrooms_list = sorted_classrooms(classrooms)
    lessons30 = {}
    number_of_roomless_lessons = 0
    for lesson, c in lessons_list:
        if not c:
            classroom_assigned = False
            for classroom in classrooms_list:
                if (lesson.get_requested_characteristics() in classroom.get_characteristics()) and \
                        (0 < lesson.get_number_of_enrolled_students() <= classroom.get_normal_capacity() *
                         (1 + (overbooking_percentage / 100))) and \
                        (classroom.is_available(lesson.generate_time_blocks())):
                    classroom.set_unavailable(lesson.generate_time_blocks())
                    assign_lessons30(lessons30, lesson, classroom)
                    classroom_assigned = True
                    break
            if not classroom_assigned:
                if lesson.requested_characteristics != "Não necessita de sala" and \
                        lesson.requested_characteristics != "Lab ISTA" and lesson.number_of_enrolled_students != 0:
                    assign_lessons30(lessons30, lesson, None)
                    number_of_roomless_lessons += 1
        else:
            assign_lessons30(lessons30, lesson, c)

    queryresult = query_result(len(metrics))
    troublesome_lessons30_key_list = sorted(lessons30, key=lambda k: len(lessons30[k]), reverse=True)[:5]

    for tbl in troublesome_lessons30_key_list:
        old_metrics = []

        for m in metrics:
            m.calculate(lessons30[tbl])
            old_metrics.append(m.get_percentage())

        trouble_l = []
        trouble_c = set()
        for t_l, t_c in lessons30[tbl]:
            trouble_l.append(t_l)
            if t_c is not None:
                t_c.set_available(t_l.generate_time_blocks())
                trouble_c.add(t_c)

        if len(trouble_l) > 3:
            new_schedule, jmp_metric_results = JMP().run_algorithm(queryresult, trouble_l, list(trouble_c),
                                                                   metrics)
            if new_schedule_is_better(old_metrics, jmp_metric_results, metrics,
                                      max(len(trouble_l), len(list(trouble_c)))):
                lessons30[tbl] = new_schedule

    print("There are ", number_of_roomless_lessons, " lessons without a classroom.")
    return lessons30
