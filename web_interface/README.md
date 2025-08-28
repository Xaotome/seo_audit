# Interface Web - SEO Audit Tool

Interface web moderne pour l'outil d'audit SEO avec suivi en temps réel et visualisation avancée des résultats.

## 🚀 Fonctionnalités

### ✨ Interface utilisateur
- **Formulaire intuitif** : Interface simple pour lancer des analyses
- **Options avancées** : Configuration détaillée des paramètres d'audit
- **Validation en temps réel** : Vérification des URLs et paramètres

### 📊 Suivi en temps réel
- **WebSocket** : Mises à jour en direct de la progression
- **Barre de progression** : Suivi visuel de l'avancement
- **Informations détaillées** : Pages analysées, temps restant, URL actuelle

### 📈 Visualisation des résultats
- **Tableaux interactifs** : Résultats détaillés avec filtres et recherche
- **Graphiques** : Visualisation des problèmes et métriques
- **Cartes de statistiques** : Résumé exécutif avec indicateurs clés
- **Détails par page** : Modal avec informations complètes

### 💾 Gestion des données
- **Export multiple** : Téléchargement en JSON, CSV, HTML
- **Historique** : Conservation des analyses précédentes
- **Sessions** : Suivi des analyses en cours

## 🛠️ Installation

### Prérequis
```bash
# Python 3.8+
python3 --version

# Dépendances de base
cd /path/to/seo_audit
pip3 install -r requirements.txt
```

### Installation web
```bash
# Dépendances web supplémentaires
pip3 install -r web_interface/requirements_web.txt

# Ou installation manuelle
pip3 install flask flask-socketio
```

## 🚀 Démarrage

### Méthode simple
```bash
cd web_interface
python3 run_web.py
```

### Méthode manuelle
```bash
cd web_interface
python3 app.py
```

### Accès à l'interface
- **URL** : http://localhost:5000
- **Interface** : Formulaire d'analyse
- **Historique** : http://localhost:5000/history

## 📖 Utilisation

### 1. Lancer une analyse
1. Accéder à http://localhost:5000
2. Saisir l'URL du site à analyser
3. Configurer les options (optionnel)
4. Cliquer sur "Démarrer l'analyse"

### 2. Suivre la progression
- Page automatique de suivi avec WebSocket
- Barre de progression en temps réel
- Informations détaillées sur l'avancement
- Possibilité d'arrêter l'analyse

### 3. Consulter les résultats
- Redirection automatique vers les résultats
- Résumé exécutif avec métriques clés
- Graphiques de visualisation
- Tableau détaillé avec filtres
- Export en différents formats

### 4. Historique
- Consultation des analyses précédentes
- Téléchargement des rapports
- Statistiques globales

## 🎨 Interface utilisateur

### Page d'accueil
- Formulaire principal avec validation
- Options avancées dépliables
- Cartes d'information sur les fonctionnalités
- Design responsive

### Page de progression
- WebSocket pour mises à jour temps réel
- Barres de progression animées
- Informations détaillées
- Boutons d'action (arrêt, historique)

### Page de résultats
- Cartes de statistiques colorées
- Graphiques interactifs (Chart.js)
- Tableau filtrable et triable
- Modals de détail par page
- Boutons d'export

### Page d'historique
- Liste des analyses avec statuts
- Statistiques globales
- Actions de téléchargement
- Gestion des analyses en cours

## ⚙️ Configuration

### Variables d'environnement
```bash
# Port du serveur (défaut: 5000)
export FLASK_PORT=5000

# Mode debug (défaut: True)
export FLASK_DEBUG=True

# Répertoire de résultats
export RESULTS_DIR="./results"
```

### Personnalisation
- **CSS** : `static/css/style.css`
- **JavaScript** : `static/js/app.js`
- **Templates** : `templates/`

## 🔧 Architecture technique

### Backend (Flask)
```
app.py                 # Application principale
├── Routes
│   ├── /              # Page d'accueil
│   ├── /start_analysis # Démarrage d'analyse
│   ├── /analysis/<id> # Progression
│   ├── /results/<id>  # Résultats
│   └── /history       # Historique
├── WebSocket
│   ├── progress_update # Mises à jour progression
│   ├── analysis_complete # Fin d'analyse
│   └── analysis_error  # Erreurs
└── API
    └── /api/status/<id> # Statut d'analyse
```

### Frontend
```
templates/
├── base.html          # Template de base
├── index.html         # Page d'accueil
├── progress.html      # Suivi progression
├── results.html       # Résultats détaillés
└── history.html       # Historique

static/
├── css/style.css      # Styles personnalisés
└── js/app.js          # JavaScript principal
```

### Gestion des données
```
results/
├── <analysis_id>.json # Données JSON
├── <analysis_id>.html # Rapport HTML
└── ...                # Autres analyses
```

## 📊 Fonctionnalités avancées

### Graphiques interactifs
- **Donut chart** : Répartition des problèmes
- **Bar chart** : Distribution des longueurs de titres
- **Chart.js** : Bibliothèque de graphiques responsive

### Filtres et recherche
- **Filtre par statut** : 200, 404, 500, etc.
- **Filtre par problèmes** : Avec/sans problèmes
- **Recherche textuelle** : URL, titre
- **Export CSV filtré** : Données selon les filtres actifs

### WebSocket temps réel
- **Progression live** : Mises à jour instantanées
- **Gestion des erreurs** : Notifications d'erreur
- **Reconnexion automatique** : En cas de déconnexion
- **Fallback polling** : Si WebSocket indisponible

## 🚨 Résolution de problèmes

### Erreurs courantes

**Port déjà utilisé**
```bash
# Vérifier les ports utilisés
lsof -i :5000

# Changer le port
export FLASK_PORT=5001
python3 run_web.py
```

**Dépendances manquantes**
```bash
# Réinstaller les dépendances
pip3 install -r requirements_web.txt

# Vérification
python3 -c "import flask, flask_socketio; print('OK')"
```

**Erreur WebSocket**
```bash
# Installer eventlet si nécessaire
pip3 install eventlet

# Ou utiliser gevent
pip3 install gevent gevent-websocket
```

**Problème d'import seo_audit**
```bash
# Vérifier la structure
ls ../seo_audit/

# Lancer depuis le bon répertoire
cd web_interface
python3 run_web.py
```

### Mode debug
```bash
# Activer les logs détaillés
export FLASK_DEBUG=True
export FLASK_ENV=development

# Lancer avec logs
python3 app.py 2>&1 | tee debug.log
```

## 🔒 Sécurité

### Recommandations production
- Changer la `secret_key` dans app.py
- Utiliser un serveur WSGI (Gunicorn, uWSGI)
- Configurer un reverse proxy (Nginx)
- Limiter l'accès aux résultats
- Nettoyer régulièrement le dossier results/

### Exemple de déploiement
```bash
# Gunicorn avec workers
pip3 install gunicorn eventlet
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 app:app
```

## 📈 Performance

### Optimisations
- **Analyse asynchrone** : Thread séparé pour l'audit
- **WebSocket optimisé** : Mises à jour uniquement nécessaires
- **Caching statique** : CSS/JS servis efficacement
- **Pagination** : Pour les gros résultats (à implémenter)

### Surveillance
- **Logs Flask** : Monitoring des requêtes
- **Métriques WebSocket** : Connexions actives
- **Stockage** : Nettoyage automatique des anciens résultats

## 🎯 Évolutions futures

### V2 Prévue
- **Multi-utilisateurs** : Authentification et sessions
- **API REST** : Endpoints pour intégration
- **Planification** : Analyses programmées
- **Notifications** : Email/Slack en fin d'analyse
- **Comparaison** : Evolution entre analyses
- **Dashboard** : Vue d'ensemble multi-sites

### Intégrations
- **GitHub Actions** : CI/CD avec analyses
- **Docker** : Conteneurisation
- **Monitoring** : Prometheus/Grafana
- **Base de données** : PostgreSQL/SQLite