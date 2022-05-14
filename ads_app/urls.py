from django.urls import path

from . import views

urlpatterns = [
    path('ads_app/', views.index, name='index'),
    path('', views.index, name='index'),
    path('data', views.data, name='data'),
    path('data.html', views.data, name='data'),
    path('results', views.results, name='results'),
    path('results.html', views.results, name='results'),
    path("download_file", views.download_file, name='download_file'),
    path('progress_bar', views.progress_bar, name='progress_bar')
]