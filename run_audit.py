#!/usr/bin/env python3
"""
Script de lancement simple pour l'outil d'audit SEO
"""

import sys
import os
import json
from pathlib import Path

# Ajouter le répertoire courant au PATH Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def generate_web_files(engine, results, domain):
    """Génère les fichiers JSON pour l'interface web statique"""
    
    # Créer le dossier web_data s'il n'existe pas
    web_data_dir = Path(__file__).parent / 'web_data'
    web_data_dir.mkdir(exist_ok=True)
    
    # Générer les données pour l'interface web
    web_data = {
        'metadata': {
            'domain': domain,
            'analysis_date': results[0].crawled_at.isoformat() if results else None,
            'total_pages': len(results),
            'analysis_id': f"audit_{int(results[0].crawled_at.timestamp())}" if results else None
        },
        'summary': {
            'total_pages': engine.get_summary().total_pages,
            'pages_with_issues': engine.get_summary().pages_with_issues,
            'avg_response_time': engine.get_summary().avg_response_time,
            'total_issues': engine.get_summary().total_issues,
            'top_issues': engine.get_top_issues(10),
            'status_codes': dict(engine.get_summary().status_codes)
        },
        'pages': []
    }
    
    # Convertir les résultats
    for result in results:
        page_data = {
            'url': result.url,
            'status': result.status,
            'responseTime': result.response_ms,
            'title': result.title,
            'titleLen': result.title_len,
            'metaDesc': result.meta_desc,
            'metaDescLen': result.meta_desc_len,
            'h1Count': result.h1_count,
            'canonical': result.canonical,
            'canonicalOk': result.canonical_ok,
            'robotsMeta': result.robots_meta,
            'noindex': result.noindex,
            'nofollow': result.nofollow,
            'imgNoAlt': result.img_no_alt,
            'linksInternal': result.links_internal,
            'linksExternal': result.links_external,
            'wordCount': result.word_count,
            'issues': result.issues,
            'issuesCount': len(result.issues),
            'redirectChain': result.redirect_chain,
            'hreflangCount': result.hreflang_count,
            'structuredDataCount': result.structured_data_count,
            'htmlSize': result.html_size,
            'isCompressed': result.is_compressed,
            'cacheHeaders': result.cache_headers,
            'crawledAt': result.crawled_at.isoformat(),
            # Heading structure
            'headingsStructure': [
                {
                    'level': h.level,
                    'text': h.text,
                    'position': h.position
                } for h in result.headings_structure
            ],
            'headingsHierarchyIssues': result.headings_hierarchy_issues
        }
        web_data['pages'].append(page_data)
    
    # Sauvegarder les données principales
    main_file = web_data_dir / 'latest_analysis.json'
    with open(main_file, 'w', encoding='utf-8') as f:
        json.dump(web_data, f, ensure_ascii=False, indent=2)
    
    # Sauvegarder l'historique
    history_file = web_data_dir / 'analysis_history.json'
    history = []
    if history_file.exists():
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            history = []
    
    # Ajouter l'analyse actuelle
    history_entry = {
        'id': web_data['metadata']['analysis_id'],
        'domain': domain,
        'date': web_data['metadata']['analysis_date'],
        'summary': web_data['summary']
    }
    
    # Garder seulement les 20 dernières analyses
    history.insert(0, history_entry)
    history = history[:20]
    
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Fichiers web générés dans {web_data_dir}")
    print(f"📊 {len(results)} pages analysées")
    print(f"📁 Fichier principal: {main_file}")

try:
    from seo_audit.cli import main
    from seo_audit.models import AuditConfig
    from seo_audit.audit_engine import SEOAuditEngine
    
    if __name__ == "__main__":
        # Vérifier si c'est pour la génération web
        if len(sys.argv) > 1 and '--web-output' in sys.argv:
            # Mode génération pour interface web
            domain = None
            for arg in sys.argv[1:]:
                if arg.startswith('http'):
                    domain = arg
                    break
            
            if not domain:
                print("❌ Domaine requis pour la génération web")
                print("Usage: python3 run_audit.py https://example.com --web-output")
                sys.exit(1)
            
            # Configuration par défaut pour le web
            config = AuditConfig(
                domain=domain,
                max_pages=20,
                rate_limit=1.0,
                output_format='json'
            )
            
            # Créer et lancer l'engine
            engine = SEOAuditEngine(config)
            
            if not engine.validate_config():
                sys.exit(1)
            
            print(f"🚀 Analyse SEO pour interface web : {domain}")
            
            # Lancer l'analyse avec progression
            def progress_callback(current, total, url):
                percentage = (current / total) * 100
                print(f"[{current}/{total}] ({percentage:.1f}%) {url}")
            
            results = engine.run_audit(progress_callback)
            
            # Générer les fichiers pour l'interface web
            generate_web_files(engine, results, domain)
            
            print("\n🌐 Interface web prête !")
            print("Ouvrez index.html dans votre navigateur")
            
        elif len(sys.argv) == 1:
            print("🔍 Outil d'audit SEO")
            print("\nUsage:")
            print("  python3 run_audit.py <domain> [options]    # Analyse normale")
            print("  python3 run_audit.py <domain> --web-output # Génération pour interface web")
            print("\nExemples:")
            print("  python3 run_audit.py https://httpbin.org")
            print("  python3 run_audit.py https://example.com --limit 50 --format json")
            print("  python3 run_audit.py https://example.com --web-output")
            print("\nPour voir toutes les options:")
            print("  python3 run_audit.py --help")
            sys.exit(0)
        else:
            # Mode CLI normal
            main()

except ImportError as e:
    print("❌ Erreur d'import:", e)
    print("\n🔧 Installez d'abord les dépendances:")
    print("   python3 install.py")
    print("\nOu manuellement:")
    print("   pip3 install requests selectolax urllib3 pandas")
    sys.exit(1)