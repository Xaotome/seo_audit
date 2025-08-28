# Analyse de la Structure des Titres - Documentation

## 🎯 Vue d'ensemble

L'outil d'audit SEO analyse maintenant la **structure hiérarchique des titres** (H1-H6) de chaque page, détecte les problèmes de hiérarchie et affiche une visualisation claire dans l'interface web.

## 📋 Fonctionnalités ajoutées

### 1. **Extraction de la structure**
- Collecte tous les titres H1 à H6 dans l'ordre d'apparition
- Enregistre le niveau, le texte et la position de chaque titre
- Limite le texte à 100 caractères pour l'affichage

### 2. **Validation de la hiérarchie**
L'outil détecte automatiquement ces problèmes :

- ❌ **Pas de H1** : Aucun titre principal trouvé
- ❌ **H1 multiples** : Plus d'un H1 sur la page
- ❌ **Premier titre non-H1** : Le premier titre n'est pas un H1
- ❌ **Saut de niveau** : Passage direct de H1 à H3 sans H2
- ❌ **Titres vides** : Balises de titre sans contenu
- ❌ **Titres trop longs** : Plus de 70 caractères

### 3. **Affichage dans l'interface web**
- **Structure visuelle** : Indentation selon le niveau hiérarchique
- **Badges colorés** : H1 (bleu), H2 (gris), H3 (vert), etc.
- **Position** : Ordre d'apparition dans le document
- **Problèmes** : Alerte avec liste des erreurs détectées
- **Validation** : Confirmation si la structure est correcte

## 🔧 Utilisation

### Analyse via Python
```bash
# Analyser un site avec structure des titres
python3 run_audit.py https://exemple.com --web-output
```

### Visualisation web
1. Ouvrez `index.html` dans votre navigateur
2. Lancez une analyse ou chargez des données existantes
3. Cliquez sur **"Détails"** pour une page
4. Consultez la section **"Structure des titres (H1-H6)"**

## 📊 Format des données

### Structure JSON générée
```json
{
  "headingsStructure": [
    {
      "level": 1,
      "text": "Titre principal de la page",
      "position": 0
    },
    {
      "level": 2,
      "text": "Section importante",
      "position": 1
    },
    {
      "level": 3,
      "text": "Sous-section détaillée",
      "position": 2
    }
  ],
  "headingsHierarchyIssues": [
    "Heading level skip: H2 → H4 (missing H3)"
  ]
}
```

### Modèle de données Python
```python
@dataclass
class HeadingItem:
    level: int          # 1-6 pour H1-H6
    text: str          # Texte du titre (max 100 chars)
    position: int      # Position dans le document

@dataclass
class PageResult:
    # ... autres champs
    headings_structure: List[HeadingItem]
    headings_hierarchy_issues: List[str]
```

## 🎨 Interface visuelle

### Exemple d'affichage
```
┌─ Structure des titres (H1-H6) ──────────────────┐
│                                                 │
│  [H1] Accueil - Mon Site Web                   │
│      Position: 1                               │
│                                                 │
│    [H2] À propos de nous                       │
│        Position: 2                             │
│                                                 │
│      [H3] Notre équipe                         │
│          Position: 3                           │
│                                                 │
│      [H3] Notre mission                        │
│          Position: 4                           │
│                                                 │
│    [H2] Nos services                           │
│        Position: 5                             │
│                                                 │
│  ✓ Structure de titrage correcte               │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Problèmes détectés
```
┌─ Problèmes de hiérarchie ──────────────────────┐
│                                                 │
│  ⚠️ Multiple H1 headings found (2)            │
│  ⚠️ Heading level skip: H1 → H3 (missing H2)  │
│  ⚠️ 1 headings are too long (>70 chars)       │
│                                                 │
└─────────────────────────────────────────────────┘
```

## 🎯 Bonnes pratiques SEO

### Structure recommandée
```
H1 - Titre principal (1 seul par page)
├── H2 - Section principale
│   ├── H3 - Sous-section
│   └── H3 - Sous-section
├── H2 - Section principale  
│   ├── H3 - Sous-section
│   │   └── H4 - Sous-sous-section
│   └── H3 - Sous-section
└── H2 - Section principale
```

### Règles importantes
- **Un seul H1** par page (titre principal)
- **Hiérarchie logique** : H1 → H2 → H3 → H4...
- **Pas de saut** : Ne pas passer de H1 à H3 directement
- **Contenu utile** : Titres descriptifs et non vides
- **Longueur optimale** : 10-70 caractères

## 🔧 Modification et extension

### Ajouter des validations personnalisées
Éditez `_validate_heading_hierarchy()` dans `seo_audit/analyzers.py` :

```python
def _validate_heading_hierarchy(self, headings: List[HeadingItem], result: PageResult):
    # Ajouter vos propres règles de validation
    # Exemple: détecter les titres avec des mots-clés spécifiques
    keyword_titles = [h for h in headings if 'mot-clé' in h.text.lower()]
    if not keyword_titles:
        issues.append("Aucun titre ne contient le mot-clé principal")
```

### Personnaliser l'affichage web
Modifiez les styles CSS dans `index.html` :

```css
.heading-item {
    /* Personnaliser l'affichage des titres */
    border-left: 3px solid #your-color;
}

.heading-level .badge {
    /* Personnaliser les badges H1-H6 */
    font-size: 0.8rem;
}
```

## 📈 Impact SEO

Cette fonctionnalité aide à :

- ✅ **Optimiser la structure** pour les moteurs de recherche
- ✅ **Améliorer l'accessibilité** pour les lecteurs d'écran  
- ✅ **Organiser le contenu** de manière logique
- ✅ **Détecter les erreurs** rapidement
- ✅ **Respecter les standards** HTML et SEO

La structure des titres est un **signal SEO important** qui aide Google et les autres moteurs de recherche à comprendre l'organisation de votre contenu.