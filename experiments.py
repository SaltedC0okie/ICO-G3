import sys
import time

import csv

from Gang.Gang import Gang
from Metrics import Metric
from Metrics.Metric import Movements, Gaps
from classroom.Classroom import Classroom
from file_manager.Manipulate_Documents import Manipulate_Documents
from alocate.Allocator import Allocator
from lesson.Lesson import Lesson


class Experiments:
    def __init__(self):
        pass

    def test1(self):
        my_list = [1, 2, 3, 4, 5]
        print(my_list[-1:])
        print(my_list[:-2])
        print("s" == 's')
        print(range(5))

    def test2(self):
        file = open('Input_Classrooms/Salas.csv')
        csvreader = csv.reader(file)
        next(csvreader)
        row = next(csvreader)
        caracteristicas = row[5:]
        print(row)
        print(caracteristicas)

    def test3(self):
        for i in range(10):
            print(i)

    def test4(self):
        my_list = []
        my_set = set()
        for i in range(10000000):
            my_list.append(str(i))
            my_set.add(str(i))

        start = time.time()
        print("9999999" in my_list)
        elapsed_time = time.time() - start
        print("lista: ", elapsed_time)

        start = time.time()
        print("9999999" in my_set)
        elapsed_time = time.time() - start
        print("set: ", elapsed_time)

    def test5(self):
        md = Manipulate_Documents()
        lessons, gangs = md.import_schedule_documents()
        classrooms = md.import_classrooms()
        print(gangs)
        print(len(gangs))
        # print(lessons)
        # print(classrooms)

        a = Allocator(classrooms, lessons, gangs)
        a.lessons = [l for l in a.lessons if l.start]
        '''for lesson in lessons:
            a.add_lesson(lesson)
        for classroom in classrooms:
            a.add_classroom(classroom)'''

        simple_schedule = a.simple_allocation()

        md.export_schedule(simple_schedule, "outputMens")

    def test6(self):
        lesson = Lesson("MEI", "ADS", "69420blz", "t-69", 420, "Sex", "3:00:00", "10:00:00", "4/23/2005",
                        "Good, Not stinky, Very good")
        print(sys.getsizeof(lesson.requested_characteristics))
        print(sys.getsizeof(Lesson("MEI", "ADS", "69420blz", "t-69", 420, "Sex", "10:00:00", "10:30:00", "4/23/2005",
                        "Good, Not stinky, Very good")))
        print(sys.getsizeof(""))

    def get_earliest(self):
      pass

    def test7(self):
        md = Manipulate_Documents()
        lessons = md.import_schedule_documents()

        earliest = "23:59:59"
        latest = "00:00:00"
        for lesson in lessons:
            print(lesson.start)
            print(lesson.end, "\n")
            if lesson.start != " " and lesson.start != "" and lesson.start < earliest:
                earliest = lesson.start
            if lesson.end != " " and lesson.end != "" and lesson.end > latest:
                latest = lesson.end

        print("earliest: ", earliest)
        print("latest: ", latest)

    def test8(self):
        string1 = "a"
        string2 = "b"
        print(string1 < string2)


    def test9(self):
        a,b = get_tuplo()
        print(a)
        print(b)

    def test10(self):
        ngosta = getattr(Metric, 'OverBooking')
        atr = ngosta("fdsa", 2)
        atr.testing("fkljdsa")
        print(atr.value)
        print(atr.name)

    def test11(self):
        metrics = [Metric.Overbooking(), Metric.Gaps()]

        for metric in [m for m in metrics if m.m_type == "lesson"]:
            metric.calculate()

    def test12(self):
        lesson1 = Lesson("MEI", "ADS", "69420blz", "t-69", 420, "Sex", "3:00:00", "10:00:00", "4/23/2005",
                        "Good, Not stinky, Very good")
        lesson2 = Lesson("MEI", "ADS", "69420blz", "t-69", 420, "Sex", "11:00:00", "12:00:00", "4/23/2005",
                        "Good, Not stinky, Very good")
        lesson3 = Lesson("MEI", "ADS", "69420blz", "t-69", 420, "Sex", "13:00:00", "15:00:00", "4/23/2005",
                        "Good, Not stinky, Very good")
        classroom1 = Classroom('Edifício 69', 'Auditório 420', 50, 25, ["cenas"])
        classroom2 = Classroom('Edifício 2', 'B203', 150, 125, ["cenas", "mais cenas", "ainda mais cenas"])
        lesson1.add_classroom(classroom1)
        lesson2.add_classroom(classroom2)
        lesson3.add_classroom(classroom2)

        gang = Gang("best", "lei", lesson1)
        gang.add_lesson(lesson2)
        gang.add_lesson(lesson3)

        g = Gaps()
        g.calculate(gang)
        m = Movements()
        m.calculate(gang)

        print(g.value)
        print(m.value)


def get_tuplo():
    return (1, 2)

e = Experiments()
e.test12()
