"""
URLs pour l'application tasks.
"""

from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard, name='dashboard'),
    
    # CRUD des tâches
    path('create/', views.task_create, name='task_create'),
    path('quick-create/', views.task_quick_create, name='task_quick_create'),
    path('<int:pk>/update/', views.task_update, name='task_update'),
    path('<int:pk>/delete/', views.task_delete, name='task_delete'),
    
    # Actions AJAX
    path('<int:pk>/toggle-status/', views.task_toggle_status, name='task_toggle_status'),
    path('<int:pk>/update-quadrant/', views.task_update_quadrant, name='task_update_quadrant'),
    
    # Statistiques
    path('statistics/', views.statistics, name='statistics'),
]
