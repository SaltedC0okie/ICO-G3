import csv
import os
from datetime import datetime, timedelta
from typing import List

from Gang.Gang import Gang
from classroom.Classroom import Classroom
from lesson.Lesson import Lesson
from django.core.files.uploadedfile import TemporaryUploadedFile
import io


class Manipulate_Documents:

    def __init__(self, semester_starting_day, input_path="input_documents", output_path="output_documents",
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
        # TODO
        self.semester_starting_day = semester_starting_day
        self.classroom_list = []

    # Código Carlos
    def import_lessons_and_gangs(self, file_name: TemporaryUploadedFile, header_order: list,
                                 dateformat_list: list, encoding='utf-8'):
        """
        Imports a csv of a schedule into a list of Lesson objects and Gang (class) objects
        :return: a list with a list Classroom objects and a list of Gang objects
        """
        lesson_list = []
        gang_list = {}

        if encoding not in ["utf-8", "ansi"]:
            csvreader = csv.reader(io.StringIO(file_name.read().decode("utf-8")), delimiter=';')
        else:
            csvreader = csv.reader(io.StringIO(file_name.read().decode(encoding)), delimiter=';')
        next(csvreader)
        for row in csvreader:
            self.read_schedule_row(row, lesson_list, gang_list, header_order, dateformat_list)

        file_name.close()
        return lesson_list, gang_list

    def import_lessons_and_gangs2(self, file_name: str, header_order: list,
                                  dateformat_list: list, encoding='utf-8'):
        """
        Imports a csv of a schedule into a list of Lesson objects and Gang (class) objects
        :return: a list with a list Classroom objects and a list of Gang objects
        """
        lesson_list = []
        gang_list = {}

        if encoding not in ["utf-8", "ansi"]:
            csvreader = csv.reader(open(file_name, "r", encoding="utf-8"), delimiter=';')
        else:
            csvreader = csv.reader(open(file_name, "r", encoding=encoding), delimiter=';')
        next(csvreader)
        for i, row in enumerate(csvreader):
            self.read_schedule_row(row, lesson_list, gang_list, header_order, dateformat_list)

        return lesson_list, gang_list

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

    def read_schedule_row(self, row, lesson_list, gang_list, header_order, dateformat_list):
        """
        Reads row of schedule file
        :param lesson_list:
        :param gang_list:
        :param header_order:
        :param dateformat_list:
        :param row:
        :param use_classrooms:
        :return:
        """
        if row[header_order[5]] and row[header_order[6]]:
            if not row[header_order[4]]:
                row[header_order[4]] = 30

            lesson_gangs = []
            for g in row[header_order[3]].split(","):
                if g not in gang_list:
                    gang_list[g] = Gang(g)
                lesson_gangs.append(gang_list[g])

            lesson = Lesson(dateformat_list,
                            row[header_order[0]],  # Curso
                            row[header_order[1]],  # Unidade de executaçao
                            row[header_order[2]],  # Turno
                            lesson_gangs,  # Turma
                            int(row[header_order[4]]),  # Inscritos no turno
                            row[header_order[5]],  # semana
                            row[header_order[6]],  # duraçao
                            row[header_order[7]])  # caracteristicas

            lesson_list.append(lesson)

            for g in lesson_gangs:
                g.add_lesson(lesson)

    def import_uploaded_classrooms(self, file_name: TemporaryUploadedFile):
        sum_classroom_characteristics = {}

        csvreader = csv.reader(io.StringIO(file_name.read().decode('utf-8')), delimiter=';')
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
            csvreader = csv.reader(io.StringIO(file_name.read().decode("utf-8")), delimiter=';')
        else:
            file_name = open("input_classrooms/Salas.csv", 'r', encoding="utf8")
            csvreader = csv.reader(file_name, delimiter=';')
        header = next(csvreader)
        for row in csvreader:
            self.read_classroom_row(row, header, sum_classroom_characteristics)
        file_name.close()
        self.calculate_classroom_rarity(sum_classroom_characteristics)
        return self.classroom_list

    def import_classrooms2(self, file_name: str = "../input_classrooms/Salas.csv"):
        """
        Imports a csv into a list of Classroom objects uploaded by the user. If the user doesn't input anything, uses the default file
        Salas.csv

        :return: list of Classroom objects
        """
        sum_classroom_characteristics = {}
        file_name = open(file_name, 'r', encoding="utf8")
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
        header = "Curso,Unidade de execução,Turno,Turma,Inscritos no turno,Dia da Semana,Início,Fim,Dia," \
                 "Características da sala pedida para a aula,Sala de aula,Lotação,Características reais da sala"

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

    def import_schedule_documents_old(self, file_name: str, use_classrooms: bool, encoding: str = "utf-8"):
        """
        Imports a csv of a schedule into a list of Lesson objects and Gang (class) objects
        :return: a list with a list Classroom objects and a list of Gang objects
        """
        classroom_dict = {}
        for classroom in self.classroom_list:
            classroom_dict[classroom.name] = classroom
        schedule = []

        csvreader = csv.reader(open(file_name, "r", encoding=encoding))
        next(csvreader)
        for row in csvreader:
            self.read_schedule_row(row, use_classrooms, classroom_dict, schedule)

        file_name.close()
        return schedule

    def read_schedule_row_old(self, row, use_classrooms, classroom_dict, schedule):
        '''
        Reads row of schedule file
        :param row:
        :param use_classrooms:
        :param classroom_dict:
        :param schedule:
        :return:
        '''
        if row[5] and row[6] and row[8]:
            lesson = Lesson(row[0], row[1], row[2], row[3],
                            int(row[4]), row[5], row[6], row[7], row[8], row[9])

            if not use_classrooms or not row[10] or row[10] not in classroom_dict.keys():
                schedule.append((lesson, None))
            else:
                classroom_dict[row[10]].set_unavailable(lesson.generate_time_blocks())
                schedule.append((lesson, classroom_dict[row[10]]))

    def read_schedule_row_testing(self, row, lesson_list, gang_list, header_order, dateformat_list):
        """
        Reads row of schedule file
        :param lesson_list:
        :param gang_list:
        :param header_order:
        :param dateformat_list:
        :param row:
        :param use_classrooms:
        :return:
        """
        if len(row) < 8:
            return

        lesson_gangs = []
        for g in row[header_order[3]].split(","):
            if g not in gang_list:
                gang_list[g] = Gang(g)
            lesson_gangs.append(gang_list[g])

        lesson = Lesson(dateformat_list,
                        row[header_order[0]],  # Curso
                        row[header_order[1]],  # Unidade de executaçao
                        row[header_order[2]],  # Turno
                        lesson_gangs,  # Turma
                        int(row[header_order[4]]),  # Inscritos no turno
                        row[header_order[5]],  # semana
                        row[header_order[6]],  # duraçao
                        row[header_order[7]])  # caracteristicas

        lesson_list.append(lesson)

        for g in lesson_gangs:
            g.add_lesson(lesson)

    def weekday_to_string(self, weekday: int):
        weekdays = ["Seg", "Ter", "Qua", "Qui", "Sex"]
        return weekdays[weekday]

    def export_schedule_dict_ts_lc(self, dict_ts_lc: dict) -> List[str]:
        """
        Export to a csv file the list of Lesson objects
        :param dict_ts_lc: Dict[TimeSLot -> List[(Lesson, Classroom)]]
        :param file_name: name of the new file
        :return:
        # TS: Week, Weekday, Hour, Minute
        """
        rows = []
        header = "Curso;Unidade de execução;Turno;Turma;Inscritos no turno;Dia da Semana;Início;Fim;Dia;" \
                 "Características da sala pedida para a aula;Sala de aula;Lotação;Características reais da sala"
        rows.append(header)

        # calculate the day with a function that receives the week, day of the week, starting day of the semester
        semester_starting_day_split = self.semester_starting_day.split("/")
        starting_day_datetime = datetime.strptime(f"{semester_starting_day_split[0]}/{semester_starting_day_split[1]}"
                                                  f"/{semester_starting_day_split[2]}", "%m/%d/%Y")

        for key, value in dict_ts_lc.items():
            week = key.week
            weekday = key.weekday
            hour = key.hour
            minute = key.minute

            # Starting and ending date and hour for all the assignments in this timeslot
            date_lesson_start = self.calculate_day(week, weekday, hour, minute, starting_day_datetime)
            duration_delta = timedelta(hours=1, minutes=30, seconds=0)
            date_lesson_end = date_lesson_start + duration_delta

            for lesson, classroom in value:
                str_to_add = (lesson.course + ";" +
                              lesson.subject + ";" +
                              lesson.shift + ";" +
                              self.list_to_comma_sep_string(lesson.gang_list) + ";" +
                              self.weekday_to_string(weekday) + ";" +
                              date_lesson_start.strftime("%H:%M:%S") + ";" +
                              date_lesson_end.strftime("%H:%M:%S") + ";" +
                              date_lesson_start.strftime("%m/%d/%Y") + ";" +
                              lesson.requested_characteristics + ";")

                if classroom:
                    rows.append(str_to_add +
                                classroom.name + ";" +
                                str(classroom.normal_capacity) + ";" +
                                self.list_to_comma_sep_string(classroom.characteristics)
                                )
                else:
                    rows.append(str_to_add + ";;")

        return rows

    def calculate_day(self, week: int, weekday: int, hour: int, minute: int, starting_day: datetime) -> datetime:
        # starting day must have the format -> mm/dd/yyyy
        # weekday must be int (do this when importing)
        week_to_sum = timedelta(weeks=week)
        actual_date = week_to_sum + starting_day
        monday = actual_date - timedelta(days=starting_day.weekday())
        actual_date = (monday + timedelta(days=weekday))
        actual_date = actual_date.replace(hour=hour, minute=minute)
        return actual_date


if __name__ == "__main__":
    mp = Manipulate_Documents("05/31/2022")
    semester_starting_day_list = mp.semester_starting_day.split("/")
    starting_day = datetime.strptime(f"{semester_starting_day_list[0]}/{semester_starting_day_list[1]}"
                                     f"/{semester_starting_day_list[2]}", "%m/%d/%Y")

    print(mp.calculate_day(2, 0, 12, 0, starting_day))
