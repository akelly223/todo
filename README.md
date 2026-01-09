# Eisenhower TODO - Application de gestion de tâches intelligente

## 📋 Description

Application web moderne de gestion de tâches basée sur la **matrice d'Eisenhower**, permettant de classer automatiquement vos tâches en 4 quadrants :

1. **Q1 - Urgent & Important** : À faire maintenant
2. **Q2 - Important mais pas urgent** : À planifier
3. **Q3 - Urgent mais pas important** : À déléguer
4. **Q4 - Ni urgent ni important** : À éliminer

## 🚀 Stack Technique

- **Backend** : Django 5.0
- **Frontend** : Django Templates + Tailwind CSS
- **Base de données** : MySQL (WampServer)
- **Authentification** : Django Auth System

## ✨ Fonctionnalités

- ✅ Création, modification, suppression de tâches
- ✅ Classification automatique dans les quadrants
- ✅ Drag & Drop entre quadrants
- ✅ Priorisation intelligente
- ✅ Mode sombre / clair
- ✅ Interface responsive et moderne
- ✅ Suggestions de priorité
- ✅ Alertes pour tâches urgentes
- ✅ Statistiques de productivité

## 📦 Installation

### Prérequis

- Python 3.10+
- WampServer (MySQL)
- Node.js (pour Tailwind CSS)

### Étapes d'installation

1. **Cloner le projet**
```bash
cd c:\Users\Mali_Code\Desktop\todo
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Installer les dépendances Python**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**
```bash
copy .env.example .env
# Éditer .env avec vos paramètres MySQL
```

5. **Créer la base de données MySQL**
- Démarrer WampServer
- Créer une base de données nommée `eisenhower_todo`
```sql
CREATE DATABASE eisenhower_todo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

6. **Appliquer les migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

7. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

8. **Installer Tailwind CSS**
```bash
npm install -D tailwindcss
npx tailwindcss init
```

9. **Compiler Tailwind CSS**
```bash
npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch
```

10. **Lancer le serveur de développement**
```bash
python manage.py runserver
```

11. **Accéder à l'application**
- Ouvrir votre navigateur : http://127.0.0.1:8000

## 🎨 Utilisation

1. **Créer un compte** ou se connecter
2. **Ajouter une tâche** avec titre, description, date d'échéance
3. **Définir l'urgence et l'importance** (score 1-5)
4. La tâche est **automatiquement classée** dans le bon quadrant
5. **Glisser-déposer** pour réorganiser
6. **Marquer comme terminée** quand c'est fait

## 🏗️ Architecture

```
config/          → Configuration Django
tasks/           → Application principale (modèles, vues, logique)
users/           → Gestion des utilisateurs
static/          → CSS, JS, images
templates/       → Templates HTML
```

## 🔒 Sécurité

- CSRF protection activée
- Authentification requise pour toutes les vues
- Validation des formulaires
- Protection XSS via Django templates

## 📊 Fonctionnalités intelligentes

- **Auto-classification** : Calcul automatique du quadrant selon urgence/importance
- **Alertes** : Notification quand une tâche importante devient urgente
- **Recommandations** : Suggestions d'actions par quadrant
- **Statistiques** : Analyse de productivité par quadrant

## 📝 Licence

Projet éducatif - Libre d'utilisation

## 👨‍💻 Auteur

Créé avec ❤️ par Antigravity (Google DeepMind)
