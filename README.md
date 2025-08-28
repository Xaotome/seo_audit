# SEO Audit Tool

Un outil d'audit SEO professionnel développé en Python pour analyser et optimiser les performances SEO de sites web.

## 🚀 Fonctionnalités

### MVP (Version 0.1.0)
- ✅ **Découverte d'URLs** : Analyse automatique via sitemap.xml avec fallback sur la page d'accueil
- ✅ **Politesse** : Respect de robots.txt, user-agent personnalisé et limitation de taux
- ✅ **Analyses de base** :
  - Code HTTP et temps de réponse
  - Présence et longueur des balises `<title>`
  - Présence et longueur de `<meta name="description">`
  - Comptage des balises H1
  - Validation des balises canonical
  - Analyse des balises meta robots (noindex/nofollow)
  - Comptage des images sans attribut alt
  - Analyse des liens internes/externes
  - Comptage des mots (contenu principal)
- ✅ **Export** : CSV, JSON et rapports HTML

### Version 1 (Fonctionnalités avancées)
- ✅ **Maillage interne** : Graphe des liens internes, détection des pages orphelines
- ✅ **Redirections** : Détection des chaînes et boucles de redirections
- ✅ **International** : Analyse hreflang pour la cohérence réciproque
- ✅ **Indexabilité** : Cohérence entre noindex, robots.txt et canonical
- ✅ **Données structurées** : Détection et validation basique des types JSON-LD
- ✅ **Performance serveur** : Taille HTML, compression GZIP, en-têtes cache

## 📦 Installation

```bash
# Cloner le repository
git clone <repository-url>
cd seo_audit

# Installer les dépendances
pip install -r requirements.txt

# Installation en mode développement
pip install -e .
```

## 🔧 Utilisation

### Interface en ligne de commande

```bash
# Audit basique
python -m seo_audit.cli https://example.com

# Audit avec options personnalisées
python -m seo_audit.cli https://example.com --limit 500 --format json --rate-limit 2.0

# Export HTML avec sortie personnalisée
python -m seo_audit.cli https://example.com --format html --output mon_audit

# Audit détaillé avec toutes les options
python -m seo_audit.cli https://example.com \
    --limit 200 \
    --depth 3 \
    --rate-limit 1.5 \
    --timeout 30 \
    --format html \
    --output audit_complet \
    --verbose
```

### Options disponibles

| Option | Description | Défaut |
|--------|-------------|--------|
| `--limit` | Nombre maximum de pages à auditer | 100 |
| `--depth` | Profondeur maximum de crawl | 3 |
| `--rate-limit` | Requêtes par seconde | 1.0 |
| `--timeout` | Timeout des requêtes (secondes) | 15 |
| `--format` | Format de sortie (csv/json/html) | csv |
| `--output` | Nom du fichier de sortie | auto |
| `--user-agent` | User agent personnalisé | SEO-AuditBot/0.1 |
| `--no-redirects` | Ne pas suivre les redirections | false |
| `--no-images` | Ignorer l'analyse des images | false |
| `--verbose` | Affichage détaillé | false |

## 📊 Rapports générés

### Format CSV
Données tabulaires détaillées avec toutes les métriques pour chaque page analysée.

### Format JSON
Structure de données complète incluant :
- Métadonnées de l'audit
- Résultats détaillés par page
- Chaînes de redirection
- En-têtes cache
- Timestamp de crawl

### Format HTML
Rapport visuel comprenant :
- Résumé exécutif avec métriques clés
- Tableau détaillé des résultats
- Insights de performance
- Top 10 des problèmes identifiés

## 🏗️ Architecture

```
seo_audit/
├── models.py              # Modèles de données (PageResult, AuditConfig, etc.)
├── utils.py               # Utilitaires (normalisation URL, validation, etc.)
├── crawler.py             # Découverte et crawl d'URLs
├── analyzers.py           # Analyseurs SEO de base (MVP)
├── advanced_analyzers.py  # Analyseurs avancés (V1)
├── exporters.py           # Export et génération de rapports
├── audit_engine.py        # Moteur principal d'orchestration
└── cli.py                 # Interface en ligne de commande
```

## 🧪 Tests

```bash
# Lancer tous les tests
python -m pytest tests/

# Tests avec couverture
python -m pytest tests/ --cov=seo_audit

# Tests spécifiques
python -m pytest tests/test_utils.py
python -m pytest tests/test_models.py
```

## 📈 Métriques analysées

### Métriques techniques
- **Codes de statut HTTP** : Identification des erreurs 4xx/5xx
- **Temps de réponse** : Détection des pages lentes
- **Taille des pages** : Identification des pages surdimensionnées
- **Compression** : Vérification de la compression GZIP
- **Chaînes de redirection** : Optimisation des redirections

### Métriques SEO on-page
- **Balises title** : Présence, longueur optimale (10-65 caractères)
- **Meta descriptions** : Présence, longueur optimale (50-160 caractères)
- **Structure H1** : Présence et unicité des H1
- **Balises canonical** : Validation et accessibilité
- **Meta robots** : Détection des directives noindex/nofollow
- **Images** : Vérification des attributs alt
- **Contenu textuel** : Comptage des mots et détection de contenu faible

### Métriques de maillage
- **Liens internes/externes** : Ratio et distribution
- **Pages orphelines** : Détection via sitemap vs crawl
- **Autorité des pages** : Score basé sur les liens entrants
- **Profondeur de crawl** : Distance depuis la page d'accueil

### Métriques internationales
- **Hreflang** : Cohérence réciproque entre versions linguistiques
- **Données structurées** : Présence et validation JSON-LD

## 🔒 Bonnes pratiques intégrées

- **Respect du robots.txt** et des directives crawl-delay
- **Rate limiting** configurable pour éviter la surcharge serveur
- **User agent identifiable** pour faciliter l'identification dans les logs
- **Gestion gracieuse des erreurs** avec continuation du crawl
- **Timeouts configurables** pour éviter les blocages
- **Déduplication d'URLs** pour éviter les analyses multiples

## 🚀 Prochaines étapes (V2)

- **Rendu JavaScript** avec Playwright pour les sites SPA
- **Core Web Vitals** via API PageSpeed Insights
- **Analyse d'images avancée** (dimensions, poids, formats modernes)
- **Accessibilité** (contraste, landmarks, ARIA)
- **Scoring et priorisation** des problèmes par impact

## 🤝 Contribution

Les contributions sont les bienvenues ! Merci de :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Consulter la documentation des bonnes pratiques SEO
- Vérifier la configuration robots.txt du site cible