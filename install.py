#!/usr/bin/env python3
"""
Script d'installation des dépendances pour l'outil d'audit SEO
"""

import subprocess
import sys
import os


def install_requirements():
    """Installer les dépendances depuis requirements.txt"""
    print("🔧 Installation des dépendances...")
    
    try:
        # Installer les dépendances
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dépendances installées avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation: {e}")
        return False


def test_imports():
    """Tester les imports principaux"""
    print("🧪 Test des imports...")
    
    try:
        # Test des imports essentiels
        import requests
        print("✅ requests")
        
        import selectolax
        print("✅ selectolax")
        
        # Test de notre package
        from seo_audit.models import PageResult
        print("✅ seo_audit.models")
        
        from seo_audit.utils import normalize_url
        print("✅ seo_audit.utils")
        
        return True
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False


def main():
    """Fonction principale"""
    print("🚀 Installation de l'outil d'audit SEO")
    print("=" * 50)
    
    # Vérifier si nous sommes dans le bon répertoire
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt non trouvé")
        print("Veuillez lancer ce script depuis le répertoire racine du projet")
        return
    
    # Installer les dépendances
    if not install_requirements():
        return
    
    print()
    
    # Tester les imports
    if test_imports():
        print("\n🎉 Installation réussie !")
        print("\nVous pouvez maintenant utiliser l'outil :")
        print("python3 -m seo_audit.cli https://example.com")
        print("ou")
        print("python3 example.py")
    else:
        print("\n❌ Problème lors des tests d'import")


if __name__ == "__main__":
    main()