from alocate.Algorithm_Utils import sorted_lessons, sorted_classrooms, assign_lessons30
from alocate import Progress

def simple_allocation(schedule: list, classrooms: list, progress: Progress) -> list:
    '''
    Simple allocation algorithm that allocates first room that accommodates the lessons requested characteristics
    and is available at that time

    :return list[(Lesson, Classroom)]: Returns list of tuples that associates lesson with allocated classroom
    '''
    lessons_list = sorted_lessons(schedule)
    classrooms_list = sorted_classrooms(classrooms)

    number_of_roomless_lessons = 0

    #schedule = []
    lessons30 = {}
    lessons_len = len(lessons_list)
    progress.set_total_tasks_simple(lessons_len)

    for lesson, c in lessons_list:
        if not c:
            classroom_assigned = False
            for classroom in classrooms_list:
                if (lesson.get_requested_characteristics() in classroom.get_characteristics()) and \
                        (lesson.get_number_of_enrolled_students() <= classroom.get_normal_capacity()) and \
                        (classroom.is_available(lesson.generate_time_blocks())):
                    classroom.set_unavailable(lesson.generate_time_blocks())
                    assign_lessons30(lessons30, lesson, classroom)
                    #schedule.append((lesson, classroom))
                    classroom_assigned = True
                    break

            if not classroom_assigned:
                if lesson.requested_characteristics != "Não necessita de sala" and \
                        lesson.requested_characteristics != "Lab ISTA":
                    assign_lessons30(lessons30, lesson, classroom)
                    #schedule.append((lesson, None))
                    number_of_roomless_lessons += 1
        else:
            assign_lessons30(lessons30, lesson, classroom)
            #schedule.append((lesson, c))
        progress.inc_cur_tasks_simple()

    return lessons30
    #return schedule
