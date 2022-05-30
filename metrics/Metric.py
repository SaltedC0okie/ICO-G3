import datetime
from typing import List
from abc import ABC, abstractmethod
from jmetal.core.problem import Problem
from Timeslot.TimeSlot import TimeSlot


class Handler(ABC):

    def handle_lesson_classroom(self) -> list:  # List[(Lesson, Classroom)]
        pass

    def handle_gangs_lesson_slot(self) -> list:  # ( dict[String->Gang], dict[Lesson->TimeSlot] )
        pass

    def handle_gangs_everything(self) -> list:  # ( dict[String->Gang], dict[Lesson->(TimeSlot, Classroom)] )
        pass

    def handle_classroom_slot(self) -> list:  # List[(Classroom, TimeSlot)]
        pass


class Metric(ABC):
    m_type = None

    def __init__(self, name, prefered_max=0.4):
        self.name = name
        self.value = []
        self.prefered_max = prefered_max
        self.weight = 0.5

    @abstractmethod
    def calculate(self, input):
        pass

    @abstractmethod
    def reset_metric(self):
        pass


class RoomlessLessons(Metric):

    def __init__(self, prefered_max=0.2):
        super().__init__("Roomless_lessons", prefered_max)
        self.objective = Problem.MINIMIZE
        self.m_type = "gangsWithEverything"  # ( dict[String->Gang], dict[Lesson->(TimeSlot, Classroom)] )
        self.value = 0
        self.total = 0

    def calculate(self, handle_gangs_everything: (dict, dict)):
        """
        Receives a Schedule and calculates the number of lessons without classrooms
        :param handle_gangs_everything:
        :return:
        """

        dict_string_gang, dict_lesson_timeslot_classroom = handle_gangs_everything

        for lesson in dict_lesson_timeslot_classroom.keys():
            classroom = dict_lesson_timeslot_classroom[lesson][1]
            self.total += 1
            if not classroom and lesson.requested_characteristics != "Não necessita de sala":
                self.value += 1

    def get_total_metric_value(self):
        return self.value

    def get_percentage(self):
        return self.value / self.total

    def reset_metric(self):
        self.value = 0
        self.total = 0


class Overbooking(Metric):

    def __init__(self, prefered_max=0.9):
        super().__init__("Overbooking", prefered_max)
        self.objective = Problem.MINIMIZE
        self.m_type = "gangsWithEverything"  # ( dict[String->Gang], dict[Lesson->(TimeSlot, Classroom)] )
        self.value = []

    def calculate(self, handle_gangs_everything: (dict, dict)):
        """
        Receives a Schedule and calculates the Over Booking of the lessons
        :param handle_gangs_everything:
        :return:
        """

        dict_string_gang, dict_lesson_timeslot_classroom = handle_gangs_everything

        for lesson in dict_lesson_timeslot_classroom.keys():
            classroom = dict_lesson_timeslot_classroom[lesson][1]
            if classroom and lesson.number_of_enrolled_students > classroom.normal_capacity:
                self.value.append(classroom.normal_capacity / lesson.number_of_enrolled_students)
            else:
                self.value.append(0)

    def get_total_metric_value(self):
        return sum(self.value)

    def get_percentage(self):
        if len(self.value) == 0:
            return 0
        return sum(self.value) / len(self.value)

    def reset_metric(self):
        self.value = []


class Underbooking(Metric):

    def __init__(self, prefered_max=0.95):
        super().__init__("Underbooking", prefered_max)
        self.objective = Problem.MINIMIZE
        self.m_type = "gangsWithEverything"  # ( dict[String->Gang], dict[Lesson->(TimeSlot, Classroom)] )
        self.prefered_max = prefered_max
        self.weight = 0.25

    def calculate(self, handle_gangs_everything: (dict, dict)):
        """
        Receives a Schedule and calculates the UnderBooking of the lessons
        :param handle_gangs_everything:
        :return:
        """

        dict_string_gang, dict_lesson_timeslot_classroom = handle_gangs_everything

        for lesson in dict_lesson_timeslot_classroom.keys():
            classroom = dict_lesson_timeslot_classroom[lesson][1]
            if classroom and lesson.number_of_enrolled_students < classroom.normal_capacity:
                self.value.append(lesson.number_of_enrolled_students / classroom.normal_capacity)
            else:
                self.value.append(0)

    def get_total_metric_value(self):
        return sum(self.value)

    def get_percentage(self):
        return sum(self.value) / len(self.value)

    def reset_metric(self):
        self.value = []


class BadClassroom(Metric):

    def __init__(self, prefered_max=0.3):
        super().__init__("Bad_classroom", prefered_max)
        self.objective = Problem.MINIMIZE
        self.m_type = "gangsWithEverything"  # ( dict[String->Gang], dict[Lesson->(TimeSlot, Classroom)] )
        self.value = 0
        self.total = 0

    def calculate(self, handle_gangs_everything: (dict, dict)):
        """
        Receives a Schedule and calculates the number of lessons without classroom with requested characteristics
        :return:
        """

        dict_string_gang, dict_lesson_timeslot_classroom = handle_gangs_everything

        for lesson in dict_lesson_timeslot_classroom.keys():
            classroom = dict_lesson_timeslot_classroom[lesson][1]
            if classroom and lesson.requested_characteristics not in classroom.characteristics:
                self.value += 1
            self.total += 1

    def get_total_metric_value(self):
        return self.value

    def get_percentage(self):
        if self.total == 0:
            return 0
        return self.value / self.total

    def reset_metric(self):
        self.value = 0
        self.total = 0


class Gaps(Metric):

    def __init__(self, prefered_max=0.4):
        super().__init__("Gaps", prefered_max)
        self.objective = Problem.MINIMIZE
        self.m_type = "gangsWithEverything"  # ( dict[String->Gang], dict[Lesson->(TimeSlot, Classroom)] )
        self.value = []

    def calculate(self, handle_gangs_everything: (dict, dict)):
        """
        Calculates number of gaps that exist in the given gang and stores the value as an attribute
        :param handle_gangs_everything:
        :return:
        """

        dict_string_gang, dict_lesson_timeslot_classroom = handle_gangs_everything

        filtered = {k: v for k, v in dict_lesson_timeslot_classroom.items()
                    if v[0] is not None and v[1] is not None}
        dict_lesson_timeslot_classroom.clear()
        dict_lesson_timeslot_classroom.update(filtered)

        dict_lesson_timeslot_classroom_sorted = dict(
            sorted(dict_lesson_timeslot_classroom.items(), key=lambda item: (item[1][0].week, item[1][0].weekday,
                                                                             item[1][0].hour, item[1][0].minute)))
        for gang in dict_string_gang.values():
            previous_lesson = None
            for lesson in dict_lesson_timeslot_classroom_sorted.keys():
                if gang in lesson.gang_list:
                    if previous_lesson is None:
                        previous_lesson = lesson
                        continue
                    if dict_lesson_timeslot_classroom_sorted[lesson][0].weekday != \
                            dict_lesson_timeslot_classroom_sorted[previous_lesson][0].weekday:
                        previous_lesson = lesson
                        continue
                    self.value.append(self.blocks_in_interval(dict_lesson_timeslot_classroom_sorted[previous_lesson][0],
                                                              dict_lesson_timeslot_classroom_sorted[lesson][0],
                                                              previous_lesson.duration))
                    previous_lesson = lesson

    def blocks_in_interval(self, prev_time_end: TimeSlot, actual_time_start: TimeSlot, duration: str):
        duration_str = duration.split(":")
        duration = datetime.timedelta(hours=int(duration_str[0]), minutes=int(duration_str[1]))

        t1 = datetime.timedelta(hours=prev_time_end.hour, minutes=prev_time_end.minute) + duration
        t2 = datetime.timedelta(hours=actual_time_start.hour, minutes=actual_time_start.minute)
        t3 = datetime.timedelta(hours=0, minutes=30)

        total_gaps_time = (abs((t2.seconds - t1.seconds)) / 3600) / (t3.seconds / 3600)

        if total_gaps_time < 15:
            return total_gaps_time
        else:
            return 0

    def get_total_metric_value(self):
        return sum([e for e in self.value])

    def get_percentage(self):
        norm = [(float(i) - min(self.value)) / (max(self.value) - min(self.value)) for i in self.value]
        return sum([e for e in norm]) / len(norm)

    def reset_metric(self):
        self.value = []


class RoomMovements(Metric):

    def __init__(self, prefered_max=0.7):
        super().__init__("RoomMovements", prefered_max)
        self.objective = Problem.MINIMIZE
        self.m_type = "gangsWithEverything"  # ( dict[String->Gang], dict[Lesson->(TimeSlot, Classroom)] )
        self.value = []

    def calculate(self, handle_gangs_everything: (dict, dict)):
        """
        Calculates number of RoomMovements that exist in the given gang and stores the value as an attribute
        :param handle_gangs_everything:
        :param handler:
        :return:
        """

        dict_string_gang, dict_lesson_timeslot_classroom = handle_gangs_everything

        filtered = {k: v for k, v in dict_lesson_timeslot_classroom.items()
                    if v[0] is not None and v[1] is not None}
        dict_lesson_timeslot_classroom.clear()
        dict_lesson_timeslot_classroom.update(filtered)

        dict_lesson_timeslot_classroom_sorted = dict(
            sorted(dict_lesson_timeslot_classroom.items(), key=lambda item: (item[1][0].week, item[1][0].weekday,
                                                                             item[1][0].hour, item[1][0].minute)))

        for gang in dict_string_gang.values():
            previous_lesson = None
            movements = 0
            possible_movements = 0
            for lesson in dict_lesson_timeslot_classroom_sorted.keys():
                if gang in lesson.gang_list:
                    possible_movements += 1
                    actual_timeslot = dict_lesson_timeslot_classroom_sorted[lesson][0]
                    actual_classroom = dict_lesson_timeslot_classroom_sorted[lesson][1]
                    if previous_lesson is None:
                        previous_lesson = lesson
                        continue

                    previous_timeslot = dict_lesson_timeslot_classroom_sorted[previous_lesson][0]
                    previous_classroom = dict_lesson_timeslot_classroom_sorted[previous_lesson][1]

                    if actual_timeslot.weekday != previous_timeslot.weekday:
                        previous_lesson = lesson
                        continue
                    if actual_classroom != previous_classroom:
                        movements += 1

                    previous_lesson = lesson
            if possible_movements != 0:
                self.value.append((movements, possible_movements))

    def get_total_metric_value(self):
        return sum([m[0] for m in self.value])

    def get_percentage(self):
        return sum([m[0] for m in self.value]) / sum([m[1] for m in self.value])

    def reset_metric(self):
        self.value = []


class BuildingMovements(Metric):

    def __init__(self, prefered_max=0.4):
        super().__init__("BuildingMovements", prefered_max)
        self.objective = Problem.MINIMIZE
        self.m_type = "gangsWithEverything"  # ( dict[String->Gang], dict[Lesson->(TimeSlot, Classroom)] )
        self.value = []

    def calculate(self, handle_gangs_everything: (dict, dict)):
        """
        Calculates number of BuildingMovements that exist in the given gang and stores the value as an attribute
        :param handle_gangs_everything:
        :return:
        """

        dict_string_gang, dict_lesson_timeslot_classroom = handle_gangs_everything

        filtered = {k: v for k, v in dict_lesson_timeslot_classroom.items()
                    if v[0] is not None and v[1] is not None}
        dict_lesson_timeslot_classroom.clear()
        dict_lesson_timeslot_classroom.update(filtered)

        dict_lesson_timeslot_classroom_sorted = dict(
            sorted(dict_lesson_timeslot_classroom.items(), key=lambda item: (item[1][0].week, item[1][0].weekday,
                                                                             item[1][0].hour, item[1][0].minute)))

        for gang in dict_string_gang.values():
            previous_lesson = None
            movements = 0
            possible_movements = 0
            for lesson in dict_lesson_timeslot_classroom_sorted.keys():
                if gang in lesson.gang_list:
                    actual_timeslot = dict_lesson_timeslot_classroom_sorted[lesson][0]
                    actual_classroom = dict_lesson_timeslot_classroom_sorted[lesson][1]
                    if previous_lesson is None:
                        previous_lesson = lesson
                        continue

                    previous_timeslot = dict_lesson_timeslot_classroom_sorted[previous_lesson][0]
                    previous_classroom = dict_lesson_timeslot_classroom_sorted[previous_lesson][1]

                    if actual_timeslot.weekday != previous_timeslot.weekday:
                        previous_lesson = lesson
                        continue
                    if actual_classroom.building != previous_classroom.building:
                        movements += 1

                    possible_movements += 1
            self.value.append((movements, possible_movements))

    def get_total_metric_value(self):
        return sum([m[0] for m in self.value])

    def get_percentage(self):
        return sum([m[0] for m in self.value]) / sum([m[1] for m in self.value])

    def reset_metric(self):
        self.value = []


class ClassroomInconsistency(Metric):

    def __init__(self, prefered_max=0.4):
        super().__init__("ClassroomInconsistency", prefered_max)
        self.objective = Problem.MINIMIZE
        self.m_type = "gangsWithEverything"  # ( dict[String->Gang], dict[Lesson->(TimeSlot, Classroom)] )
        self.value = []

    def calculate(self, handle_gangs_everything: (dict, dict)):
        """
        Receives a Schedule and calculates the ClassroomInconsistency
        :param handle_gangs_everything:
        :return:
        """

        dict_string_gang, dict_lesson_timeslot_classroom = handle_gangs_everything

        filtered = {k: v for k, v in dict_lesson_timeslot_classroom.items()
                    if v[0] is not None and v[1] is not None}
        dict_lesson_timeslot_classroom.clear()
        dict_lesson_timeslot_classroom.update(filtered)

        dict_lesson_timeslot_classroom_sorted = dict(
            sorted(dict_lesson_timeslot_classroom.items(), key=lambda item: (item[1][0].week, item[1][0].weekday,
                                                                             item[1][0].hour, item[1][0].minute)))

        for gang in dict_string_gang.values():
            dict_subject = {}
            for lesson in dict_lesson_timeslot_classroom_sorted.keys():
                if gang in lesson.gang_list:
                    classroom = dict_lesson_timeslot_classroom_sorted[lesson][1]
                    if lesson.subject not in dict_subject.keys():
                        dict_subject[lesson.subject] = [{classroom}, 1]
                    else:
                        dict_subject[lesson.subject][0].add(classroom)
                        dict_subject[lesson.subject][1] = dict_subject[lesson.subject][1] + 1

            for c, pc in dict_subject.values():
                self.value.append((len(c), pc))

    def get_total_metric_value(self):
        return sum([m[0] for m in self.value])

    def get_percentage(self):
        return sum([m[0] for m in self.value]) / sum([m[1] for m in self.value])

    def reset_metric(self):
        self.value = []


class ClassroomCollisions(Metric):

    def __init__(self, prefered_max=0.4):
        super().__init__("ClassroomCollisions", prefered_max)
        self.objective = Problem.MAXIMIZE
        self.m_type = "gangsWithEverything"  # ( dict[String->Gang], dict[Lesson->(TimeSlot, Classroom)] )
        self.value = 0
        self.total = 0

    def calculate(self, handle_gangs_everything: (dict, dict)):
        """
        Receives a Schedule and calculates the number of times a classroom is assigned more than once in a half hour
        block :param
        handler: :return:
        """
        dict_string_gang, dict_lesson_timeslot_classroom = handle_gangs_everything

        filtered = {k: v for k, v in dict_lesson_timeslot_classroom.items()
                    if v[0] is not None and v[1] is not None}
        dict_lesson_timeslot_classroom.clear()
        dict_lesson_timeslot_classroom.update(filtered)

        collisions = 0
        possible_collisions = 0
        classrooms_set = set()

        try:

            for timeslot, classroom in dict_lesson_timeslot_classroom.values():
                possible_collisions += 1
                if classroom not in classrooms_set:
                    classrooms_set.add(classroom)
                else:
                    collisions += 1

            self.value = collisions
            self.total = possible_collisions

        except AttributeError:
            self.value = -1
            self.total = 1

    def get_total_metric_value(self):
        return self.value

    def get_percentage(self):
        if self.value == -1:
            return 1
        return self.value / self.total

    def reset_metric(self):
        self.value = 0
        self.total = 0


class LessonCollisions(Metric):

    def __init__(self, prefered_max=0.4):
        super().__init__("LessonCollisions", prefered_max)
        self.objective = Problem.MAXIMIZE
        self.m_type = "gangsWithEverything"  # ( dict[String->Gang], dict[Lesson->(TimeSlot, Classroom)] )
        self.value = 0
        self.total = 0

    def calculate(self, handle_gangs_everything: (dict, dict)):
        """
        Receives a Schedule and calculates the number of times a classroom is assigned more than once in a half hour
        block :param
        handler: :return:
        """
        dict_string_gang, dict_lesson_timeslot_classroom = handle_gangs_everything
        filtered = {k: v for k, v in dict_lesson_timeslot_classroom.items()
                    if v[0] is not None and v[1] is not None}
        dict_lesson_timeslot_classroom.clear()
        dict_lesson_timeslot_classroom.update(filtered)

        dict_lesson_timeslot_classroom_sorted = dict(
            sorted(dict_lesson_timeslot_classroom.items(), key=lambda item: (item[1][0].week, item[1][0].weekday,
                                                                             item[1][0].hour, item[1][0].minute)))
        for gang in dict_string_gang.values():
            collisions = 0
            possible_collisions = 0
            timeslot_set = set()
            for lesson in dict_lesson_timeslot_classroom_sorted.keys():
                if gang in lesson.gang_list:
                    possible_collisions += 1
                    timeslot = dict_lesson_timeslot_classroom_sorted[lesson][0]
                    for ts in timeslot_set:
                        if timeslot.week == ts.week and timeslot.weekday == ts.weekday \
                                and timeslot.hour == ts.hour and timeslot.minute == ts.minute:
                            collisions += 1
                            break
                    timeslot_set.add(timeslot)
            self.value += collisions
            self.total += possible_collisions

    def get_total_metric_value(self):
        return self.value

    def get_percentage(self):
        if self.total == 0:
            return 0
        return self.value / self.total

    def reset_metric(self):
        self.value = 0
        self.total = 0


class GangLessonVolume(Metric):

    def __init__(self, prefered_max=0.4):
        super().__init__("GangLessonVolume", prefered_max)
        self.objective = Problem.MINIMIZE
        self.m_type = "gangsWithEverything"  # ( dict[String->Gang], dict[Lesson->(TimeSlot, Classroom)] )
        self.value = []

    def calculate(self, handle_gangs_everything: (dict, dict)):
        """
        Receives a Schedule and calculates the ClassroomInconsistency
        :param handle_gangs_everything:
        :return:
        """

        dict_string_gang, dict_lesson_timeslot_classroom = handle_gangs_everything

        filtered = {k: v for k, v in dict_lesson_timeslot_classroom.items()
                    if v[0] is not None and v[1] is not None}
        dict_lesson_timeslot_classroom.clear()
        dict_lesson_timeslot_classroom.update(filtered)

        dict_lesson_timeslot_classroom_sorted = dict(
            sorted(dict_lesson_timeslot_classroom.items(), key=lambda item: (item[1][0].week, item[1][0].weekday,
                                                                             item[1][0].hour, item[1][0].minute)))

        for gang in dict_string_gang.values():
            previous_lesson = None
            duration_list = []
            for lesson in dict_lesson_timeslot_classroom_sorted.keys():
                if gang in lesson.gang_list:
                    actual_timeslot = dict_lesson_timeslot_classroom_sorted[lesson][0]

                    if previous_lesson is None:
                        duration_list.append(lesson.duration)
                        previous_lesson = lesson
                        continue

                    previous_timeslot = dict_lesson_timeslot_classroom_sorted[previous_lesson][0]

                    if actual_timeslot.weekday != previous_timeslot.weekday:
                        self.value.append(self.number_of_hours(duration_list))
                        duration_list = [lesson.duration]
                        previous_lesson = lesson
                        continue

                    duration_list.append(lesson.duration)
                    previous_lesson = lesson

    def number_of_hours(self, duration_list: List[str]):
        total_time = 0
        for duration in duration_list:
            duration_str = duration.split(":")
            total_time += int(duration_str[0]) + int(duration_str[1]) / 60
        return total_time

    def get_total_metric_value(self):
        return sum([m for m in self.value])

    # TODO - find the best way to get the percentage
    def get_percentage(self):
        norm = [(float(i) - min(self.value)) / (max(self.value) - min(self.value)) for i in self.value]
        return sum([e for e in norm]) / len(norm)

    def reset_metric(self):
        self.value = []


class GangLessonDistribution(Metric):

    def __init__(self, prefered_max=0.4):
        super().__init__("GangLessonDistribution", prefered_max)
        self.objective = Problem.MINIMIZE
        self.m_type = "gangsWithEverything"  # ( dict[String->Gang], dict[Lesson->(TimeSlot, Classroom)] )
        self.value = []

    def calculate(self, handle_gangs_everything: (dict, dict)):
        """
        Receives a Schedule and calculates the ClassroomInconsistency
        :param handle_gangs_everything:
        :param handler:
        :return:
        """

        dict_string_gang, dict_lesson_timeslot_classroom = handle_gangs_everything

        filtered = {k: v for k, v in dict_lesson_timeslot_classroom.items()
                    if v[0] is not None and v[1] is not None}
        dict_lesson_timeslot_classroom.clear()
        dict_lesson_timeslot_classroom.update(filtered)

        dict_lesson_timeslot_classroom_sorted = dict(
            sorted(dict_lesson_timeslot_classroom.items(), key=lambda item: (item[1][0].week, item[1][0].weekday,
                                                                             item[1][0].hour, item[1][0].minute)))

        for gang in dict_string_gang.values():
            previous_lesson = None
            time_slot_list = []
            for lesson in dict_lesson_timeslot_classroom_sorted.keys():
                if gang in lesson.gang_list:
                    actual_timeslot = dict_lesson_timeslot_classroom_sorted[lesson][0]
                    time_slot_list.append(actual_timeslot)
                    if previous_lesson is None:
                        previous_lesson = lesson
                        continue

                    previous_timeslot = dict_lesson_timeslot_classroom_sorted[previous_lesson][0]

                    if actual_timeslot.weekday != previous_timeslot.weekday:
                        previous_lesson = lesson
                        continue

            self.value.append(self.time_slot_interval_distribution(time_slot_list))

    def time_slot_interval_distribution(self, time_slot_list: List[TimeSlot]):

        lesson_distribution_list = []

        dict_distribution = {}

        morning_start = datetime.timedelta(hours=8, minutes=0)
        morning_end = datetime.timedelta(hours=12, minutes=0)

        afternoon_start = datetime.timedelta(hours=12, minutes=0)
        afternoon_end = datetime.timedelta(hours=18, minutes=0)

        evening_start = datetime.timedelta(hours=18, minutes=0)
        evening_end = datetime.timedelta(hours=22, minutes=0)

        for ts in time_slot_list:
            time_slot = datetime.timedelta(hours=ts.hour, minutes=ts.minute)
            if morning_start < time_slot < morning_end:
                lesson_distribution_list.append("MORNING")
                pass
            elif afternoon_start < time_slot < afternoon_end:
                lesson_distribution_list.append("AFTERNOON")
                pass
            elif evening_start < time_slot < evening_end:
                lesson_distribution_list.append("EVENING")
                pass

        dict_distribution["MORNING"] = lesson_distribution_list.count("MORNING")
        dict_distribution["AFTERNOON"] = lesson_distribution_list.count("AFTERNOON")
        dict_distribution["EVENING"] = lesson_distribution_list.count("EVENING")
        total_distribution = lesson_distribution_list.count("MORNING") + lesson_distribution_list.count(
            "AFTERNOON") + lesson_distribution_list.count("EVENING")
        # Check this

        dict_distribution = sorted(dict_distribution.items(), key=lambda item: item[1])
        dict_distribution = dict([(k, v) for k, v in dict_distribution])
        dict_distribution.popitem()
        bad_distribution = sum(dict_distribution.values())
        if total_distribution == 0:
            return 0
        else:
            return bad_distribution / total_distribution

    def get_total_metric_value(self):
        return sum([m for m in self.value])

    def get_percentage(self):
        return sum([m for m in self.value]) / len(self.value)

    def reset_metric(self):
        self.value = []


class LessonInconsistency(Metric):

    def __init__(self, prefered_max=0.4):
        super().__init__("LessonInconsistency", prefered_max)
        self.objective = Problem.MINIMIZE
        self.m_type = "gangsWithEverything"  # ( dict[String->Gang], dict[Lesson->(TimeSlot, Classroom)] )
        self.value = []

    def calculate(self, handle_gangs_everything: (dict, dict)):
        """
        Receives a Schedule and calculates the ClassroomInconsistency
        :param handle_gangs_everything:
        :return:
        """

        dict_string_gang, dict_lesson_timeslot_classroom = handle_gangs_everything

        filtered = {k: v for k, v in dict_lesson_timeslot_classroom.items()
                    if v[0] is not None and v[1] is not None}
        dict_lesson_timeslot_classroom.clear()
        dict_lesson_timeslot_classroom.update(filtered)

        dict_lesson_timeslot_classroom_sorted = dict(
            sorted(dict_lesson_timeslot_classroom.items(), key=lambda item: (item[1][0].week, item[1][0].weekday,
                                                                             item[1][0].hour, item[1][0].minute)))

        for gang in dict_string_gang.values():
            dict_subject = {}
            for lesson in dict_lesson_timeslot_classroom_sorted.keys():
                if gang in lesson.gang_list:
                    actual_timeslot = dict_lesson_timeslot_classroom_sorted[lesson][0]

                    if lesson.subject not in dict_subject.keys():
                        dict_subject[lesson.subject] = [{actual_timeslot}, 1]
                    else:
                        dict_subject[lesson.subject][0].add(actual_timeslot)
                        dict_subject[lesson.subject][1] = dict_subject[lesson.subject][1] + 1

            for ts, pts in dict_subject.values():
                self.value.append((len(ts), pts))

    def get_total_metric_value(self):
        return sum([m[0] for m in self.value])

    def get_percentage(self):
        return sum([m[0] for m in self.value]) / sum([m[1] for m in self.value])

    def reset_metric(self):
        self.value = []
