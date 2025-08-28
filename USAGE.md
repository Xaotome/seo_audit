# Guide d'utilisation - Outil d'audit SEO

## 🚀 Démarrage rapide

### 1. Installation
```bash
# Installer les dépendances
python3 install.py

# Ou avec make
make install
```

### 2. Premier audit
```bash
# Audit simple
python3 run_audit.py https://example.com

# Avec le Makefile
make run
```

## 📖 Exemples d'utilisation

### Audits basiques
```bash
# Audit avec 50 pages maximum
python3 run_audit.py https://example.com --limit 50

# Export en JSON
python3 run_audit.py https://example.com --format json

# Export HTML avec nom personnalisé
python3 run_audit.py https://example.com --format html --output mon_site_audit
```

### Audits avancés
```bash
# Audit complet avec options personnalisées
python3 run_audit.py https://example.com \
    --limit 200 \
    --rate-limit 2.0 \
    --timeout 30 \
    --format html \
    --verbose

# Audit sans suivre les redirections
python3 run_audit.py https://example.com --no-redirects

# Audit rapide (ignorer les images)
python3 run_audit.py https://example.com --no-images --rate-limit 3.0
```

## 📊 Interprétation des résultats

### Format CSV
Le fichier CSV contient une ligne par page avec les colonnes :
- `url` : URL de la page
- `status` : Code de statut HTTP
- `response_ms` : Temps de réponse en millisecondes
- `title_len` : Longueur du titre
- `meta_desc_len` : Longueur de la meta description
- `h1_count` : Nombre de balises H1
- `word_count` : Nombre de mots
- `issues` : Liste des problèmes détectés

### Problèmes courants détectés
- **"Missing title"** : Pas de balise `<title>`
- **"Title too short"** : Titre < 10 caractères
- **"Title too long"** : Titre > 65 caractères
- **"Missing meta description"** : Pas de meta description
- **"Meta description too short"** : Meta description < 50 caractères
- **"Meta description too long"** : Meta description > 160 caractères
- **"Missing H1"** : Aucune balise H1
- **"Multiple H1 tags"** : Plusieurs balises H1
- **"Missing canonical"** : Pas de balise canonical
- **"Canonical not accessible"** : Canonical retourne une erreur
- **"Low word count"** : Moins de 150 mots
- **"X images without alt"** : Images sans attribut alt

## 🔧 Configuration avancée

### Variables d'environnement
```bash
# User agent personnalisé
export SEO_USER_AGENT="MonBot/1.0 (+https://monsite.com)"

# Timeout par défaut
export SEO_TIMEOUT=20
```

### Utilisation programmatique
```python
from seo_audit.models import AuditConfig
from seo_audit.audit_engine import SEOAuditEngine

# Configuration
config = AuditConfig(
    domain="https://example.com",
    max_pages=100,
    rate_limit=1.5,
    output_format="json"
)

# Audit
engine = SEOAuditEngine(config)
results = engine.run_audit()

# Export
engine.export_results("mon_audit")
```

## 🎯 Bonnes pratiques

### Pour les gros sites
```bash
# Commencer petit pour tester
python3 run_audit.py https://monsite.com --limit 10

# Augmenter progressivement
python3 run_audit.py https://monsite.com --limit 100 --rate-limit 0.5

# Production avec toutes les options
python3 run_audit.py https://monsite.com \
    --limit 1000 \
    --rate-limit 1.0 \
    --timeout 30 \
    --format html \
    --output audit_complet
```

### Pour les sites lents
```bash
# Augmenter le timeout
python3 run_audit.py https://monsite.com --timeout 45

# Réduire la charge
python3 run_audit.py https://monsite.com --rate-limit 0.5
```

### Pour les sites avec JavaScript
```bash
# Activer le rendu JS (nécessite playwright)
python3 run_audit.py https://monsite.com --js-rendering
```

## 🚨 Résolution des problèmes

### Erreurs courantes

**"ModuleNotFoundError"**
```bash
# Réinstaller les dépendances
python3 install.py
```

**"Connection timeout"**
```bash
# Augmenter le timeout
python3 run_audit.py https://example.com --timeout 60
```

**"Rate limited"**
```bash
# Réduire la vitesse
python3 run_audit.py https://example.com --rate-limit 0.5
```

**"Blocked by robots.txt"**
- Vérifier robots.txt du site
- L'outil respecte automatiquement robots.txt

### Tests et débogage
```bash
# Test des imports
make test-basic

# Tests complets (si pytest installé)
make test

# Démonstration complète
make demo

# Nettoyage
make clean
```

## 📈 Optimisation des performances

### Recommandations
1. **Rate limiting** : Commencer à 1 req/s, ajuster selon la réactivité
2. **Timeout** : 15s par défaut, augmenter pour les sites lents  
3. **Limite de pages** : Commencer petit (50-100), augmenter progressivement
4. **Format de sortie** : CSV pour l'analyse, HTML pour la présentation

### Surveillance
```bash
# Monitoring en temps réel
python3 run_audit.py https://example.com --verbose

# Audit par batch
for site in site1.com site2.com site3.com; do
    python3 run_audit.py https://$site --limit 100 --output "audit_$site"
done
```

## 💡 Cas d'usage typiques

### Audit de migration
```bash
# Avant migration
python3 run_audit.py https://ancien-site.com --output avant_migration

# Après migration  
python3 run_audit.py https://nouveau-site.com --output apres_migration

# Comparer les fichiers CSV résultants
```

### Suivi régulier
```bash
# Script de suivi mensuel
#!/bin/bash
DATE=$(date +%Y%m%d)
python3 run_audit.py https://monsite.com \
    --limit 500 \
    --format html \
    --output "audit_${DATE}"
```

### Audit concurrentiel
```bash
# Analyser plusieurs sites
for concurrent in site1.com site2.com site3.com; do
    python3 run_audit.py https://$concurrent \
        --limit 50 \
        --output "concurrent_$concurrent"
done
```