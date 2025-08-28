#!/usr/bin/env python3
"""
Simple HTTP server pour lancer les analyses SEO depuis l'interface web
"""

import json
import os
import sys
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import subprocess
from pathlib import Path

# Ajouter le répertoire courant au PATH Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class SEOAuditHandler(SimpleHTTPRequestHandler):
    """Handler HTTP personnalisé pour les analyses SEO"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)
    
    def end_headers(self):
        # Ajouter les headers CORS pour les requêtes cross-origin
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        """Gérer les requêtes OPTIONS pour CORS"""
        self.send_response(200)
        self.end_headers()
    
    def do_POST(self):
        """Gérer les requêtes POST pour lancer les analyses"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/start-analysis':
            self.handle_start_analysis()
        elif parsed_path.path == '/api/analysis-status':
            self.handle_analysis_status()
        elif parsed_path.path == '/api/export-pdf':
            self.handle_export_pdf()
        else:
            self.send_error(404, 'Point d\'accès API non trouvé')
    
    def do_GET(self):
        """Gérer les requêtes GET"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/check-data':
            self.handle_check_data()
        else:
            # Servir les fichiers statiques normalement
            super().do_GET()
    
    def handle_start_analysis(self):
        """Lancer une analyse SEO en arrière-plan"""
        try:
            # Lire les données POST
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            
            domain = data.get('domain')
            max_pages = data.get('maxPages', 20)
            
            if not domain:
                self.send_json_response({'error': 'Domaine requis'}, 400)
                return
            
            # Créer un ID d'analyse unique
            analysis_id = f"analysis_{int(time.time())}"
            
            # Marquer l'analyse comme en cours
            self.save_analysis_status(analysis_id, 'running', domain)
            
            # Lancer l'analyse en arrière-plan
            def run_analysis():
                try:
                    # Exécuter le script Python d'analyse
                    cmd = [
                        sys.executable, 'run_audit.py', 
                        domain, '--web-output'
                    ]
                    
                    process = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        cwd=os.path.dirname(os.path.abspath(__file__))
                    )
                    
                    if process.returncode == 0:
                        self.save_analysis_status(analysis_id, 'completed', domain)
                    else:
                        error_msg = process.stderr or 'Erreur inconnue'
                        self.save_analysis_status(analysis_id, 'error', domain, error_msg)
                        
                except Exception as e:
                    self.save_analysis_status(analysis_id, 'error', domain, str(e))
            
            # Démarrer le thread d'analyse
            analysis_thread = threading.Thread(target=run_analysis)
            analysis_thread.daemon = True
            analysis_thread.start()
            
            # Réponse immédiate
            self.send_json_response({
                'status': 'started',
                'analysis_id': analysis_id,
                'message': f'Analyse de {domain} démarrée'
            })
            
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def handle_analysis_status(self):
        """Vérifier le statut d'une analyse"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            
            analysis_id = data.get('analysis_id')
            if not analysis_id:
                self.send_json_response({'error': 'ID d\'analyse requis'}, 400)
                return
            
            status = self.get_analysis_status(analysis_id)
            self.send_json_response(status)
            
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def handle_export_pdf(self):
        """Exporter l'analyse en PDF"""
        try:
            # Vérifier si ReportLab est disponible
            try:
                from seo_audit.pdf_generator import SEOAuditPDFGenerator
            except ImportError:
                self.send_json_response({
                    'error': 'ReportLab non installé',
                    'message': 'Installez ReportLab avec: pip install reportlab'
                }, 500)
                return
            
            # Vérifier que les données d'analyse existent
            web_data_file = Path('web_data/latest_analysis.json')
            if not web_data_file.exists():
                self.send_json_response({
                    'error': 'Aucune analyse disponible',
                    'message': 'Lancez d\'abord une analyse SEO'
                }, 400)
                return
            
            # Charger les données
            with open(web_data_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            
            # Générer le nom du fichier PDF
            domain_name = analysis_data['metadata']['domain'].replace('https://', '').replace('http://', '').replace('/', '_')
            timestamp = int(time.time())
            pdf_filename = f"audit_seo_{domain_name}_{timestamp}.pdf"
            pdf_path = Path('web_data') / pdf_filename
            
            # Générer le PDF
            generator = SEOAuditPDFGenerator()
            success = generator.generate_report(analysis_data, str(pdf_path))
            
            if success and pdf_path.exists():
                # Calculer la taille du fichier
                file_size = pdf_path.stat().st_size
                
                self.send_json_response({
                    'success': True,
                    'filename': pdf_filename,
                    'size': file_size,
                    'download_url': f'/web_data/{pdf_filename}',
                    'message': 'Rapport PDF généré avec succès'
                })
            else:
                self.send_json_response({
                    'error': 'Erreur lors de la génération PDF',
                    'message': 'Vérifiez les logs pour plus d\'informations'
                }, 500)
                
        except Exception as e:
            self.send_json_response({'error': f'Erreur PDF: {str(e)}'}, 500)
    
    def handle_check_data(self):
        """Vérifier si des données d'analyse sont disponibles"""
        try:
            web_data_file = Path('web_data/latest_analysis.json')
            
            if web_data_file.exists():
                # Lire les métadonnées
                with open(web_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.send_json_response({
                    'available': True,
                    'domain': data['metadata']['domain'],
                    'total_pages': data['metadata']['total_pages'],
                    'analysis_date': data['metadata']['analysis_date']
                })
            else:
                self.send_json_response({'available': False})
                
        except Exception as e:
            self.send_json_response({'available': False, 'error': str(e)})
    
    def save_analysis_status(self, analysis_id, status, domain, error=None):
        """Sauvegarder le statut d'une analyse"""
        status_file = Path('web_data/analysis_status.json')
        status_file.parent.mkdir(exist_ok=True)
        
        status_data = {
            'analysis_id': analysis_id,
            'status': status,  # running, completed, error
            'domain': domain,
            'timestamp': time.time(),
            'error': error
        }
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, ensure_ascii=False, indent=2)
    
    def get_analysis_status(self, analysis_id):
        """Récupérer le statut d'une analyse"""
        status_file = Path('web_data/analysis_status.json')
        
        if not status_file.exists():
            return {'status': 'not_found'}
        
        try:
            with open(status_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'status': 'error', 'error': 'Impossible de lire le fichier de statut'}
    
    def send_json_response(self, data, status_code=200):
        """Envoyer une réponse JSON"""
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(json_data.encode('utf-8'))))
        self.end_headers()
        
        self.wfile.write(json_data.encode('utf-8'))


def main():
    """Démarrer le serveur"""
    port = 8000
    
    # Chercher un port libre
    while True:
        try:
            server = HTTPServer(('localhost', port), SEOAuditHandler)
            break
        except OSError:
            port += 1
            if port > 8010:
                print("❌ Impossible de trouver un port libre")
                return
    
    print(f"🚀 Serveur SEO Audit démarré sur http://localhost:{port}")
    print(f"📱 Interface web : http://localhost:{port}/index.html")
    print(f"🔧 API disponible sur /api/")
    print("\n💡 Vous pouvez maintenant lancer des analyses directement depuis l'interface web !")
    print("🛑 Appuyez sur Ctrl+C pour arrêter le serveur\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur...")
        server.shutdown()


if __name__ == '__main__':
    main()