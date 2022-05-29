from file_manager.Manipulate_Documents import Manipulate_Documents
import statistics

md = Manipulate_Documents(1)
order = [0, 1, 2, 3, 4, 5, 6, 7]
lessons, gangs = md.import_lessons_and_gangs2("input_documents/Exemplo_de_horario_primeiro_semestre_ICO.csv",
                                              order, ["MM", "DD", "YYYY"])

num_lessons_list = []
for name, gang in gangs.items():
    num_lessons_list.append(len(gang.lessons))

print("Max=", max(num_lessons_list))
print("Min=", min(num_lessons_list))
print("Avg=", sum(num_lessons_list)/len(num_lessons_list))
print("Mediana=", statistics.median(num_lessons_list))