import time

from alocate.Progress import Progress
from alocate.overbooking_with_jmp_algorithm import overbooking_with_jmp_algorithm
from alocate.simple_allocation import simple_allocation
from alocate.weekly_allocation import weekly_allocation
from file_manager.Manipulate_Documents import *

from metrics.Metric import Gaps, UsedRooms, RoomlessLessons, Overbooking, Underbooking, BadClassroom, RoomMovements, \
    BuildingMovements, ClassroomInconsistency
from django.shortcuts import render

from django.http import HttpResponse, Http404
from django.http import JsonResponse
import json

import copy

global schedule_simple
global schedule_overbooking
global progress

def index(request):
    return render(request, 'index.html')


# This might not be needed but it's a placeholder
#def loading(request):
#    form = UploadForm(request.POST or None, request.FILES or None)
#    if request.is_ajax():
#        if form.is_valid():
#            form.save()
#            return JsonResponse({'message': 'hell yeah'})
#    context = {
#        'form': form,
#    }
#    return render(request, 'uploads/main.html', context)

def progress_bar(request):
    if request.method == 'GET':
        global progress
        percent = progress.get_progress()
        #print("Progress: ", percent, "%")
        return JsonResponse({'percent':str(round(percent, 1)), 'error':'0'})
    else:
        print("\nNot get, kinda weird\n")
        return JsonResponse({'percent':'0', 'error':'1'})

def results(request):
    if request.method == 'POST' and request.FILES['filename']:
        global progress
        progress = Progress()
        print(progress.get_progress(), "% view")
        mp = Manipulate_Documents()
        myFile = request.FILES['filename']
        myFile.seek(0)
        schedule = mp.import_schedule_documents(myFile, False)
        metrics_chosen = request.POST.getlist('metrics')
        metrics = []
        metrics_jmp_compatible = []
        for metric in metrics_chosen:
            if metric == "RoomlessLessons":
                metrics.append(RoomlessLessons())
                metrics_jmp_compatible.append(RoomlessLessons())
            if metric == "Overbooking":
                metrics.append(Overbooking())
                metrics_jmp_compatible.append(Overbooking())
            if metric == "Underbooking":
                metrics.append(Underbooking())
                metrics_jmp_compatible.append(Underbooking())
            if metric == "BadClassroom":
                metrics.append(BadClassroom())
                metrics_jmp_compatible.append(BadClassroom())
            if metric == "Gaps":
                metrics.append(Gaps())
            if metric == "RoomMovements":
                metrics.append(RoomMovements())
            if metric == "BuildingMovements":
                metrics.append(BuildingMovements())
            if metric == "UsedRooms":
                metrics.append(UsedRooms())
            if metric == "ClassroomInconsistency":
                metrics.append(ClassroomInconsistency())

        classrooms = mp.import_classrooms()

        c_copy = copy.deepcopy(classrooms)

        s_copy = copy.deepcopy(schedule)

        a_simple = simple_allocation(s_copy, c_copy, progress)

        c_copy = copy.deepcopy(classrooms)
        s_copy = copy.deepcopy(schedule)
        a_weekly = weekly_allocation(s_copy, c_copy, progress)

        start = time.time()
        c_copy = copy.deepcopy(classrooms)
        s_copy = copy.deepcopy(schedule)
        print("TIME FOR DEEP COPY: ", time.time() - start)

        if not request.POST.get("Overbooking_max"):
            a_jmp = overbooking_with_jmp_algorithm(s_copy, c_copy, metrics_jmp_compatible, progress)
        else:
            a_jmp = overbooking_with_jmp_algorithm( s_copy, c_copy, metrics_jmp_compatible, progress, int(request.POST.get("Overbooking_max")))


        progress.set_total_tasks_metrics(len(metrics)*3)

        results_metrics = {"Metric":[],"Algorithm - Simple":[],"Algorithm - Weekly":[], "Algorithm - Overbooking": []};
        for m in metrics:
            m.calculate(a_simple)
            #print(m.name, ": ", round(m.get_percentage() * 100, 2), "%")
            results_metrics["Metric"].append(m.name)
            results_metrics["Algorithm - Simple"].append(str(round(m.get_percentage() * 100, 2)) + "%")
            m.reset_metric()
            progress.inc_cur_tasks_metrics()


        schedule_andre = []
        for sublist in a_weekly.values():
            for item in sublist:
                schedule_andre.append(item)

        for m in metrics:
            m.calculate(schedule_andre)
            results_metrics["Metric"].append(m.name)
            results_metrics["Algorithm - Weekly"].append(str(round(m.get_percentage() * 100, 2)) + "%")
            m.reset_metric()
            progress.inc_cur_tasks_metrics()
 

        schedule_nuno = []
        for sublist in a_jmp.values():
            for item in sublist:
                schedule_nuno.append(item)

        for m in metrics:
            m.calculate(schedule_nuno)
            results_metrics["Metric"].append(m.name)
            results_metrics["Algorithm - Overbooking"].append(str(round(m.get_percentage() * 100, 2)) + "%")
            m.reset_metric()
            progress.inc_cur_tasks_metrics()

        iterator = len(results_metrics["Algorithm - Simple"])
        i = 0
        final_dict = []
        while i < iterator:
            tmp_dict = {}
            for key, values in results_metrics.items():
                #print(tmp_dict[key], "inside for", values[i])
                try:
                    tmp_dict[key] = values[i]
                except Exception:
                   print("didn't insert the value")

            final_dict.append(tmp_dict)
            i+=1
        results_metrics = final_dict

        #a_simple represents the schedule from the simple algorithm
        #schedule_nuno represents the schedule from the overbooking algorithm
        global schedule_simple
        global schedule_overbooking
        global schedule_weekly

        schedule_simple = a_simple
        schedule_overbooking = schedule_nuno
        schedule_weekly = schedule_andre
        # table columns
        headers = {"Metric": "Metrics", "Algorithm - Simple": "Algorithm - Simple", "Algorithm - Weekly": "Algorith - Weekly", "Algorithm - Overbooking": "Algorithm - Overbooking"}

        # content of evaluation table
        context = [{"Metric": "1", "Algorithm - 1": "97.5%", "Algorithm - 2": "50%"},
                   {"Metric": "2", "Algorithm - 1": "10.5%", "Algorithm - 2": "99.7%"}]
        context = json.dumps(context)
        results_metrics = json.dumps(results_metrics)
        # content of all algorithms to show on page, append to render
        return render(request, 'results.html', {"context": context, "table_headers": headers, "results_metrics": results_metrics})

    return render(request, 'index.html')

def download_file(request):
    # fill these variables with real values
    # fl_path = "Output_Documents/"
    # filename = 'Output_Schedule.csv'
    global schedule_simple
    global schedule_overbooking
    global schedule_weekly

    if request.method == 'POST':
        if request.POST.get("algorithm") == "simple_algorithm":
            lines = Manipulate_Documents().export_schedule_str(schedule_simple)
        if request.POST.get("algorithm") == "weekly_algorithm":
            lines = Manipulate_Documents().export_schedule_str(schedule_weekly)
        if request.POST.get("algorithm") == "overbooking_algorithm":
            lines = Manipulate_Documents().export_schedule_str(schedule_overbooking)
        response = HttpResponse(content_type='text/csv')
        response['Content-Type'] = 'text/csv'
        response['Content-Disposition'] = 'attachment; filename=Algorithm_Results.csv'

        content = ""
        for x in lines:
            content += x + "\n"
        response.writelines(content)

    return response