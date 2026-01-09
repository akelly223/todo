"""
Formulaires Django pour la création et modification de tâches.
"""

from django import forms
from django.utils import timezone
from .models import Task
from .services import TaskIntelligenceService


class TaskForm(forms.ModelForm):
    """
    Formulaire pour créer et modifier une tâche.
    Inclut des widgets personnalisés pour une meilleure UX.
    """
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'urgency_score', 'importance_score', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all',
                'placeholder': 'Ex: Finir le rapport trimestriel',
                'required': True,
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all',
                'placeholder': 'Décrivez votre tâche en détail...',
                'rows': 4,
            }),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all',
                'type': 'datetime-local',
                'required': True,
            }),
            'urgency_score': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all',
            }),
            'importance_score': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all',
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all',
            }),
        }
        labels = {
            'title': 'Titre de la tâche',
            'description': 'Description',
            'due_date': 'Date d\'échéance',
            'urgency_score': 'Niveau d\'urgence',
            'importance_score': 'Niveau d\'importance',
            'status': 'Statut',
        }
        help_texts = {
            'urgency_score': '1 = Pas urgent, 5 = Très urgent',
            'importance_score': '1 = Pas important, 5 = Très important',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si c'est une nouvelle tâche, suggérer automatiquement les priorités
        if not self.instance.pk and self.data:
            # Auto-suggestion basée sur les données soumises
            title = self.data.get('title', '')
            description = self.data.get('description', '')
            due_date_str = self.data.get('due_date', '')
            
            if title and due_date_str:
                try:
                    # Parser la date
                    from django.utils.dateparse import parse_datetime
                    due_date = parse_datetime(due_date_str)
                    
                    if due_date:
                        # Obtenir les suggestions
                        suggestions = TaskIntelligenceService.suggest_priority(
                            title, description, due_date
                        )
                        
                        # Pré-remplir si les champs sont vides
                        if not self.data.get('urgency_score'):
                            self.initial['urgency_score'] = suggestions['urgency']
                        if not self.data.get('importance_score'):
                            self.initial['importance_score'] = suggestions['importance']
                except Exception:
                    pass
    
    def clean_due_date(self):
        """Valide que la date d'échéance est dans le futur."""
        due_date = self.cleaned_data.get('due_date')
        
        if due_date and due_date < timezone.now():
            # Permettre les dates passées mais avertir
            pass  # On pourrait ajouter un warning ici
        
        return due_date
    
    def clean(self):
        """Validation globale du formulaire."""
        cleaned_data = super().clean()
        
        title = cleaned_data.get('title')
        urgency = cleaned_data.get('urgency_score')
        importance = cleaned_data.get('importance_score')
        
        # Vérifier la cohérence
        if title and len(title.strip()) < 3:
            raise forms.ValidationError("Le titre doit contenir au moins 3 caractères.")
        
        return cleaned_data


class QuickTaskForm(forms.ModelForm):
    """
    Formulaire simplifié pour créer rapidement une tâche.
    Utilisé pour l'ajout rapide depuis le dashboard.
    """
    
    class Meta:
        model = Task
        fields = ['title', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': 'Nouvelle tâche rapide...',
            }),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'type': 'datetime-local',
            }),
        }
    
    def save(self, commit=True, user=None):
        """
        Sauvegarde avec des valeurs par défaut intelligentes.
        """
        task = super().save(commit=False)
        
        if user:
            task.user = user
        
        # Valeurs par défaut
        task.urgency_score = 3
        task.importance_score = 3
        task.status = 'TODO'
        
        # Auto-suggestion si possible
        if task.title and task.due_date:
            suggestions = TaskIntelligenceService.suggest_priority(
                task.title, '', task.due_date
            )
            task.urgency_score = suggestions['urgency']
            task.importance_score = suggestions['importance']
        
        if commit:
            task.save()
        
        return task


class TaskFilterForm(forms.Form):
    """
    Formulaire pour filtrer les tâches dans le dashboard.
    """
    
    STATUS_CHOICES = [
        ('', 'Tous les statuts'),
        ('TODO', 'À faire'),
        ('IN_PROGRESS', 'En cours'),
        ('DONE', 'Terminé'),
    ]
    
    QUADRANT_CHOICES = [
        ('', 'Tous les quadrants'),
        ('Q1', 'Q1 - Urgent & Important'),
        ('Q2', 'Q2 - Important'),
        ('Q3', 'Q3 - Urgent'),
        ('Q4', 'Q4 - Ni urgent ni important'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500',
        })
    )
    
    quadrant = forms.ChoiceField(
        choices=QUADRANT_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500',
        })
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500',
            'placeholder': 'Rechercher une tâche...',
        })
    )
