#!/usr/bin/env python3
"""
Script de démarrage simplifié pour l'interface web SEO Audit Tool
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🌐 SEO Audit Tool - Interface Web")
    print("=" * 50)
    
    # Vérifier la structure du projet
    project_root = Path(__file__).parent
    web_interface_dir = project_root / "web_interface"
    
    if not web_interface_dir.exists():
        print("❌ Répertoire web_interface introuvable")
        sys.exit(1)
    
    # Changer vers le répertoire web
    os.chdir(str(web_interface_dir))
    
    # Vérifier les dépendances Python
    try:
        import flask
        import flask_socketio
        print("✅ Dépendances Flask détectées")
    except ImportError:
        print("📦 Installation des dépendances web...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "flask", "flask-socketio", "eventlet"
            ])
            print("✅ Dépendances installées")
        except subprocess.CalledProcessError:
            print("❌ Erreur lors de l'installation des dépendances")
            print("Installez manuellement : pip3 install flask flask-socketio eventlet")
            sys.exit(1)
    
    # Lancer l'interface web
    print("\n🚀 Démarrage de l'interface web...")
    print("📍 Interface disponible sur : http://localhost:5000")
    print("⚠️  Utilisez Ctrl+C pour arrêter le serveur\n")
    
    try:
        # Utiliser le script de lancement dédié
        subprocess.run([sys.executable, "run_web.py"])
    except KeyboardInterrupt:
        print("\n👋 Interface web arrêtée")
    except Exception as e:
        print(f"❌ Erreur : {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()