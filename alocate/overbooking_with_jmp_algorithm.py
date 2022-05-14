from alocate.Algorithm_Utils import sorted_lessons, sorted_classrooms, assign_lessons30, new_schedule_is_better, \
    preparing_classrooms_to_jmp
from alocate.Progress import Progress
from jmetalpy.JMP import JMP
from swrlAPI.SWRL_API import query_result


def overbooking_with_jmp_algorithm(schedule: list, classrooms: list, metrics: list, progress: Progress, overbooking_percentage=20,
                                   use_jmp=True) -> dict:
    """
    This Algorithm iterates by the schedule and classroom and tries to allocate lessons to classroom if
    every requirement gets fulfilled by the conditions. Then uses JMetalPy to improve some problematic zones of
    our schedule.

    :param use_jmp:
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
    progress.set_total_tasks_overbooking_det(len(lessons_list))
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
                assign_lessons30(lessons30, lesson, None)
                number_of_roomless_lessons += 1
        else:
            assign_lessons30(lessons30, lesson, c)
        progress.inc_cur_tasks_overbooking_det()


    if use_jmp:
        # queryresult = query_result(len(metrics))
        troublesome_lessons30_key_list = sorted(lessons30, key=lambda k: len(lessons30[k]), reverse=True)[:5]
        progress.set_total_tasks_overbooking_jmp(len(troublesome_lessons30_key_list))

        for tbl in troublesome_lessons30_key_list:
            old_metrics = []

            for m in metrics:
                m.calculate(lessons30[tbl])
                old_metrics.append(m.get_percentage())

            trouble_l = [item[0] for item in lessons30[tbl]]
            trouble_c = preparing_classrooms_to_jmp(classrooms, tbl, lessons30[tbl])
            if len(trouble_l) > 3:
                new_schedule, jmp_metric_results = JMP().run_algorithm([], trouble_l, list(trouble_c),
                                                                       metrics)
                if new_schedule_is_better(old_metrics, jmp_metric_results, metrics,
                                          max(len(trouble_l), len(list(trouble_c)))):
                    lessons30[tbl] = new_schedule
            progress.inc_cur_tasks_overbooking_jmp()
    else:
        progress.set_total_tasks_overbooking_jmp(1)
        progress.inc_cur_tasks_overbooking_jmp()

    #print("There are ", number_of_roomless_lessons, " lessons without a classroom.")
    return lessons30
