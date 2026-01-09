# 📊 DOCUMENTATION TECHNIQUE - Eisenhower TODO

## 🏗️ Architecture du Projet

### Vue d'ensemble

Eisenhower TODO est une application web Django moderne qui implémente la matrice d'Eisenhower pour la gestion intelligente des tâches. L'application classe automatiquement les tâches en 4 quadrants selon leur urgence et importance.

### Stack Technique

- **Backend**: Django 6.0
- **Base de données**: MySQL (via WampServer)
- **Frontend**: Django Templates + Tailwind CSS (CDN)
- **Authentification**: Django Auth System
- **Architecture**: MVC (Model-View-Controller)

## 📁 Structure du Projet

```
eisenhower_todo/
├── config/                      # Configuration Django
│   ├── settings.py             # Paramètres (DB, apps, middleware)
│   ├── urls.py                 # URLs principales
│   └── wsgi.py                 # WSGI pour déploiement
│
├── tasks/                       # Application principale
│   ├── models.py               # Task, TaskStatistics
│   ├── views.py                # Dashboard, CRUD, statistiques
│   ├── forms.py                # TaskForm, QuickTaskForm
│   ├── services.py             # Logique métier intelligente
│   ├── urls.py                 # Routes de l'app
│   └── admin.py                # Interface admin
│
├── users/                       # Gestion utilisateurs
│   ├── views.py                # Login, Register, Logout
│   └── urls.py                 # Routes auth
│
├── templates/                   # Templates HTML
│   ├── base.html               # Template de base
│   ├── tasks/
│   │   ├── dashboard.html      # Vue principale (4 quadrants)
│   │   ├── task_form.html      # Création/modification
│   │   ├── task_confirm_delete.html
│   │   ├── statistics.html     # Statistiques détaillées
│   │   └── components/
│   │       └── task_card.html  # Composant réutilisable
│   └── users/
│       ├── login.html
│       └── register.html
│
├── static/                      # Fichiers statiques
│   ├── css/
│   ├── js/
│   └── images/
│
├── manage.py                    # CLI Django
├── requirements.txt             # Dépendances Python
├── .env                         # Variables d'environnement
├── .gitignore                   # Exclusions Git
├── README.md                    # Documentation utilisateur
├── INSTALLATION.md              # Guide d'installation
└── setup_database.sql           # Script SQL initial
```

## 🗄️ Modèles de Données

### Task (Tâche)

**Champs principaux:**
- `user` (ForeignKey) - Utilisateur propriétaire
- `title` (CharField) - Titre de la tâche
- `description` (TextField) - Description détaillée
- `due_date` (DateTimeField) - Date d'échéance
- `urgency_score` (IntegerField 1-5) - Niveau d'urgence
- `importance_score` (IntegerField 1-5) - Niveau d'importance
- `status` (CharField) - TODO, IN_PROGRESS, DONE
- `quadrant` (CharField) - Q1, Q2, Q3, Q4 (calculé automatiquement)
- `order` (IntegerField) - Pour le drag & drop

**Méthodes clés:**
- `calculate_quadrant()` - Calcule le quadrant selon urgence/importance
- `get_priority_score()` - Score de priorité global (0-100)
- `is_overdue` (property) - Vérifie si en retard
- `is_due_soon` (property) - Vérifie si due dans 24h
- `recommendation` (property) - Recommandation d'action

**Logique de classification:**
```python
if urgency >= 4 and importance >= 4: return 'Q1'  # Urgent & Important
elif urgency < 4 and importance >= 4: return 'Q2'  # Important
elif urgency >= 4 and importance < 4: return 'Q3'  # Urgent
else: return 'Q4'  # Ni urgent ni important
```

### TaskStatistics

**Champs:**
- `user` (OneToOneField) - Utilisateur
- `q1_completed`, `q2_completed`, `q3_completed`, `q4_completed` - Compteurs
- `total_tasks_created` - Total de tâches créées
- `total_tasks_completed` - Total de tâches complétées
- `last_updated` - Dernière mise à jour

**Méthodes:**
- `completion_rate` (property) - Taux de complétion en %
- `update_statistics()` - Met à jour les statistiques

## 🧠 Services Intelligents

### TaskIntelligenceService

**Méthodes principales:**

1. **suggest_priority(title, description, due_date)**
   - Suggère automatiquement urgence et importance
   - Analyse les mots-clés du titre/description
   - Calcule l'urgence selon la date d'échéance

2. **get_tasks_requiring_attention(user)**
   - Retourne les tâches nécessitant attention immédiate
   - Tâches en retard ou dues dans 24h
   - Tâches Q1 non commencées

3. **get_productivity_insights(user)**
   - Génère des insights de productivité
   - Analyse la distribution des tâches
   - Recommandations personnalisées

4. **get_next_recommended_task(user)**
   - Recommande la prochaine tâche à faire
   - Algorithme de priorisation intelligent
   - Ordre: Q1 en retard > Q1 aujourd'hui > Q1 prioritaire > Q2

5. **check_and_send_alerts(user)**
   - Vérifie et génère des alertes
   - Tâches en retard
   - Tâches dues bientôt
   - Tâches Q2 devenant urgentes

## 🎨 Vues (Views)

### Dashboard (dashboard)
- Vue principale avec les 4 quadrants
- Affiche les tâches par quadrant
- Alertes intelligentes
- Tâche recommandée
- Statistiques rapides
- Formulaire d'ajout rapide

### CRUD des tâches
- `task_create` - Créer une tâche
- `task_update` - Modifier une tâche
- `task_delete` - Supprimer une tâche
- `task_quick_create` - Ajout rapide

### Actions AJAX
- `task_toggle_status` - Basculer TODO/DONE
- `task_update_quadrant` - Drag & drop entre quadrants

### Statistiques (statistics)
- Vue détaillée des statistiques
- Répartition par quadrant
- Taux de complétion
- Recommandations de productivité

## 🔐 Authentification

### Vues utilisateurs
- `register` - Inscription
- `user_login` - Connexion
- `user_logout` - Déconnexion

### Configuration
- `LOGIN_URL = 'users:login'`
- `LOGIN_REDIRECT_URL = 'tasks:dashboard'`
- `LOGOUT_REDIRECT_URL = 'users:login'`

## 🎨 Design & UX

### Principes de design
- **Moderne**: Gradients, glassmorphism, animations
- **Responsive**: Mobile-first avec Tailwind CSS
- **Dark mode**: Toggle automatique avec localStorage
- **Couleurs par quadrant**:
  - Q1: Rouge (urgent & important)
  - Q2: Orange (important)
  - Q3: Bleu (urgent)
  - Q4: Gris (basse priorité)

### Animations
- Slide-in pour les nouveaux éléments
- Fade-in pour les transitions
- Hover effects sur les cartes
- Transform scale sur les boutons

### Composants réutilisables
- `task_card.html` - Carte de tâche avec tous les indicateurs
- Messages flash avec auto-dismiss
- Navigation sticky avec dark mode toggle

## 🔒 Sécurité

### Mesures implémentées
- CSRF protection (Django)
- Authentification requise pour toutes les vues tasks
- Validation des formulaires côté serveur
- Protection XSS via Django templates
- Échappement automatique des variables

### Pour la production
- Changer `SECRET_KEY`
- Mettre `DEBUG=False`
- Configurer `ALLOWED_HOSTS`
- Utiliser HTTPS
- Créer un utilisateur MySQL dédié
- Configurer les fichiers statiques avec collectstatic

## 📊 Base de Données

### Configuration MySQL
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'eisenhower_todo',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

### Migrations
```bash
python manage.py makemigrations  # Créer les migrations
python manage.py migrate         # Appliquer les migrations
```

## 🚀 Déploiement

### Développement
```bash
python manage.py runserver
```

### Production (exemple)
1. Collecter les fichiers statiques:
   ```bash
   python manage.py collectstatic
   ```

2. Utiliser un serveur WSGI (Gunicorn, uWSGI)
   ```bash
   gunicorn config.wsgi:application
   ```

3. Reverse proxy avec Nginx

## 📈 Fonctionnalités Futures

### Améliorations possibles
- [ ] Drag & drop réel entre quadrants (JavaScript)
- [ ] Notifications par email
- [ ] Export des tâches (PDF, CSV)
- [ ] Partage de tâches entre utilisateurs
- [ ] Récurrence des tâches
- [ ] Tags et catégories
- [ ] Recherche avancée
- [ ] API REST (Django REST Framework)
- [ ] Application mobile (React Native)
- [ ] Intégration calendrier (Google Calendar)

## 🧪 Tests

### Tests à implémenter
```python
# tests/test_models.py
def test_task_quadrant_calculation():
    task = Task(urgency_score=5, importance_score=5)
    assert task.calculate_quadrant() == 'Q1'

# tests/test_views.py
def test_dashboard_requires_login():
    response = client.get('/tasks/')
    assert response.status_code == 302  # Redirect to login

# tests/test_services.py
def test_priority_suggestion():
    suggestions = TaskIntelligenceService.suggest_priority(
        "Urgent client meeting", "", datetime.now() + timedelta(hours=2)
    )
    assert suggestions['urgency'] >= 4
```

## 📚 Ressources

### Documentation
- Django: https://docs.djangoproject.com/
- Tailwind CSS: https://tailwindcss.com/docs
- MySQL: https://dev.mysql.com/doc/

### Dépendances
- Django 6.0
- mysqlclient 2.2.1
- python-decouple 3.8

## 👨‍💻 Contribution

### Standards de code
- PEP 8 pour Python
- Commentaires en français
- Docstrings pour toutes les fonctions
- Type hints recommandés

### Git workflow
```bash
git checkout -b feature/nouvelle-fonctionnalite
git commit -m "feat: description de la fonctionnalité"
git push origin feature/nouvelle-fonctionnalite
```

## 📝 Licence

Projet éducatif - Libre d'utilisation

---

**Créé avec ❤️ par Antigravity (Google DeepMind)**
