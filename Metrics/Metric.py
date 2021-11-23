from abc import ABC, abstractmethod
from Gang import Gang
from lesson import Lesson
import time


class Metric(ABC):
    m_type = None

    def __init__(self, name):
        self.name = name
        self.values = []

    @abstractmethod
    def calculate(self, input):
        pass


class Overbooking(Metric):

    def __init__(self):
        self.name = "Overbooking"
        self.m_type = "lessons"

    def calculate(self):
        print("I got the smarts, quick mafs")
        '''lista = [1,2,3]
        for lesson in lessons:
            obj = lista[0]()
            obj.evaluate_metric(input)'''


class Gaps(Metric):

    def __init__(self):
        self.name = "Gaps"
        self.m_type = "gangs"
        self.value = 0

    def calculate(self, input):
        gang_lessons = input.lessons
        gang_lessons.sort(key=lambda x: (time.strptime(x.day, '%m/%d/%Y'), time.strptime(x.start, '%H:%M:%S')))

        first_lesson = gang_lessons[0]
        last_end = first_lesson.end
        last_day = first_lesson.day
        for lesson in gang_lessons[1:]:
            if lesson.start != last_end and lesson.day == last_day:
                self.value += 1
            last_end = lesson.end


class Movements(Metric):

    def __init__(self):
        self.name = "Movements"
        self.m_type = "gangs"
        self.value = 0

    def calculate(self, input):
        gang_lessons = input.lessons
        gang_lessons.sort(key=lambda x: (time.strptime(x.day, '%m/%d/%Y'), time.strptime(x.start, '%H:%M:%S')))

        first_lesson = gang_lessons[0]
        last_classroom = first_lesson.classroom
        last_day = first_lesson.day
        for lesson in gang_lessons[1:]:
            if lesson.classroom != last_classroom and lesson.day == last_day:
                self.value += 1
            last_classroom = lesson.classroom

class UsedRooms(Metric):

    def __init__(self):
        self.name = "UsedRooms"
        self.m_type = "lessons"
        self.values = []
        self.value = 0

    def calculate(self, lesson, classroom):
        if classroom not in self.values:
            self.values.append(classroom)
            self.value += 1