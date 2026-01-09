# 🚀 GUIDE D'INSTALLATION - Eisenhower TODO

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir installé :

1. **Python 3.10 ou supérieur**
   - Télécharger : https://www.python.org/downloads/
   - Vérifier : `python --version`

2. **WampServer (pour MySQL)**
   - Télécharger : https://www.wampserver.com/
   - Démarrer WampServer et vérifier que l'icône est verte

3. **Node.js** (optionnel, pour Tailwind CSS en local)
   - Télécharger : https://nodejs.org/

## 🔧 Installation étape par étape

### Étape 1 : Préparer l'environnement Python

```bash
# Se placer dans le dossier du projet
cd c:\Users\Mali_Code\Desktop\todo

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

### Étape 2 : Configurer la base de données MySQL

1. **Démarrer WampServer**
   - Cliquer sur l'icône WampServer
   - Attendre que l'icône devienne verte

2. **Créer la base de données**
   - Ouvrir phpMyAdmin : http://localhost/phpmyadmin
   - Cliquer sur "SQL" dans le menu
   - Copier-coller le contenu de `setup_database.sql`
   - Cliquer sur "Exécuter"

   OU en ligne de commande :
   ```bash
   mysql -u root -p < setup_database.sql
   ```

3. **Vérifier le fichier .env**
   - Le fichier `.env` doit contenir :
   ```
   DB_NAME=eisenhower_todo
   DB_USER=root
   DB_PASSWORD=
   DB_HOST=127.0.0.1
   DB_PORT=3306
   ```
   - Si vous avez un mot de passe MySQL, ajoutez-le dans `DB_PASSWORD`

### Étape 3 : Créer les tables Django

```bash
# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate
```

### Étape 4 : Créer un superutilisateur

```bash
python manage.py createsuperuser
```

Suivez les instructions :
- Nom d'utilisateur : (votre choix)
- Email : (optionnel)
- Mot de passe : (votre choix)

### Étape 5 : Lancer le serveur

```bash
python manage.py runserver
```

### Étape 6 : Accéder à l'application

Ouvrir votre navigateur et aller sur :
- **Application** : http://127.0.0.1:8000
- **Admin Django** : http://127.0.0.1:8000/admin

## 🎨 Configuration de Tailwind CSS (Optionnel)

Si vous voulez compiler Tailwind CSS localement :

```bash
# Installer Tailwind
npm install -D tailwindcss

# Initialiser Tailwind
npx tailwindcss init

# Compiler CSS (dans un terminal séparé)
npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch
```

**Note** : L'application utilise actuellement le CDN Tailwind pour le développement rapide.

## 🐛 Résolution des problèmes courants

### Erreur : "No module named 'MySQLdb'"

```bash
pip install mysqlclient
```

Si l'installation échoue sur Windows, télécharger le wheel depuis :
https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient

### Erreur : "Can't connect to MySQL server"

1. Vérifier que WampServer est démarré (icône verte)
2. Vérifier les paramètres dans `.env`
3. Tester la connexion MySQL :
   ```bash
   mysql -u root -p
   ```

### Erreur : "django.db.utils.OperationalError"

La base de données n'existe pas. Exécuter le script SQL :
```bash
mysql -u root -p < setup_database.sql
```

### Port 8000 déjà utilisé

Lancer sur un autre port :
```bash
python manage.py runserver 8080
```

## 📚 Utilisation de l'application

### Première connexion

1. Créer un compte sur http://127.0.0.1:8000/users/register/
2. Se connecter avec vos identifiants
3. Vous serez redirigé vers le dashboard

### Créer votre première tâche

1. Cliquer sur "Nouvelle tâche" dans le menu
2. Remplir le formulaire :
   - **Titre** : Ex: "Finir le rapport trimestriel"
   - **Description** : Détails de la tâche
   - **Date d'échéance** : Choisir une date
   - **Urgence** : 1 (pas urgent) à 5 (très urgent)
   - **Importance** : 1 (pas important) à 5 (très important)
3. Cliquer sur "Créer la tâche"

La tâche sera automatiquement classée dans le bon quadrant !

### Comprendre les quadrants

- **Q1 (Rouge)** : Urgent & Important → À faire MAINTENANT
- **Q2 (Orange)** : Important mais pas urgent → À PLANIFIER
- **Q3 (Bleu)** : Urgent mais pas important → À DÉLÉGUER
- **Q4 (Gris)** : Ni urgent ni important → À ÉLIMINER

### Fonctionnalités intelligentes

- **Recommandations** : L'application suggère la prochaine tâche à faire
- **Alertes** : Notifications pour les tâches en retard ou urgentes
- **Statistiques** : Analysez votre productivité par quadrant
- **Auto-classification** : Les tâches sont classées automatiquement

## 🔒 Sécurité

### Pour la production

1. **Changer le SECRET_KEY** dans `.env`
   ```python
   # Générer une nouvelle clé
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **Désactiver DEBUG**
   ```
   DEBUG=False
   ```

3. **Configurer ALLOWED_HOSTS**
   ```
   ALLOWED_HOSTS=votredomaine.com,www.votredomaine.com
   ```

4. **Créer un utilisateur MySQL dédié**
   ```sql
   CREATE USER 'eisenhower_user'@'localhost' IDENTIFIED BY 'mot_de_passe_securise';
   GRANT ALL PRIVILEGES ON eisenhower_todo.* TO 'eisenhower_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

## 📞 Support

En cas de problème :
1. Vérifier les logs Django dans le terminal
2. Consulter la documentation Django : https://docs.djangoproject.com/
3. Vérifier que toutes les dépendances sont installées : `pip list`

## 🎉 Félicitations !

Votre application Eisenhower TODO est maintenant opérationnelle !

Commencez à gérer vos tâches intelligemment avec la matrice d'Eisenhower. 🚀
