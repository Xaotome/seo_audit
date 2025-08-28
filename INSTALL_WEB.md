# Installation de l'Interface Web - SEO Audit Tool

Guide d'installation rapide pour l'interface web de l'outil d'audit SEO.

## 🚀 Installation rapide

### 1. Installation automatique
```bash
# Depuis le répertoire racine du projet
python3 start_web_server.py
```

### 2. Installation manuelle

#### Étape 1 : Dépendances
```bash
# Dépendances de base
pip3 install -r requirements.txt

# Dépendances web
pip3 install flask flask-socketio eventlet
```

#### Étape 2 : Lancement
```bash
# Méthode 1 : Script dédié
cd web_interface
python3 run_web.py

# Méthode 2 : Direct
cd web_interface
python3 app.py
```

## 🌐 Accès à l'interface

Une fois démarré, l'interface est accessible sur :
- **URL principale** : http://localhost:5000
- **Historique** : http://localhost:5000/history

## 📋 Vérification de l'installation

### Test rapide
```bash
# Vérifier les imports Python
python3 -c "
import flask
import flask_socketio
from seo_audit.models import PageResult
print('✅ Installation OK')
"
```

### Test complet
1. Accéder à http://localhost:5000
2. Saisir une URL de test (ex: https://httpbin.org)
3. Lancer l'analyse avec les paramètres par défaut
4. Vérifier le suivi en temps réel
5. Consulter les résultats

## 🛠️ Structure des fichiers

```
web_interface/
├── app.py                 # Application Flask principale
├── run_web.py            # Script de lancement
├── requirements_web.txt  # Dépendances web
├── templates/            # Templates HTML
│   ├── base.html
│   ├── index.html        # Formulaire d'analyse
│   ├── progress.html     # Suivi en temps réel
│   ├── results.html      # Résultats détaillés
│   └── history.html      # Historique
├── static/              # Ressources statiques
│   ├── css/style.css    # Styles personnalisés
│   └── js/app.js        # JavaScript principal
└── results/             # Stockage des résultats
```

## 🔧 Configuration

### Variables d'environnement optionnelles
```bash
export FLASK_PORT=5000     # Port du serveur
export FLASK_DEBUG=True    # Mode debug
export RESULTS_DIR="./results"  # Répertoire de stockage
```

### Personnalisation
- **Port** : Modifier dans `app.py` (ligne finale)
- **Styles** : Éditer `static/css/style.css`
- **Fonctionnalités** : Modifier `static/js/app.js`

## 📊 Fonctionnalités principales

### ✨ Interface utilisateur
- Formulaire intuitif avec validation
- Options avancées configurables
- Design responsive (mobile/desktop)

### 📈 Suivi temps réel
- WebSocket pour mises à jour live
- Barre de progression animée
- Informations détaillées sur l'avancement

### 📋 Résultats avancés
- Tableaux interactifs avec filtres
- Graphiques de visualisation (Chart.js)
- Export multiple (JSON, CSV, HTML)
- Détails par page en modal

### 📚 Historique
- Conservation des analyses précédentes
- Téléchargement des rapports
- Statistiques globales

## 🚨 Résolution de problèmes

### Erreur : "Port already in use"
```bash
# Vérifier les processus sur le port 5000
lsof -i :5000

# Arrêter le processus ou changer le port
# Dans app.py, modifier la dernière ligne :
# socketio.run(app, debug=True, host='0.0.0.0', port=5001)
```

### Erreur : "ModuleNotFoundError"
```bash
# Installer les dépendances manquantes
pip3 install flask flask-socketio eventlet

# Ou via requirements
pip3 install -r web_interface/requirements_web.txt
```

### Erreur : WebSocket connection failed
```bash
# Vérifier eventlet
pip3 install eventlet

# Alternative avec gevent
pip3 install gevent gevent-websocket
```

### Erreur : Cannot import seo_audit
```bash
# Vérifier la structure du projet
ls seo_audit/

# S'assurer d'être dans le bon répertoire
cd web_interface
python3 run_web.py
```

## 🔒 Production

### Configuration sécurisée
```python
# Dans app.py, changer :
app.secret_key = 'votre-cle-secrete-aleatoire'

# Désactiver le debug
socketio.run(app, debug=False, host='0.0.0.0', port=5000)
```

### Déploiement avec Gunicorn
```bash
# Installation
pip3 install gunicorn eventlet

# Lancement
cd web_interface
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 app:app
```

### Nginx (reverse proxy)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /socket.io/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 📈 Performance

### Recommandations
- **Nettoyage** : Supprimer régulièrement les anciens résultats
- **Mémoire** : Limiter le nombre d'analyses simultanées
- **Stockage** : Surveiller l'espace disque du dossier results/

### Monitoring
```bash
# Taille des résultats
du -sh web_interface/results/

# Processus Python
ps aux | grep python

# Connexions réseau
netstat -tulpn | grep :5000
```

## 📞 Support

### En cas de problème
1. Vérifier les logs dans la console
2. Tester avec une URL simple (httpbin.org)
3. Consulter les fichiers de log
4. Vérifier les dépendances Python

### Logs utiles
```bash
# Logs détaillés
cd web_interface
python3 app.py 2>&1 | tee debug.log

# Vérification des modules
python3 -c "
import sys
print('Python version:', sys.version)
import flask
print('Flask version:', flask.__version__)
import flask_socketio
print('Flask-SocketIO version:', flask_socketio.__version__)
"
```

Cette interface web complète permettra à vos utilisateurs d'utiliser facilement l'outil d'audit SEO via un navigateur, avec un suivi en temps réel et une présentation professionnelle des résultats !