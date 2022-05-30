import mimetypes
from os import read
import sys

from django.shortcuts import render
from operator import itemgetter
# from cytoolz import take


from django.http import HttpResponse, FileResponse
import time

from NovoAlgoritmo import novo_algoritmo
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
global mp
global dict_lessons_30


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
    pass
    # if request.method == 'GET':
    #     global progress
    #     percent = progress.get_progress()
    #     # print("Progress: ", percent, "%")
    #     return JsonResponse({'percent': str(round(percent, 1)), 'error': '0'})
    # else:
    #     print("\nNot get, kinda weird\n")
    #     return JsonResponse({'percent': '0', 'error': '1'})


def lessons_to_lessons30(lesson_list):
    dict_lesson30 = {}
    for lesson in lesson_list:
        if lesson.assignment[1] in dict_lesson30.keys():
            dict_lesson30[lesson.assignment[1]].append((lesson, lesson.assignment[0]))
        else:
            dict_lesson30[lesson.assignment[1]] = [(lesson, lesson.assignment[0])]
    return dict_lesson30

def show_metrics_results(gangs, lessons, metrics):
    # Determine Mémétrics:

    # Make dict with lesson, timeslot and classroom
    lesson_timeslot_classroom_dict = {lesson: (lesson.assignment[1], lesson.assignment[0]) for lesson in lessons}

    # Make tuple with both dicts
    tuple_dicts = (gangs, lesson_timeslot_classroom_dict)

    # Evaluate metrics for the entire algorithm
    metric_percents = []
    for metric in metrics:
        metric.reset_metric()
        metric.calculate(tuple_dicts)
        metric_percents.append(metric.get_percentage())

    # Print the metrics
    print("")
    print("Objectives:")
    for i in range(len(metric_percents)):
        print(f"{metrics[i].name}- {metric_percents[i]}")


def results(request):
    if request.method == 'POST' and request.FILES['schedulefilename']:
        s_headers = ["Course", "Subject", "Shift", "Class", "Enrolled", "Week", "Duration",
                     "Requested_Char", "Classroom", "Capacity", "Actual_Char"]
        order = []
        for h in s_headers:
            order.append(int(request.POST.get(h)))
        global progress
        progress = Progress()
        global mp
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

        novo_algoritmo(lesson_list, gang_dict, classrooms, metrics)
        global dict_lessons_30
        dict_lessons_30 = lessons_to_lessons30(lesson_list)

        lesson_timeslot_classroom_dict = {lesson: (lesson.assignment[1], lesson.assignment[0]) for lesson in
                                          lesson_list}

        # Make tuple with both dicts
        tuple_dicts = (gang_dict, lesson_timeslot_classroom_dict)

        headers = {"Metric": "Metrics", "Result": "Result"}
        results_metrics = {"Metric": [], "Result": []}
        for metric in metrics:
            metric.reset_metric()
            metric.calculate(tuple_dicts)
            results_metrics["Metric"].append(metric.name)
            results_metrics["Result"].append(str(round(metric.get_percentage() * 100, 2)) + "%")

        iterator = len(metrics)
        i = 0
        final_dict = []
        while i < iterator:
            tmp_dict = {}
            for key, values in results_metrics.items():
                try:
                    tmp_dict[key] = values[i]
                except Exception:
                    print("didn't insert the value")

            final_dict.append(tmp_dict)
            i += 1
        results_metrics = final_dict

        # content of evaluation table
        # context = [{"Metric": "1", "Algorithm - 1": "97.5%", "Algorithm - 2": "50%"},
        #            {"Metric": "2", "Algorithm - 1": "10.5%", "Algorithm - 2": "99.7%"}]
        # context = json.dumps(context)
        # results_metrics = json.dumps(results_metrics)
        # # content of all algorithms to show on page, append to render
        # print(f"headers: {headers}")
        # print(f"results_metrics: {results_metrics}")
        return render(request, 'results.html',
                      {"table_headers": headers, "results_metrics": results_metrics})

    return render(request, 'index.html')


def download_file(request):
    # fill these variables with real values
    # fl_path = "Output_Documents/"
    # filename = 'Output_Schedule.csv'
    global dict_lessons_30
    global mp

    if request.method == 'POST':
        if request.POST.get("b") == "simple_algorithm":
            lines = mp.export_schedule_dict_ts_lc(dict_lessons_30)

    response = HttpResponse(content_type='text/csv')
    response['Content-Type'] = 'text/csv'
    response['Content-Disposition'] = 'attachment; filename=Algorithm_Results.csv'

    content = ""
    for x in lines:
        content += x + "\n"
    response.writelines(content)

    return response
