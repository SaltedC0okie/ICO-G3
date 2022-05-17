import time

from jmetal.algorithm.multiobjective import NSGAII
from jmetal.util.solution import get_non_dominated_solutions
from jmetal.util.termination_criterion import StoppingByEvaluations

from Gang.Gang import Gang
from classroom.Classroom import Classroom
from file_manager.Manipulate_Documents import Manipulate_Documents
#from jmetalpy.TimeSlotCrossover import TimeSlotCrossover
from jmetalpy.TimeSlotMutation import TimeSlotMutation
from jmetalpy.TimeSlotProblem import TimeSlotProblem
from lesson.Lesson import Lesson
from metrics.Metric import NullMetric


head_order = ["Course", "Subject", "Shift", "Class", "Enrolled", "Week", "Duration",
                     "Requested_Char", "Classroom", "Capacity", "Actual_Char"]

file_m = Manipulate_Documents()
lessons, gangs = file_m.import_lessons_and_gangs("Exemplo_de_horario_primeiro_semestre_ICO.csv",head_order, )
classrooms = file_m.import_classrooms()

gangs["gang1"] = Gang("gang1")
metrics = [NullMetric()]

problem = TimeSlotProblem(lessons, classrooms, gangs, metrics, 40, 2018)

alg = NSGAII(
            problem=problem,
            population_size=100,
            offspring_population_size=100,
            mutation=TimeSlotMutation(probability=0.5),  # (probability=1.0 / problem.number_of_variables),
            #crossover=TimeSlotCrossover(probability=0.5),
            termination_criterion=StoppingByEvaluations(max_evaluations=200)
)

s_time = time.time()
alg.run()
print("\n", time.time() - s_time, "\n")

solutions = alg.get_result()
front = get_non_dominated_solutions(solutions)

