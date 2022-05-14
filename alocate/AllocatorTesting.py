from classroom.Classroom import Classroom
from lesson.Lesson import Lesson


def test_add_classroom(alloc):
    c1 = Classroom('Edifício Sedas Nunes (ISCTE-IUL)', 'Auditório 4', 250, 125, ["cenas", "mais cenas"])
    c2 = Classroom('Edifício 2', 'B203', 150, 125, ["cenas", "mais cenas", "ainda mais cenas"])
    c3 = Classroom('Edifício 69', 'Auditório 420', 50, 25, ["cenas"])
    c4 = Classroom('Edifício Sedas Nunes (ISCTE-IUL)', 'Auditório 4', 250, 125, ["cenas", "mais cenas", "outras cenas"])
    c5 = Classroom('Edifício Sedas Nunes (ISCTE-IUL)', 'Sala daquelas tipo fixes', 250, 125, ["cenas", "mais cenas"])

    alloc.add_classroom(c1)
    alloc.add_classroom(c2)
    alloc.add_classroom(c3)
    alloc.add_classroom(c4)
    alloc.add_classroom(c5)

    print_elements_in_list(alloc.classrooms)


def test_add_lesson(alloc):
    l1 = Lesson("MEI", "ADS", "69420blz", "t-69", 69, "Sex", "10:00:00", "10:00:00", "4/23/2005",
                "Good, Not stinky, Very good")
    l2 = Lesson("LEI", "PCD", "69420blzit", "t-420", 420, "Qui", "3:00:00", "10:00:00", "12/23/2005",
                "Good, Not stinky")
    l3 = Lesson("ETI", "Irrelevant stuff", "42069blz", "t-1337", 420, "Sex", "3:00:00", "10:00:00", "4/06/2005",
                "Good, Very good")
    l4 = Lesson("MEI", "GSI", "4269blzit", "t-69", 42069, "Sex", "3:00:00", "10:00:00", "9/14/2015",
                "Not stinky, Very good")
    l5 = Lesson("MEI", "SRSI", "Ya drenas", "t-69", 420, "Qua", "3:00:00", "10:00:00", "5/31/2069", "Not stinky")

    alloc.add_lesson(l1)
    alloc.add_lesson(l2)
    alloc.add_lesson(l3)
    alloc.add_lesson(l4)
    alloc.add_lesson(l5)

    print_elements_in_list(alloc.lessons)


def test_sort_lessons(alloc):
    print_elements_in_list(alloc.lessons)
    alloc.sort_lessons()
    print_elements_in_list(alloc.lessons)


def test_sort_classrooms(alloc):
    print_elements_in_list(alloc.classrooms)
    alloc.sort_classrooms()
    print_elements_in_list(alloc.classrooms)


def test_simple_allocation(alloc):
    sched = alloc.simple_allocation()
    print(sched)


def test_add_classroom_to_lesson(alloc):
    alloc.add_classroom_to_lesson()


def test_remove_classroom_from_lesson(alloc):
    alloc.remove_classroom_from_lesson()


def test_remove_all_allocations(alloc):
    alloc.remove_all_allocations()


def print_elements_in_list(list):
    for e in list:
        print(e)
    print()


#test_sort_lessons(allocator)
#test_sort_classrooms(allocator)
# test_add_classroom_to_lesson(allocator)
# test_remove_classroom_from_lesson(allocator)
# test_remove_all_allocations(allocator)
