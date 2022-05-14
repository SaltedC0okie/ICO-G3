import copy
import time

from alocate.Algorithm_Utils import assign_lessons30, get_classroom_score, new_schedule_is_better, \
    preparing_classrooms_to_jmp
from alocate.Progress import Progress
from jmetalpy.JMP import JMP
from metrics.Metric import RoomlessLessons, Overbooking, Underbooking, BadClassroom
from swrlAPI.SWRL_API import query_result


def weekly_allocation(main_schedule, main_classrooms, progress: Progress, characs=100, len_characs=20, len_characs_div=4,
                      rarity=10, overbooking=50, underbooking=50, use_JMP=True,
                      metrics=[RoomlessLessons(), Overbooking(), Underbooking(), BadClassroom()]) -> dict:
    '''
    More advanced allocation algorithm that allocates the apparent best fitting room for the presented lesson
    and the same lessons in different weeks

    :return list[(Lesson, Classroom)]: Returns list of tuples that associates lesson with allocated classroom
    '''
    # self.classrooms.sort(key=lambda x: x.normal_capacity)
    main_schedule.sort(key=lambda x: (x[0].gang, x[0].subject, x[0].week_day, time.strptime(x[0].day, '%m/%d/%Y')))
    number_of_roomless_lessons = 0
    lessons30 = {}
    last_lesson = ""
    cur_classroom = None
    cur_score = 0

    progress.set_total_tasks_weekly_det(len(main_schedule))

    for lesson, c in main_schedule:
        if not c:
            if lesson.requested_characteristics == "Não necessita de sala":
                assign_lessons30(lessons30, lesson, None)
                progress.inc_cur_tasks_weekly_det()
                continue

            if last_lesson != (
                    lesson.course + lesson.subject + lesson.shift + lesson.gang + lesson.week_day) or (
                    cur_classroom and not cur_classroom.is_available(lesson.time_blocks)):
                last_lesson = (lesson.course + lesson.subject + lesson.shift + lesson.gang + lesson.week_day)
                cur_score = 0
                for classroom in main_classrooms:
                    if not classroom.is_available(lesson.time_blocks):
                        continue

                    new_score = get_classroom_score(lesson, classroom, characs, len_characs, len_characs_div,
                                                    rarity, overbooking, underbooking)

                    if new_score > cur_score:
                        cur_classroom = classroom
                        cur_score = new_score

            if cur_classroom is None:
                assign_lessons30(lessons30, lesson, None)
                number_of_roomless_lessons += 1
                progress.inc_cur_tasks_weekly_det()
                continue

            cur_classroom.set_unavailable(lesson.time_blocks)
            assign_lessons30(lessons30, lesson, cur_classroom)

        else:
            cur_classroom.set_unavailable(lesson.time_blocks)
            assign_lessons30(lessons30, lesson, c)

        progress.inc_cur_tasks_weekly_det()
    # print("There are ", number_of_roomless_lessons, " lessons without a classroom.")
    # metrics = [RoomlessLessons(), Overbooking(), Underbooking(), BadClassroom()]

    # queryresult = query_result(len(metrics))

    count = 0
    blocks_to_improve = []
    if use_JMP and len(metrics) > 0:
        for block, half_hour in lessons30.items():
            old_metric_results = []
            added_to_blocks_to_improve = False
            for metric in metrics:
                metric.reset_metric()
            for metric in metrics:
                metric.calculate(half_hour)
                old_metric_results.append(metric.get_percentage())

                #print(metric.name, ": ", metric.get_percentage(), " > ", metric.prefered_max, " is ", metric.get_percentage() > metric.prefered_max)
                if not added_to_blocks_to_improve and metric.get_percentage() > metric.prefered_max:
                    blocks_to_improve.append((block, half_hour, old_metric_results))
                    added_to_blocks_to_improve = True

        if len(blocks_to_improve) == 0:
            progress.set_total_tasks_weekly_jmp(1)
            progress.inc_cur_tasks_weekly_jmp()
        else:
            progress.set_total_tasks_weekly_jmp(len(blocks_to_improve))

        print("len(blocks_to_improve) = ", len(blocks_to_improve))
        for block, half_hour, old_metric_results in blocks_to_improve:
            classrooms = preparing_classrooms_to_jmp(main_classrooms, block, half_hour)
            lessons = [item[0] for item in half_hour]

            if len(lessons) >= 3:

                new_schedule, JMP_metric_results = JMP().run_algorithm([], lessons, classrooms, metrics)

                if new_schedule_is_better(old_metric_results, JMP_metric_results, metrics,
                                          max(len(lessons), len(classrooms))):
                    '''print("old: ", old_metric_results)
                    print("new: ", JMP_metric_results)
                    print("switching")'''

                    lessons30[block] = new_schedule
            progress.inc_cur_tasks_weekly_jmp()

    else:
        progress.set_total_tasks_weekly_jmp(1)
        progress.inc_cur_tasks_weekly_jmp()
    return lessons30



"""if use_JMP and len(metrics) > 0:
        for block, half_hour in lessons30.items():

            half_hour_is_bad = False
            old_metric_results = []
            for metric in metrics:

                metric.calculate(half_hour)
                old_metric_results.append(metric.get_percentage())

                if metric.get_percentage() > metric.prefered_max:
                    half_hour_is_bad = True

            if half_hour_is_bad:

                classrooms = preparing_classrooms_to_jmp(main_classrooms, block, half_hour)
                lessons = [item[0] for item in half_hour]

                if len(lessons) >= 3:

                    new_schedule, JMP_metric_results = JMP().run_algorithm([], lessons, classrooms, metrics)

                    if new_schedule_is_better(old_metric_results, JMP_metric_results, metrics,
                                              max(len(lessons), len(classrooms))):
                        '''print("old: ", old_metric_results)
                        print("new: ", JMP_metric_results)
                        print("switching")'''

                        lessons30[block] = new_schedule"""