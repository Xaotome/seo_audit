#!/usr/bin/env python3
"""
Test de la fonctionnalité de structure des titres
"""

import sys
import os
import json

# Ajouter le répertoire courant au PATH Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test d'import
try:
    from seo_audit.models import HeadingItem, PageResult
    print("✅ Import des modèles HeadingItem et PageResult réussi")
except ImportError as e:
    print(f"❌ Erreur d'import des modèles: {e}")
    sys.exit(1)

# Test de création d'un HeadingItem
try:
    heading = HeadingItem(level=1, text="Test H1 Title", position=0)
    print(f"✅ HeadingItem créé: H{heading.level} - '{heading.text}' (pos: {heading.position})")
except Exception as e:
    print(f"❌ Erreur de création HeadingItem: {e}")
    sys.exit(1)

# Test de création d'un PageResult avec structure de titres
try:
    page_result = PageResult(url="https://test.com")
    page_result.headings_structure = [
        HeadingItem(level=1, text="Main Title", position=0),
        HeadingItem(level=2, text="Section 1", position=1),
        HeadingItem(level=3, text="Subsection 1.1", position=2),
        HeadingItem(level=2, text="Section 2", position=3),
    ]
    page_result.headings_hierarchy_issues = ["No issues found"]
    
    print(f"✅ PageResult créé avec {len(page_result.headings_structure)} titres")
    
    # Test de sérialisation JSON (pour vérifier la compatibilité web)
    headings_data = [
        {
            'level': h.level,
            'text': h.text,
            'position': h.position
        } for h in page_result.headings_structure
    ]
    
    json_data = json.dumps(headings_data, ensure_ascii=False, indent=2)
    print("✅ Sérialisation JSON réussie:")
    print(json_data)
    
except Exception as e:
    print(f"❌ Erreur de test PageResult: {e}")
    sys.exit(1)

print("\n🎉 Tous les tests de la structure des titres sont réussis !")
print("\n📋 Fonctionnalités testées :")
print("   - Modèle HeadingItem")
print("   - Structure de titres dans PageResult")
print("   - Sérialisation JSON pour l'interface web")
print("\n🚀 La fonctionnalité est prête à être utilisée !")

print("\n💡 Pour tester avec une vraie analyse:")
print("   python3 run_audit.py https://httpbin.org --web-output")
print("   Puis ouvrez index.html pour voir les détails des pages")