from file_manager.Manipulate_Documents import Manipulate_Documents
import statistics

from metrics.Metric import Overbooking

md = Manipulate_Documents(1)
order = [0, 1, 2, 3, 4, 5, 6, 7]
lessons, gangs = md.import_lessons_and_gangs2("input_documents/Exemplo_de_horario_primeiro_semestre_ICO.csv",
                                              order, ["MM", "DD", "YYYY"])

classrooms2 = md.import_classrooms2()

metrics2 = [Overbooking()]


