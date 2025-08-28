#!/usr/bin/env python3
"""
Script de lancement pour l'interface web
"""

import os
import sys
import subprocess

def check_dependencies():
    """Vérifier les dépendances web"""
    try:
        import flask
        import flask_socketio
        print("✅ Flask et Flask-SocketIO sont installés")
        return True
    except ImportError as e:
        print(f"❌ Dépendances manquantes: {e}")
        print("\n🔧 Installation des dépendances web...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements_web.txt"
            ])
            print("✅ Dépendances web installées")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors de l'installation: {e}")
            return False

def main():
    print("🌐 SEO Audit Tool - Interface Web")
    print("=" * 50)
    
    # Vérifier les dépendances
    if not check_dependencies():
        print("\n❌ Impossible de démarrer l'interface web")
        print("Installez manuellement les dépendances :")
        print("pip3 install flask flask-socketio")
        sys.exit(1)
    
    # Changer vers le répertoire de l'interface web
    web_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(web_dir)
    
    # Importer et lancer l'application
    try:
        from app import app, socketio
        
        print("\n🚀 Démarrage de l'interface web...")
        print("📍 URL: http://localhost:5000")
        print("⚠️  Utilisez Ctrl+C pour arrêter le serveur")
        print()
        
        # Lancer le serveur
        socketio.run(
            app,
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=True
        )
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()