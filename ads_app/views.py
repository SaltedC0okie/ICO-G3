import mimetypes
from os import read
import sys

from django.shortcuts import render
from operator import itemgetter
# from cytoolz import take


from django.http import HttpResponse, FileResponse
import time
from alocate import Algorithm_Utils
from alocate.ICOModel1Allocation import ico_model1_allocation_whole_schedule
from alocate.Model1Handler import Model1Handler
from alocate.Progress import Progress
from alocate.overbooking_with_jmp_algorithm import overbooking_with_jmp_algorithm
from alocate.simple_allocation import simple_allocation
from alocate.weekly_allocation import weekly_allocation
from file_manager.Manipulate_Documents import *

from metrics.Metric import Gaps, RoomlessLessons, Overbooking, Underbooking, BadClassroom, RoomMovements, \
    BuildingMovements, ClassroomInconsistency, ClassroomCollisions, LessonCollisions, GangLessonVolume, \
    GangLessonDistribution, LessonInconsistency
from django.shortcuts import render
from lesson.Lesson import *

from django.http import HttpResponse, Http404
from django.http import JsonResponse
import json

import copy

global schedule_simple
global schedule_overbooking
global schedule_weekly
global progress


def index(request):
    return render(request, 'index.html')


def data(request):
    request.session["metrics"] = request.POST.getlist('metrics')
    request.session["roomless_max"] = request.POST.get("RoomlessLessons_max")
    request.session["over_max"] = request.POST.get("Overbooking_max")
    request.session["under_max"] = request.POST.get("Underbooking_max")
    request.session["bad_max"] = request.POST.get("BadClassroom_max")

    request.session['starting_day'] = request.POST.get("Semester_starting_day")
    # print(request.FILES['schedulefilename'])
    # request.session['schedulefile'] = request.FILES['schedulefilename']
    # print(request.session['var'])
    # request.FILES[0] = 123

    headers = ["Course", "Subject", "Shift", "Class", "Enrolled", "Week", "Duration",
               "Requested_Char", "Classroom", "Capacity", "Actual_Char"]

    return render(request, 'data.html', {"hlist": headers})


def progress_bar(request):
    if request.method == 'GET':
        global progress
        percent = progress.get_progress()
        # print("Progress: ", percent, "%")
        return JsonResponse({'percent': str(round(percent, 1)), 'error': '0'})
    else:
        print("\nNot get, kinda weird\n")
        return JsonResponse({'percent': '0', 'error': '1'})


def results(request):
    if request.method == 'POST' and request.FILES['schedulefilename']:
        s_headers = ["Course", "Subject", "Shift", "Class", "Enrolled", "Week", "Duration",
                     "Requested_Char", "Classroom", "Capacity", "Actual_Char"]
        order = []
        for h in s_headers:
            order.append(int(request.POST.get(h)))
        global progress
        progress = Progress()
        mp = Manipulate_Documents(request.session["starting_day"])
        mySchedule = request.FILES['schedulefilename']
        mySchedule.seek(0)
        encoding = request.POST.get('encoding')
        dateformat_list = re.split('\W+', request.POST.get('dateformat'))

        lesson_list, gang_dict = mp.import_lessons_and_gangs(mySchedule, order, dateformat_list, encoding)
        metrics_chosen = request.session['metrics']

        values = {}
        for lesson in lesson_list:
            if lesson.week in values.keys():
                values[lesson.week] += 1
            else:
                values[lesson.week] = 1

        busiest_week = max(values, key=values.get)
        busiest_week_lessons = list(filter(lambda l: l.week == busiest_week, lesson_list))

        lesson_list = busiest_week_lessons  # TODO TEMPORÁRIO
        print("HEY I'M HERE   : ", len(lesson_list))

        metrics = []
        for metric in metrics_chosen:
            if metric == "RoomlessLessons":
                metrics.append(RoomlessLessons())
            if metric == "Overbooking":
                metrics.append(Overbooking())
            if metric == "Underbooking":
                metrics.append(Underbooking())
            if metric == "BadClassroom":
                metrics.append(BadClassroom())
            if metric == "Gaps":
                metrics.append(Gaps())
            if metric == "RoomMovements":
                metrics.append(RoomMovements())
            if metric == "BuildingMovements":
                metrics.append(BuildingMovements())
            if metric == "ClassroomInconsistency":
                metrics.append(ClassroomInconsistency())
            if metric == "ClassroomCollisions":
                metrics.append(ClassroomCollisions())
            if metric == "LessonInconsistency":
                metrics.append(LessonInconsistency())
            if metric == "LessonCollisions":
                metrics.append(LessonCollisions())
            if metric == "GangLessonVolume":
                metrics.append(GangLessonVolume())
            if metric == "GangLessonDistribution":
                metrics.append(GangLessonDistribution())

        if 'classroomfilename' in request.FILES:
            myClassroom = request.FILES['classroomfilename']
            myClassroom.seek(0)
            classrooms = mp.import_uploaded_classrooms(request.FILES['classroomfilename'])
        else:
            classrooms = mp.import_classrooms()

        # count = Algorithm_Utils.check_for_collisions(a_jmp)
        #
        # progress.set_total_tasks_metrics(len(metrics)*3-1)
        #
        # schedule_s = []
        # for sublist in a_simple.values():
        #     for item in sublist:
        #         schedule_s.append(item)
        #
        # for m in metrics:
        #     if m.name == "ClassroomCollisions":
        #         m.calculate(a_simple)
        #     else:
        #         m.calculate(schedule_s)
        #     #print(m.name, ": ", round(m.get_percentage() * 100, 2), "%")
        #     results_metrics["Metric"].append(m.name)
        #     results_metrics["Algorithm - Simple"].append(str(round(m.get_percentage() * 100, 2)) + "%")
        #     m.reset_metric()
        #     progress.inc_cur_tasks_metrics()
        #
        # schedule_andre = []
        # for sublist in a_weekly.values():
        #     for item in sublist:
        #         schedule_andre.append(item)
        #
        # for m in metrics:
        #     if m.name == "ClassroomCollisions":
        #         m.calculate(a_weekly)
        #     else:
        #         m.calculate(schedule_andre)
        #     results_metrics["Metric"].append(m.name)
        #     results_metrics["Algorithm - Weekly"].append(str(round(m.get_percentage() * 100, 2)) + "%")
        #     m.reset_metric()
        #
        #     progress.inc_cur_tasks_metrics()
        #
        # schedule_nuno = []
        # for sublist in a_jmp.values():
        #     for item in sublist:
        #         schedule_nuno.append(item)
        #
        # len_metrics = len(metrics)
        # for i, m in enumerate(metrics):
        #     if m.name == "ClassroomCollisions":
        #         m.calculate(a_jmp)
        #     else:
        #         m.calculate(schedule_nuno)
        #     results_metrics["Metric"].append(m.name)
        #     results_metrics["Algorithm - Overbooking"].append(str(round(m.get_percentage() * 100, 2)) + "%")
        #     m.reset_metric()
        #     if i == len_metrics - 2:
        #         progress.inc_cur_tasks_metrics()
        #     if i != len_metrics - 1:
        #         progress.inc_cur_tasks_metrics()
        #
        # iterator = len(results_metrics["Algorithm - Simple"])
        # i = 0
        # final_dict = []
        # while i < iterator:
        #     tmp_dict = {}
        #     for key, values in results_metrics.items():
        #         # print(tmp_dict[key], "inside for", values[i])
        #         try:
        #             tmp_dict[key] = values[i]
        #         except Exception:
        #             print("didn't insert the value")
        #
        #     final_dict.append(tmp_dict)
        #     i += 1
        # results_metrics = final_dict
        #
        # # a_simple represents the schedule from the simple algorithm
        # # schedule_nuno represents the schedule from the overbooking algorithm
        # global schedule_simple
        # global schedule_overbooking
        # global schedule_weekly
        # schedule_simple = a_simple
        # schedule_overbooking = schedule_nuno
        # schedule_weekly = schedule_andre

        # table columns

        solutions = ico_model1_allocation_whole_schedule(lesson_list, classrooms, gang_dict, metrics)

        # for solution in solutions:
        #     handle_everything = Model1Handler(lessons, self.classrooms, self.gangs, self.num_slots,
        #                                       solution).handle_gangs_everything()
        #     for i, metric in enumerate(self.metrics):
        #         # for j in created_schedule:
        #         #    metric.calculate(j[0], j[1])
        #         metric.calculate(handle_everything)
        #         solution.objectives[i] = metric.get_total_metric_value()
        #         metric.reset_metric()

        headers = {"Metric": "Metrics"}
        results_metrics = {"Metric": []}
        for metric in metrics:
            results_metrics["Metric"].append(metric.name)

        for i in range(len(solutions)):
            headers["solution" + str(i)] = "solution" + str(i)
            results_metrics["solution" + str(i)] = []
            for metric_value in solutions[i].objectives:
                results_metrics["solution" + str(i)].append(str(round(metric_value * 100, 2)) + "%")

        iterator = len(metrics)
        i = 0
        final_dict = []
        while i < iterator:
            tmp_dict = {}
            for key, values in results_metrics.items():
                # print(tmp_dict[key], "inside for", values[i])
                try:
                    tmp_dict[key] = values[i]
                except Exception:
                    print("didn't insert the value")

            final_dict.append(tmp_dict)
            i += 1
        results_metrics = final_dict

        # content of evaluation table
        context = [{"Metric": "1", "Algorithm - 1": "97.5%", "Algorithm - 2": "50%"},
                   {"Metric": "2", "Algorithm - 1": "10.5%", "Algorithm - 2": "99.7%"}]
        context = json.dumps(context)
        results_metrics = json.dumps(results_metrics)
        # content of all algorithms to show on page, append to render
        print(f"headers: {headers}")
        print(f"results_metrics: {results_metrics}")
        return render(request, 'results.html',
                      {"context": context, "table_headers": headers, "results_metrics": results_metrics})

    return render(request, 'index.html')


def download_file(request):
    # fill these variables with real values
    # fl_path = "Output_Documents/"
    # filename = 'Output_Schedule.csv'
    global schedule_simple
    global schedule_overbooking
    global schedule_weekly

    if request.method == 'POST':
        if request.POST.get("b") == "simple_algorithm":
            lines = Manipulate_Documents().export_schedule_str(schedule_simple)
        if request.POST.get("b") == "weekly_algorithm":
            print("")
            # lines = Manipulate_Documents().export_schedule_str(schedule_weekly)
        if request.POST.get("b") == "overbooking_algorithm":
            lines = Manipulate_Documents().export_schedule_str(schedule_overbooking)

    response = HttpResponse(content_type='text/csv')
    response['Content-Type'] = 'text/csv'
    response['Content-Disposition'] = 'attachment; filename=Algorithm_Results.csv'

    content = ""
    for x in lines:
        content += x + "\n"
    response.writelines(content)

    return response
