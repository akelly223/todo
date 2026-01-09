"""
Configuration de l'interface d'administration Django pour les tâches.
"""

from django.contrib import admin
from .models import Task, TaskStatistics


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Interface d'administration pour les tâches.
    """
    list_display = ['title', 'user', 'quadrant', 'status', 'urgency_score', 'importance_score', 'due_date', 'created_at']
    list_filter = ['quadrant', 'status', 'urgency_score', 'importance_score', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['quadrant', 'created_at', 'updated_at']
    date_hierarchy = 'due_date'
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('user', 'title', 'description')
        }),
        ('Priorités', {
            'fields': ('urgency_score', 'importance_score', 'quadrant')
        }),
        ('Dates', {
            'fields': ('due_date', 'status', 'created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        """Optimise les requêtes avec select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(TaskStatistics)
class TaskStatisticsAdmin(admin.ModelAdmin):
    """
    Interface d'administration pour les statistiques.
    """
    list_display = ['user', 'total_tasks_created', 'total_tasks_completed', 'completion_rate', 'last_updated']
    readonly_fields = ['q1_completed', 'q2_completed', 'q3_completed', 'q4_completed', 
                       'total_tasks_created', 'total_tasks_completed', 'last_updated']
    search_fields = ['user__username']
    
    def completion_rate(self, obj):
        """Affiche le taux de complétion."""
        return f"{obj.completion_rate}%"
    completion_rate.short_description = 'Taux de complétion'
