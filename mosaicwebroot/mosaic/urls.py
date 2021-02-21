from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<mosaic_name>/', views.mosaic_view, name = 'mosaic_view'),
]