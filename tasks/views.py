"""
Vues Django pour l'application de gestion de tâches.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.utils import timezone

from .models import Task, TaskStatistics
from .forms import TaskForm, QuickTaskForm, TaskFilterForm
from .services import TaskIntelligenceService


@login_required
def dashboard(request):
    """
    Vue principale du dashboard avec la matrice d'Eisenhower.
    Affiche les 4 quadrants et les statistiques.
    """
    # Récupérer toutes les tâches de l'utilisateur
    tasks = Task.objects.filter(user=request.user)
    
    # Appliquer les filtres si présents
    filter_form = TaskFilterForm(request.GET)
    if filter_form.is_valid():
        status = filter_form.cleaned_data.get('status')
        quadrant = filter_form.cleaned_data.get('quadrant')
        search = filter_form.cleaned_data.get('search')
        
        if status:
            tasks = tasks.filter(status=status)
        if quadrant:
            tasks = tasks.filter(quadrant=quadrant)
        if search:
            tasks = tasks.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
    
    # Séparer les tâches par quadrant
    q1_tasks = tasks.filter(quadrant='Q1').exclude(status='DONE').order_by('-urgency_score', 'due_date')
    q2_tasks = tasks.filter(quadrant='Q2').exclude(status='DONE').order_by('-importance_score', 'due_date')
    q3_tasks = tasks.filter(quadrant='Q3').exclude(status='DONE').order_by('due_date')
    q4_tasks = tasks.filter(quadrant='Q4').exclude(status='DONE').order_by('due_date')
    
    # Tâches complétées (pour affichage séparé)
    completed_tasks = tasks.filter(status='DONE').order_by('-updated_at')[:10]
    
    # Obtenir les insights de productivité
    insights = TaskIntelligenceService.get_productivity_insights(request.user)
    
    # Obtenir les alertes
    alerts = TaskIntelligenceService.check_and_send_alerts(request.user)
    
    # Tâche recommandée
    recommended_task = TaskIntelligenceService.get_next_recommended_task(request.user)
    
    # Formulaire pour ajout rapide
    quick_form = QuickTaskForm()
    
    context = {
        'q1_tasks': q1_tasks,
        'q2_tasks': q2_tasks,
        'q3_tasks': q3_tasks,
        'q4_tasks': q4_tasks,
        'completed_tasks': completed_tasks,
        'insights': insights,
        'alerts': alerts,
        'recommended_task': recommended_task,
        'quick_form': quick_form,
        'filter_form': filter_form,
        'total_active': tasks.exclude(status='DONE').count(),
    }
    
    return render(request, 'tasks/dashboard.html', context)


@login_required
def task_create(request):
    """
    Vue pour créer une nouvelle tâche.
    """
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            
            messages.success(
                request, 
                f'✅ Tâche "{task.title}" créée avec succès dans {task.get_quadrant_display()}!'
            )
            
            # Mettre à jour les statistiques
            stats, _ = TaskStatistics.objects.get_or_create(user=request.user)
            stats.update_statistics()
            
            return redirect('tasks:dashboard')
    else:
        form = TaskForm()
    
    context = {
        'form': form,
        'title': 'Créer une nouvelle tâche',
        'button_text': 'Créer la tâche',
    }
    
    return render(request, 'tasks/task_form.html', context)


@login_required
def task_quick_create(request):
    """
    Vue pour créer rapidement une tâche (AJAX).
    """
    if request.method == 'POST':
        form = QuickTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False, user=request.user)
            task.save()
            
            messages.success(request, f'✅ Tâche "{task.title}" ajoutée !')
            
            # Mettre à jour les statistiques
            stats, _ = TaskStatistics.objects.get_or_create(user=request.user)
            stats.update_statistics()
            
            return redirect('tasks:dashboard')
    
    return redirect('tasks:dashboard')


@login_required
def task_update(request, pk):
    """
    Vue pour modifier une tâche existante.
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            
            messages.success(
                request, 
                f'✅ Tâche "{task.title}" mise à jour dans {task.get_quadrant_display()}!'
            )
            
            return redirect('tasks:dashboard')
    else:
        form = TaskForm(instance=task)
    
    context = {
        'form': form,
        'task': task,
        'title': f'Modifier: {task.title}',
        'button_text': 'Enregistrer les modifications',
    }
    
    return render(request, 'tasks/task_form.html', context)


@login_required
def task_delete(request, pk):
    """
    Vue pour supprimer une tâche.
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)
    
    if request.method == 'POST':
        task_title = task.title
        task.delete()
        
        messages.success(request, f'🗑️ Tâche "{task_title}" supprimée.')
        
        # Mettre à jour les statistiques
        stats, _ = TaskStatistics.objects.get_or_create(user=request.user)
        stats.update_statistics()
        
        return redirect('tasks:dashboard')
    
    context = {
        'task': task,
    }
    
    return render(request, 'tasks/task_confirm_delete.html', context)


@login_required
@require_POST
def task_toggle_status(request, pk):
    """
    Vue AJAX pour basculer le statut d'une tâche (TODO <-> DONE).
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)
    
    if task.status == 'DONE':
        task.status = 'TODO'
        message = f'Tâche "{task.title}" marquée comme à faire'
    else:
        task.status = 'DONE'
        message = f'✅ Tâche "{task.title}" complétée !'
    
    task.save()
    
    # Mettre à jour les statistiques
    stats, _ = TaskStatistics.objects.get_or_create(user=request.user)
    stats.update_statistics()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'new_status': task.status,
            'message': message
        })
    
    messages.success(request, message)
    return redirect('tasks:dashboard')


@login_required
@require_POST
def task_update_quadrant(request, pk):
    """
    Vue AJAX pour déplacer une tâche vers un autre quadrant (drag & drop).
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)
    new_quadrant = request.POST.get('quadrant')
    
    if new_quadrant in ['Q1', 'Q2', 'Q3', 'Q4']:
        # Calculer les nouveaux scores basés sur le quadrant cible
        quadrant_scores = {
            'Q1': {'urgency': 5, 'importance': 5},
            'Q2': {'urgency': 2, 'importance': 5},
            'Q3': {'urgency': 5, 'importance': 2},
            'Q4': {'urgency': 2, 'importance': 2},
        }
        
        scores = quadrant_scores[new_quadrant]
        task.urgency_score = scores['urgency']
        task.importance_score = scores['importance']
        task.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'new_quadrant': task.quadrant,
                'message': f'Tâche déplacée vers {task.get_quadrant_display()}'
            })
    
    return JsonResponse({'success': False}, status=400)


@login_required
def statistics(request):
    """
    Vue pour afficher les statistiques détaillées de productivité.
    """
    stats, _ = TaskStatistics.objects.get_or_create(user=request.user)
    stats.update_statistics()
    
    tasks = Task.objects.filter(user=request.user)
    
    # Statistiques par quadrant
    quadrant_stats = {
        'Q1': {
            'total': tasks.filter(quadrant='Q1').count(),
            'completed': tasks.filter(quadrant='Q1', status='DONE').count(),
            'active': tasks.filter(quadrant='Q1').exclude(status='DONE').count(),
        },
        'Q2': {
            'total': tasks.filter(quadrant='Q2').count(),
            'completed': tasks.filter(quadrant='Q2', status='DONE').count(),
            'active': tasks.filter(quadrant='Q2').exclude(status='DONE').count(),
        },
        'Q3': {
            'total': tasks.filter(quadrant='Q3').count(),
            'completed': tasks.filter(quadrant='Q3', status='DONE').count(),
            'active': tasks.filter(quadrant='Q3').exclude(status='DONE').count(),
        },
        'Q4': {
            'total': tasks.filter(quadrant='Q4').count(),
            'completed': tasks.filter(quadrant='Q4', status='DONE').count(),
            'active': tasks.filter(quadrant='Q4').exclude(status='DONE').count(),
        },
    }
    
    # Insights
    insights = TaskIntelligenceService.get_productivity_insights(request.user)
    
    context = {
        'stats': stats,
        'quadrant_stats': quadrant_stats,
        'insights': insights,
    }
    
    return render(request, 'tasks/statistics.html', context)
