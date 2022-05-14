import csv
import os
from classroom.Classroom import Classroom
from lesson.Lesson import Lesson
from django.core.files.uploadedfile import TemporaryUploadedFile
import io


class Manipulate_Documents:

    def __init__(self, input_path="input_documents", output_path="output_documents",
                 input_classrooms="input_classrooms"):
        """
        Basic init for Manipulate_Documents

        :param input_path:
        :param output_path:
        :param input_classrooms:
        """
        self.ext = [".csv", ".xml", ".json", ".bd"]
        self.input_path = input_path
        self.output_path = output_path
        self.input_classrooms = input_classrooms

        self.classroom_list = []

    # Código Carlos
    def import_schedule_documents(self, file_name: TemporaryUploadedFile, use_classrooms: bool, header_order: list,
                                  dateformat_list: list, encoding='utf-8'):
        """
        Imports a csv of a schedule into a list of Lesson objects and Gang (class) objects
        :return: a list with a list Classroom objects and a list of Gang objects
        """
        classroom_dict = {}
        for classroom in self.classroom_list:
            classroom_dict[classroom.name] = classroom
        schedule = []
        if encoding not in ["utf-8", "ansi"]:
            csvreader = csv.reader(io.StringIO(file_name.read().decode("utf-8")))
        else:
            csvreader = csv.reader(io.StringIO(file_name.read().decode(encoding)))
        next(csvreader)
        for row in csvreader:
            self.read_schedule_row(row, use_classrooms, classroom_dict, schedule, header_order, dateformat_list)

        file_name.close()
        return schedule

    # Código Nuno
    # def import_schedule_documents(self, file_name: TemporaryUploadedFile, use_classrooms: bool, dateformat_list: list,
    #                               encoding='utf-8'):
    #
    #     """
    #     Imports a csv of a schedule into a list of Lesson objects and Gang (class) objects
    #
    #     :return: a list with a list Classroom objects and a list of Gang objects
    #     """
    #     classroom_dict = {}
    #     for classroom in self.classroom_list:
    #         classroom_dict[classroom.name] = classroom
    #     schedule = []
    #     if encoding not in ["utf-8", "ansi"]:
    #         csvreader = csv.reader(io.StringIO(file_name.read().decode("utf-8")))
    #     else:
    #         csvreader = csv.reader(io.StringIO(file_name.read().decode(encoding)))
    #     next(csvreader)
    #     for row in csvreader:
    #
    #         self.read_schedule_row(row, use_classrooms, classroom_dict, schedule, dateformat_list)
    #
    #     file_name.close()
    #     return schedule


    """
    if row[5] and row[6] and row[8] and int(row[4]) > 5 and row[9] not in ["Não necessita de sala", "Lab ISTA"]:
    """
    def read_schedule_row(self, row, use_classrooms, classroom_dict, schedule, header_order, dateformat_list):
        """
        Reads row of schedule file
        :param header_order:
        :param dateformat_list:
        :param row:
        :param use_classrooms:
        :param classroom_dict:
        :param schedule:
        :return:
        """

        if row[header_order[5]] and row[header_order[6]] and row[header_order[8]]:
            lesson = Lesson(dateformat_list, row[header_order[0]], row[header_order[1]], row[header_order[2]], row[header_order[3]],
                            int(row[header_order[4]]), row[header_order[5]], row[header_order[6]], row[header_order[7]],
                            row[header_order[8]], row[header_order[9]])

            if not use_classrooms or not row[header_order[10]] or row[header_order[10]] not in classroom_dict.keys():
                schedule.append((lesson, None))
            else:
                classroom_dict[row[header_order[10]]].set_unavailable(lesson.generate_time_blocks())
                schedule.append((lesson, classroom_dict[row[header_order[10]]]))

    def import_uploaded_classrooms(self, file_name: TemporaryUploadedFile):
        sum_classroom_characteristics = {}

        csvreader = csv.reader(io.StringIO(file_name.read().decode('utf-8')))
        header = next(csvreader)

        for row in csvreader:
            self.read_classroom_row(row, header, sum_classroom_characteristics)
        self.calculate_classroom_rarity(sum_classroom_characteristics)
        return self.classroom_list


    def import_classrooms(self, file_name: TemporaryUploadedFile):
        """
        Imports a csv into a list of Classroom objects uploaded by the user. If the user doesn't input anything, uses the default file
        Salas.csv

        :return: list of Classroom objects
        """
        sum_classroom_characteristics = {}
        if file_name is not None:
            csvreader = csv.reader(io.StringIO(file_name.read().decode("utf-8")))
        else:
            file_name = open("input_classrooms/Salas.csv", 'r', encoding="utf8")
            csvreader = csv.reader(file_name)
        header = next(csvreader)
        for row in csvreader:
            self.read_classroom_row(row, header, sum_classroom_characteristics)
        file_name.close()
        self.calculate_classroom_rarity(sum_classroom_characteristics)
        return self.classroom_list

    def calculate_classroom_rarity(self, sum_classroom_characteristics):
        '''
        Calculates rarity and saves value in Classroom objects
        :param sum_classroom_characteristics:
        :return:
        '''
        for classroom in self.classroom_list:
            characs = []
            for charac in classroom.get_characteristics():
                characs.append(sum_classroom_characteristics[charac])
            rarity = 1 - (min(characs) / sum(sum_classroom_characteristics.values()))
            classroom.set_rarity(rarity)

    """
        def read_schedule_row(self, row, use_classrooms, classroom_dict, schedule, header_order):
        '''
        Reads row of schedule file
        :param row:
        :param use_classrooms:
        :param classroom_dict:
        :param schedule:
        :return:
        '''
        if row[header_order[5]] and row[header_order[6]] and row[header_order[8]]:
            lesson = Lesson(row[header_order[0]], row[header_order[1]], row[header_order[2]], row[header_order[3]],
                            int(row[header_order[4]]), row[header_order[5]], row[header_order[6]], row[header_order[7]],
                            row[header_order[8]], row[header_order[9]], row[header_order[10]])

            if not use_classrooms or not row[header_order[10]] or row[header_order[10]] not in classroom_dict.keys():
                schedule.append((lesson, None))
            else:
                classroom_dict[row[header_order[10]]].set_unavailable(lesson.generate_time_blocks())
                schedule.append((lesson, classroom_dict[row[header_order[10]]]))

    """

    def read_classroom_row(self, row, header, sum_classroom_characteristics):
        '''
        Read row of classroom file
        :param row:
        :param header:
        :param sum_classroom_characteristics:
        :return:
        '''
        charact_list = []
        for i in range(5, len(row)):
            if row[i].lower() == "x":
                charact_list.append(header[i])
        if int(row[2]) > 5:
            classroom = Classroom(row[0], row[1], int(row[2]), int(row[3]), charact_list)
            self.classroom_list.append(classroom)

            for characteristic in classroom.get_characteristics():
                if characteristic in sum_classroom_characteristics:
                    sum_classroom_characteristics[characteristic] += 1
                else:
                    sum_classroom_characteristics[characteristic] = 1

    def export_schedule(self, schedule: list, file_name: str) -> None:
        """
        Export to a csv file the list of Lesson objects

        :param schedule: it's a list of tuples like this (Lesson, Classroom)
        :param file_name:
        :return:
        """
        try:
            print(1)
            print(os.path.join(self.output_path, file_name) + ".csv")
            with open(os.path.join(self.output_path, file_name) + ".csv", 'w+', newline='') as file:
                print(2)
                # create the csv writer
                writer = csv.writer(file)

                # write first row with headers
                header = ["Curso", "Unidade de execução", "Turno", "Turma", "Inscritos no turno", "Dia da Semana",
                          "Início",
                          "Fim", "Dia", "Características da sala pedida para a aula",
                          "Sala de aula", "Lotação", "Características reais da sala"]
                writer.writerow(header)

                # write rows to the csv file
                for tuple in schedule:
                    row = tuple[0].get_row()
                    if tuple[1] is not None:
                        row.extend([tuple[1].name, tuple[1].normal_capacity,
                                    self.list_to_comma_sep_string(tuple[1].characteristics)])
                    # print("row: ", row)
                    writer.writerow(row)
        except EnvironmentError as e:  # parent of IOError, OSError *and* WindowsError where available
            print("Something went wrong with creating a file to export the results into")
            print(e)

    def export_schedule_lessons30(self, lessons30: dict, file_name: str) -> None:
        """
        Export to a csv file the list of Lesson objects

        :param schedule: it's a list of tuples like this (Lesson, Classroom)
        :param file_name:
        :return:
        """
        try:

            print(os.path.join(self.output_path, file_name) + ".csv")
            with open(os.path.join(self.output_path, file_name) + ".csv", 'w+', newline='') as file:

                # create the csv writer
                writer = csv.writer(file)

                # write first row with headers
                header = ["Curso", "Unidade de execução", "Turno", "Turma", "Inscritos no turno", "Dia da Semana",
                          "Início",
                          "Fim", "Dia", "Características da sala pedida para a aula",
                          "Sala de aula", "Lotação", "Características reais da sala"]
                writer.writerow(header)

                # write rows to the csv file
                flat_list = []
                for sublist in lessons30.values():
                    for item in sublist:
                        flat_list.append(item)

                for tuple in flat_list:
                    row = tuple[0].get_row()
                    if tuple[1] is not None:
                        row.extend([tuple[1].name, tuple[1].normal_capacity,
                                    self.list_to_comma_sep_string(tuple[1].characteristics)])
                    # print("row: ", row)
                    writer.writerow(row)
        except EnvironmentError as e:  # parent of IOError, OSError *and* WindowsError where available
            print("Something went wrong with creating a file to export the results into")
            print(e)

    def export_schedule_str(self, schedule: list) -> str:
        """
        Export to a list the schedule generated with tuples of Lesson and Classroom

        :param schedule:
        :return:
        """

        rows = []

        # write first row with headers
        header = "Curso,Unidade de execução,Turno,Turma,Inscritos no turno,Dia da Semana,Início,Fim,Dia,Características da sala pedida para a aula,Sala de aula,Lotação,Características reais da sala"

        rows.append(header)

        # write lessons and classrooms to rows list
        for tuple in schedule:
            # make row initially with the lesson infos
            row = tuple[0].get_row_str()
            if tuple[1] is not None:
                # add the classroom
                row += "," + tuple[1].name + "," + str(tuple[1].normal_capacity) + "," + \
                       "\"" + self.list_to_comma_sep_string(tuple[1].characteristics) + "\""
            else:
                row += ",,,"
            rows.append(row)
        print(rows)
        return rows

    def list_to_comma_sep_string(self, my_list: list) -> str:
        """
        Takes a list and returns a string with all its values concatenated with a comma and a space
        :param my_list:
        :return:
        """
        string = ""
        for e in my_list:
            string += str(e) + ", "
        string = string[:-2]
        return string
