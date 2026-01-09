"""
Services pour la logique métier intelligente de l'application.
Contient les algorithmes de priorisation et de recommandation.
"""

from django.utils import timezone
from datetime import timedelta
from .models import Task, TaskStatistics


class TaskIntelligenceService:
    """
    Service pour les fonctionnalités intelligentes de gestion de tâches.
    """
    
    @staticmethod
    def suggest_priority(title, description, due_date):
        """
        Suggère automatiquement les niveaux d'urgence et d'importance
        basés sur le contenu de la tâche et la date d'échéance.
        
        Args:
            title (str): Titre de la tâche
            description (str): Description de la tâche
            due_date (datetime): Date d'échéance
        
        Returns:
            dict: {'urgency': int, 'importance': int}
        """
        urgency = 3  # Valeur par défaut
        importance = 3  # Valeur par défaut
        
        # Analyse de l'urgence basée sur la date d'échéance
        time_until_due = (due_date - timezone.now()).total_seconds()
        hours_until_due = time_until_due / 3600
        
        if hours_until_due < 24:
            urgency = 5  # Très urgent
        elif hours_until_due < 72:
            urgency = 4  # Urgent
        elif hours_until_due < 168:  # 1 semaine
            urgency = 3  # Moyennement urgent
        elif hours_until_due < 720:  # 1 mois
            urgency = 2  # Peu urgent
        else:
            urgency = 1  # Pas urgent
        
        # Analyse de l'importance basée sur les mots-clés
        text_to_analyze = f"{title} {description}".lower()
        
        # Mots-clés indiquant une haute importance
        high_importance_keywords = [
            'urgent', 'important', 'critique', 'prioritaire', 'essentiel',
            'client', 'projet', 'deadline', 'livraison', 'présentation',
            'réunion', 'boss', 'direction', 'stratégique'
        ]
        
        # Mots-clés indiquant une faible importance
        low_importance_keywords = [
            'peut-être', 'éventuellement', 'si possible', 'optionnel',
            'bonus', 'nice to have', 'amélioration mineure'
        ]
        
        high_count = sum(1 for keyword in high_importance_keywords if keyword in text_to_analyze)
        low_count = sum(1 for keyword in low_importance_keywords if keyword in text_to_analyze)
        
        if high_count >= 2:
            importance = 5
        elif high_count == 1:
            importance = 4
        elif low_count >= 1:
            importance = 2
        
        return {
            'urgency': urgency,
            'importance': importance
        }
    
    @staticmethod
    def get_tasks_requiring_attention(user):
        """
        Retourne les tâches nécessitant une attention immédiate.
        
        Critères :
        - Tâches en retard
        - Tâches dues dans les 24h
        - Tâches Q1 non commencées
        
        Args:
            user: L'utilisateur Django
        
        Returns:
            QuerySet: Tâches nécessitant attention
        """
        now = timezone.now()
        tomorrow = now + timedelta(hours=24)
        
        tasks = Task.objects.filter(user=user).exclude(status='DONE')
        
        # Tâches en retard ou dues bientôt
        urgent_tasks = tasks.filter(
            due_date__lte=tomorrow
        ) | tasks.filter(quadrant='Q1')
        
        return urgent_tasks.distinct().order_by('due_date')
    
    @staticmethod
    def get_productivity_insights(user):
        """
        Génère des insights sur la productivité de l'utilisateur.
        
        Args:
            user: L'utilisateur Django
        
        Returns:
            dict: Insights et recommandations
        """
        stats, created = TaskStatistics.objects.get_or_create(user=user)
        
        if created or stats.total_tasks_created == 0:
            stats.update_statistics()
        
        tasks = Task.objects.filter(user=user)
        active_tasks = tasks.exclude(status='DONE')
        
        # Analyse de la distribution des tâches
        q1_count = active_tasks.filter(quadrant='Q1').count()
        q2_count = active_tasks.filter(quadrant='Q2').count()
        q3_count = active_tasks.filter(quadrant='Q3').count()
        q4_count = active_tasks.filter(quadrant='Q4').count()
        
        insights = {
            'completion_rate': stats.completion_rate,
            'total_active': active_tasks.count(),
            'quadrant_distribution': {
                'Q1': q1_count,
                'Q2': q2_count,
                'Q3': q3_count,
                'Q4': q4_count,
            },
            'recommendations': []
        }
        
        # Génération de recommandations
        if q1_count > 5:
            insights['recommendations'].append({
                'type': 'warning',
                'message': f"⚠️ Vous avez {q1_count} tâches urgentes et importantes. Concentrez-vous sur Q1 !"
            })
        
        if q4_count > 10:
            insights['recommendations'].append({
                'type': 'info',
                'message': f"💡 Vous avez {q4_count} tâches dans Q4. Envisagez de les éliminer pour vous concentrer sur l'essentiel."
            })
        
        if q2_count > 0 and q1_count == 0:
            insights['recommendations'].append({
                'type': 'success',
                'message': "✅ Excellent ! Vous êtes proactif. Continuez à planifier vos tâches importantes."
            })
        
        if stats.completion_rate > 80:
            insights['recommendations'].append({
                'type': 'success',
                'message': f"🎉 Bravo ! Vous avez un taux de complétion de {stats.completion_rate}% !"
            })
        elif stats.completion_rate < 30:
            insights['recommendations'].append({
                'type': 'warning',
                'message': "📉 Votre taux de complétion est faible. Essayez de vous concentrer sur moins de tâches à la fois."
            })
        
        return insights
    
    @staticmethod
    def get_next_recommended_task(user):
        """
        Recommande la prochaine tâche à accomplir selon un algorithme intelligent.
        
        Priorité :
        1. Tâches Q1 en retard
        2. Tâches Q1 dues aujourd'hui
        3. Tâches Q1 avec le score de priorité le plus élevé
        4. Tâches Q2 avec le score de priorité le plus élevé
        
        Args:
            user: L'utilisateur Django
        
        Returns:
            Task ou None: La tâche recommandée
        """
        now = timezone.now()
        active_tasks = Task.objects.filter(user=user).exclude(status='DONE')
        
        # 1. Tâches en retard dans Q1
        overdue_q1 = active_tasks.filter(
            quadrant='Q1',
            due_date__lt=now
        ).order_by('due_date').first()
        
        if overdue_q1:
            return overdue_q1
        
        # 2. Tâches Q1 dues aujourd'hui
        end_of_day = now.replace(hour=23, minute=59, second=59)
        today_q1 = active_tasks.filter(
            quadrant='Q1',
            due_date__lte=end_of_day
        ).order_by('due_date').first()
        
        if today_q1:
            return today_q1
        
        # 3. Tâches Q1 par score de priorité
        q1_tasks = active_tasks.filter(quadrant='Q1')
        if q1_tasks.exists():
            return max(q1_tasks, key=lambda t: t.get_priority_score())
        
        # 4. Tâches Q2 par score de priorité
        q2_tasks = active_tasks.filter(quadrant='Q2')
        if q2_tasks.exists():
            return max(q2_tasks, key=lambda t: t.get_priority_score())
        
        # 5. Sinon, n'importe quelle tâche active
        return active_tasks.order_by('-importance_score', '-urgency_score').first()
    
    @staticmethod
    def check_and_send_alerts(user):
        """
        Vérifie les tâches nécessitant des alertes.
        
        Retourne une liste d'alertes à afficher à l'utilisateur.
        
        Args:
            user: L'utilisateur Django
        
        Returns:
            list: Liste de dictionnaires avec les alertes
        """
        alerts = []
        now = timezone.now()
        
        tasks = Task.objects.filter(user=user).exclude(status='DONE')
        
        # Alerte pour tâches en retard
        overdue_tasks = tasks.filter(due_date__lt=now)
        if overdue_tasks.exists():
            alerts.append({
                'type': 'danger',
                'icon': '🚨',
                'message': f"Vous avez {overdue_tasks.count()} tâche(s) en retard !",
                'tasks': list(overdue_tasks[:3])  # Limite à 3 pour l'affichage
            })
        
        # Alerte pour tâches dues dans les 24h
        tomorrow = now + timedelta(hours=24)
        due_soon = tasks.filter(due_date__gte=now, due_date__lte=tomorrow)
        if due_soon.exists():
            alerts.append({
                'type': 'warning',
                'icon': '⏰',
                'message': f"{due_soon.count()} tâche(s) due(s) dans les 24 heures",
                'tasks': list(due_soon[:3])
            })
        
        # Alerte pour tâches importantes devenant urgentes
        # (Q2 qui devrait passer en Q1)
        q2_becoming_urgent = tasks.filter(
            quadrant='Q2',
            due_date__lte=now + timedelta(days=2)
        )
        if q2_becoming_urgent.exists():
            alerts.append({
                'type': 'info',
                'icon': '📢',
                'message': f"{q2_becoming_urgent.count()} tâche(s) importante(s) deviennent urgentes",
                'tasks': list(q2_becoming_urgent[:3])
            })
        
        return alerts
