from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta


class Task(models.Model):
    """
    Modèle représentant une tâche dans la matrice d'Eisenhower.
    
    Chaque tâche est automatiquement classée dans un quadrant selon
    son niveau d'urgence et d'importance.
    """
    
    # Choix pour le statut de la tâche
    STATUS_CHOICES = [
        ('TODO', 'À faire'),
        ('IN_PROGRESS', 'En cours'),
        ('DONE', 'Terminé'),
    ]
    
    # Choix pour les quadrants (calculés automatiquement)
    QUADRANT_CHOICES = [
        ('Q1', 'Urgent & Important - À FAIRE MAINTENANT'),
        ('Q2', 'Important mais pas urgent - À PLANIFIER'),
        ('Q3', 'Urgent mais pas important - À DÉLÉGUER'),
        ('Q4', 'Ni urgent ni important - À ÉLIMINER'),
    ]
    
    # Champs de base
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='tasks',
        verbose_name='Utilisateur'
    )
    title = models.CharField(
        max_length=200, 
        verbose_name='Titre'
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name='Description'
    )
    
    # Dates
    due_date = models.DateTimeField(
        verbose_name='Date d\'échéance',
        help_text='Date limite pour accomplir cette tâche'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Créé le'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Modifié le'
    )
    
    # Scores de priorité (1-5)
    urgency_score = models.IntegerField(
        default=3,
        choices=[(i, i) for i in range(1, 6)],
        verbose_name='Niveau d\'urgence',
        help_text='1 = Pas urgent, 5 = Très urgent'
    )
    importance_score = models.IntegerField(
        default=3,
        choices=[(i, i) for i in range(1, 6)],
        verbose_name='Niveau d\'importance',
        help_text='1 = Pas important, 5 = Très important'
    )
    
    # Statut et quadrant
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='TODO',
        verbose_name='Statut'
    )
    quadrant = models.CharField(
        max_length=2,
        choices=QUADRANT_CHOICES,
        default='Q2',
        editable=False,
        verbose_name='Quadrant'
    )
    
    # Ordre pour le drag & drop
    order = models.IntegerField(
        default=0,
        verbose_name='Ordre d\'affichage'
    )
    
    class Meta:
        ordering = ['-importance_score', '-urgency_score', 'due_date']
        verbose_name = 'Tâche'
        verbose_name_plural = 'Tâches'
        indexes = [
            models.Index(fields=['user', 'quadrant', 'status']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_quadrant_display()})"
    
    def save(self, *args, **kwargs):
        """
        Surcharge de la méthode save pour calculer automatiquement
        le quadrant selon les scores d'urgence et d'importance.
        """
        self.quadrant = self.calculate_quadrant()
        super().save(*args, **kwargs)
    
    def calculate_quadrant(self):
        """
        Calcule le quadrant de la tâche selon la matrice d'Eisenhower.
        
        Logique :
        - Q1 : Urgence >= 4 ET Importance >= 4 (DO NOW)
        - Q2 : Urgence < 4 ET Importance >= 4 (SCHEDULE)
        - Q3 : Urgence >= 4 ET Importance < 4 (DELEGATE)
        - Q4 : Urgence < 4 ET Importance < 4 (ELIMINATE)
        """
        if self.urgency_score >= 4 and self.importance_score >= 4:
            return 'Q1'
        elif self.urgency_score < 4 and self.importance_score >= 4:
            return 'Q2'
        elif self.urgency_score >= 4 and self.importance_score < 4:
            return 'Q3'
        else:
            return 'Q4'
    
    @property
    def is_overdue(self):
        """Vérifie si la tâche est en retard."""
        return self.due_date < timezone.now() and self.status != 'DONE'
    
    @property
    def is_due_soon(self):
        """Vérifie si la tâche est due dans les 24 heures."""
        time_until_due = self.due_date - timezone.now()
        return timedelta(0) < time_until_due < timedelta(hours=24)
    
    @property
    def urgency_level_display(self):
        """Retourne un label visuel pour le niveau d'urgence."""
        levels = {
            1: 'Très faible',
            2: 'Faible',
            3: 'Moyen',
            4: 'Élevé',
            5: 'Critique'
        }
        return levels.get(self.urgency_score, 'Non défini')
    
    @property
    def importance_level_display(self):
        """Retourne un label visuel pour le niveau d'importance."""
        levels = {
            1: 'Très faible',
            2: 'Faible',
            3: 'Moyen',
            4: 'Élevé',
            5: 'Critique'
        }
        return levels.get(self.importance_score, 'Non défini')
    
    @property
    def recommendation(self):
        """
        Retourne une recommandation d'action selon le quadrant.
        """
        recommendations = {
            'Q1': 'À FAIRE MAINTENANT - Priorité absolue !',
            'Q2': 'À PLANIFIER - Bloquez du temps dans votre agenda',
            'Q3': 'À DÉLÉGUER - Peut-être confier à quelqu\'un d\'autre ?',
            'Q4': 'À ÉLIMINER - Est-ce vraiment nécessaire ?'
        }
        return recommendations.get(self.quadrant, 'Aucune recommandation')
    
    def get_priority_score(self):
        """
        Calcule un score de priorité global (0-100).
        Utilisé pour le tri intelligent des tâches.
        """
        # Score basé sur urgence et importance
        base_score = (self.urgency_score * 10) + (self.importance_score * 10)
        
        # Bonus si la date d'échéance est proche
        time_until_due = (self.due_date - timezone.now()).total_seconds()
        if time_until_due < 86400:  # Moins de 24h
            base_score += 20
        elif time_until_due < 259200:  # Moins de 3 jours
            base_score += 10
        
        return min(base_score, 100)


class TaskStatistics(models.Model):
    """
    Modèle pour stocker les statistiques de productivité par utilisateur.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='task_statistics'
    )
    
    # Compteurs par quadrant
    q1_completed = models.IntegerField(default=0, verbose_name='Q1 complétées')
    q2_completed = models.IntegerField(default=0, verbose_name='Q2 complétées')
    q3_completed = models.IntegerField(default=0, verbose_name='Q3 complétées')
    q4_completed = models.IntegerField(default=0, verbose_name='Q4 complétées')
    
    # Statistiques générales
    total_tasks_created = models.IntegerField(default=0, verbose_name='Total créées')
    total_tasks_completed = models.IntegerField(default=0, verbose_name='Total complétées')
    
    # Dates
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Statistique'
        verbose_name_plural = 'Statistiques'
    
    def __str__(self):
        return f"Stats de {self.user.username}"
    
    @property
    def completion_rate(self):
        """Calcule le taux de complétion en pourcentage."""
        if self.total_tasks_created == 0:
            return 0
        return round((self.total_tasks_completed / self.total_tasks_created) * 100, 1)
    
    def update_statistics(self):
        """Met à jour les statistiques basées sur les tâches de l'utilisateur."""
        tasks = Task.objects.filter(user=self.user)
        
        self.total_tasks_created = tasks.count()
        self.total_tasks_completed = tasks.filter(status='DONE').count()
        
        self.q1_completed = tasks.filter(quadrant='Q1', status='DONE').count()
        self.q2_completed = tasks.filter(quadrant='Q2', status='DONE').count()
        self.q3_completed = tasks.filter(quadrant='Q3', status='DONE').count()
        self.q4_completed = tasks.filter(quadrant='Q4', status='DONE').count()
        
        self.save()
