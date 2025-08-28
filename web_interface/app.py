#!/usr/bin/env python3
"""
Interface web pour l'outil d'audit SEO
"""

import os
import sys
import json
import uuid
import threading
import time
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file
from flask_socketio import SocketIO, emit

# Ajouter le répertoire parent au path pour importer seo_audit
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seo_audit.models import AuditConfig
from seo_audit.audit_engine import SEOAuditEngine
from seo_audit.utils import normalize_url, is_valid_url

app = Flask(__name__)
app.secret_key = 'seo-audit-secret-key-change-in-production'
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration
RESULTS_DIR = Path(__file__).parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

# Stockage des analyses en cours
active_analyses = {}
completed_analyses = {}


class WebProgressCallback:
    """Callback pour envoyer les mises à jour de progression via WebSocket"""
    
    def __init__(self, analysis_id, socketio_instance):
        self.analysis_id = analysis_id
        self.socketio = socketio_instance
        self.start_time = time.time()
    
    def __call__(self, current, total, url):
        """Appelé pour chaque page analysée"""
        elapsed = time.time() - self.start_time
        progress = (current / total) * 100
        
        self.socketio.emit('progress_update', {
            'analysis_id': self.analysis_id,
            'current': current,
            'total': total,
            'progress': progress,
            'url': url,
            'elapsed': elapsed,
            'eta': (elapsed / current * total - elapsed) if current > 0 else 0
        })


def run_seo_analysis(analysis_id, domain, options):
    """Exécuter l'analyse SEO en arrière-plan"""
    try:
        # Marquer l'analyse comme en cours
        active_analyses[analysis_id] = {
            'domain': domain,
            'start_time': datetime.now(),
            'status': 'running',
            'progress': 0
        }
        
        # Configuration de l'audit
        config = AuditConfig(
            domain=domain,
            max_pages=options.get('max_pages', 100),
            rate_limit=options.get('rate_limit', 1.0),
            timeout=options.get('timeout', 15),
            output_format='json',
            follow_redirects=options.get('follow_redirects', True),
            include_images=options.get('include_images', True)
        )
        
        # Créer l'engine d'audit
        engine = SEOAuditEngine(config)
        
        if not engine.validate_config():
            raise ValueError("Configuration d'audit invalide")
        
        # Callback pour les mises à jour de progression
        progress_callback = WebProgressCallback(analysis_id, socketio)
        
        # Lancer l'analyse
        results = engine.run_audit(progress_callback=progress_callback)
        
        # Sauvegarder les résultats
        results_file = RESULTS_DIR / f"{analysis_id}.json"
        engine.export_results(str(results_file.with_suffix('')))
        
        # Générer le rapport HTML
        html_file = RESULTS_DIR / f"{analysis_id}.html"
        engine.report_generator.generate_html_report(
            results, 
            engine.get_summary(), 
            str(html_file)
        )
        
        # Marquer comme terminé
        completed_analyses[analysis_id] = {
            'domain': domain,
            'start_time': active_analyses[analysis_id]['start_time'],
            'end_time': datetime.now(),
            'status': 'completed',
            'results_count': len(results),
            'summary': {
                'total_pages': engine.get_summary().total_pages,
                'pages_with_issues': engine.get_summary().pages_with_issues,
                'avg_response_time': engine.get_summary().avg_response_time,
                'total_issues': engine.get_summary().total_issues,
                'top_issues': engine.get_top_issues(5)
            },
            'results_file': f"{analysis_id}.json",
            'html_file': f"{analysis_id}.html"
        }
        
        # Supprimer de la liste active
        if analysis_id in active_analyses:
            del active_analyses[analysis_id]
        
        # Envoyer la notification de fin
        socketio.emit('analysis_complete', {
            'analysis_id': analysis_id,
            'status': 'completed',
            'results_count': len(results)
        })
        
    except Exception as e:
        # Marquer comme échoué
        completed_analyses[analysis_id] = {
            'domain': domain,
            'start_time': active_analyses.get(analysis_id, {}).get('start_time', datetime.now()),
            'end_time': datetime.now(),
            'status': 'error',
            'error': str(e)
        }
        
        # Supprimer de la liste active
        if analysis_id in active_analyses:
            del active_analyses[analysis_id]
        
        # Envoyer la notification d'erreur
        socketio.emit('analysis_error', {
            'analysis_id': analysis_id,
            'error': str(e)
        })


@app.route('/')
def index():
    """Page d'accueil avec le formulaire d'analyse"""
    return render_template('index.html')


@app.route('/start_analysis', methods=['POST'])
def start_analysis():
    """Démarrer une nouvelle analyse"""
    domain = request.form.get('domain', '').strip()
    
    if not domain:
        flash('Veuillez saisir un domaine', 'error')
        return redirect(url_for('index'))
    
    # Normaliser et valider l'URL
    try:
        normalized_domain = normalize_url(domain)
        if not is_valid_url(normalized_domain):
            flash('URL invalide', 'error')
            return redirect(url_for('index'))
    except Exception:
        flash('URL invalide', 'error')
        return redirect(url_for('index'))
    
    # Options de l'analyse
    options = {
        'max_pages': min(int(request.form.get('max_pages', 100)), 500),  # Limiter à 500
        'rate_limit': float(request.form.get('rate_limit', 1.0)),
        'timeout': int(request.form.get('timeout', 15)),
        'follow_redirects': request.form.get('follow_redirects') == 'on',
        'include_images': request.form.get('include_images') == 'on'
    }
    
    # Générer un ID unique pour l'analyse
    analysis_id = str(uuid.uuid4())
    
    # Stocker l'ID dans la session
    session['current_analysis'] = analysis_id
    
    # Lancer l'analyse en arrière-plan
    thread = threading.Thread(
        target=run_seo_analysis,
        args=(analysis_id, normalized_domain, options)
    )
    thread.daemon = True
    thread.start()
    
    return redirect(url_for('analysis_progress', analysis_id=analysis_id))


@app.route('/analysis/<analysis_id>')
def analysis_progress(analysis_id):
    """Page de progression de l'analyse"""
    # Vérifier si l'analyse existe
    if analysis_id not in active_analyses and analysis_id not in completed_analyses:
        flash('Analyse introuvable', 'error')
        return redirect(url_for('index'))
    
    return render_template('progress.html', analysis_id=analysis_id)


@app.route('/results/<analysis_id>')
def view_results(analysis_id):
    """Afficher les résultats d'une analyse"""
    if analysis_id not in completed_analyses:
        flash('Résultats introuvables', 'error')
        return redirect(url_for('index'))
    
    analysis_data = completed_analyses[analysis_id]
    
    if analysis_data['status'] == 'error':
        flash(f"Erreur lors de l'analyse : {analysis_data['error']}", 'error')
        return redirect(url_for('index'))
    
    # Charger les résultats JSON
    results_file = RESULTS_DIR / analysis_data['results_file']
    try:
        with open(results_file, 'r', encoding='utf-8') as f:
            results_data = json.load(f)
    except Exception as e:
        flash(f'Erreur lors du chargement des résultats : {e}', 'error')
        return redirect(url_for('index'))
    
    return render_template('results.html', 
                         analysis_data=analysis_data, 
                         results_data=results_data,
                         analysis_id=analysis_id)


@app.route('/results/<analysis_id>/download/<file_type>')
def download_results(analysis_id, file_type):
    """Télécharger les résultats"""
    if analysis_id not in completed_analyses:
        return jsonify({'error': 'Analyse introuvable'}), 404
    
    analysis_data = completed_analyses[analysis_id]
    
    if file_type == 'json':
        file_path = RESULTS_DIR / analysis_data['results_file']
    elif file_type == 'html':
        file_path = RESULTS_DIR / analysis_data['html_file']
    else:
        return jsonify({'error': 'Type de fichier invalide'}), 400
    
    if not file_path.exists():
        return jsonify({'error': 'Fichier introuvable'}), 404
    
    return send_file(str(file_path), as_attachment=True)


@app.route('/api/status/<analysis_id>')
def get_analysis_status(analysis_id):
    """API pour obtenir le statut d'une analyse"""
    if analysis_id in active_analyses:
        return jsonify({
            'status': 'running',
            'data': active_analyses[analysis_id]
        })
    elif analysis_id in completed_analyses:
        return jsonify({
            'status': 'completed',
            'data': completed_analyses[analysis_id]
        })
    else:
        return jsonify({'status': 'not_found'}), 404


@app.route('/page/<analysis_id>/<int:page_index>')
def view_page_details(analysis_id, page_index):
    """Afficher les détails d'une page spécifique"""
    if analysis_id not in completed_analyses:
        flash('Analyse introuvable', 'error')
        return redirect(url_for('index'))
    
    analysis_data = completed_analyses[analysis_id]
    
    if analysis_data['status'] == 'error':
        flash(f"Erreur lors de l'analyse : {analysis_data['error']}", 'error')
        return redirect(url_for('index'))
    
    # Charger les résultats JSON
    results_file = RESULTS_DIR / analysis_data['results_file']
    try:
        with open(results_file, 'r', encoding='utf-8') as f:
            results_data = json.load(f)
    except Exception as e:
        flash(f'Erreur lors du chargement des résultats : {e}', 'error')
        return redirect(url_for('index'))
    
    # Vérifier que l'index de page existe
    if page_index >= len(results_data['results']) or page_index < 0:
        flash('Page introuvable dans les résultats', 'error')
        return redirect(url_for('view_results', analysis_id=analysis_id))
    
    page_result = results_data['results'][page_index]
    
    return render_template('page_details.html',
                         analysis_data=analysis_data,
                         page_result=page_result,
                         page_index=page_index,
                         analysis_id=analysis_id,
                         total_pages=len(results_data['results']))


@app.route('/history')
def analysis_history():
    """Historique des analyses"""
    return render_template('history.html', 
                         active_analyses=active_analyses,
                         completed_analyses=completed_analyses)


@socketio.on('connect')
def handle_connect():
    """Gestion des connexions WebSocket"""
    print(f'Client connecté : {request.sid}')


@socketio.on('disconnect')
def handle_disconnect():
    """Gestion des déconnexions WebSocket"""
    print(f'Client déconnecté : {request.sid}')


@socketio.on('join_analysis')
def handle_join_analysis(data):
    """Rejoindre le suivi d'une analyse"""
    analysis_id = data.get('analysis_id')
    if analysis_id:
        # Envoyer le statut actuel
        if analysis_id in active_analyses:
            emit('analysis_status', {
                'analysis_id': analysis_id,
                'status': 'running',
                'data': active_analyses[analysis_id]
            })
        elif analysis_id in completed_analyses:
            emit('analysis_status', {
                'analysis_id': analysis_id,
                'status': 'completed',
                'data': completed_analyses[analysis_id]
            })


if __name__ == '__main__':
    print("🌐 Démarrage de l'interface web SEO Audit Tool")
    print("📍 Interface disponible sur : http://localhost:5000")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)