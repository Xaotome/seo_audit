#!/usr/bin/env python3
"""
Exemple d'utilisation de l'outil d'audit SEO
"""

from seo_audit.models import AuditConfig
from seo_audit.audit_engine import SEOAuditEngine


def run_example_audit():
    """Exemple d'audit SEO programmatique"""
    print("🔍 SEO Audit Tool - Exemple d'utilisation")
    print("=" * 50)
    
    # Configuration de l'audit
    config = AuditConfig(
        domain="https://httpbin.org",  # Site de test
        max_pages=5,  # Limiter pour l'exemple
        rate_limit=0.5,  # Plus lent pour être poli
        timeout=10,
        output_format="json"
    )
    
    print(f"🎯 Domaine cible: {config.domain}")
    print(f"📊 Pages maximum: {config.max_pages}")
    print(f"⏱️  Rate limit: {config.rate_limit} req/s")
    print()
    
    # Créer et lancer l'audit
    engine = SEOAuditEngine(config)
    
    if not engine.validate_config():
        print("❌ Configuration invalide")
        return
    
    try:
        # Lancer l'audit
        results = engine.run_audit()
        
        if results:
            print(f"\n✅ Audit terminé - {len(results)} pages analysées")
            
            # Exporter les résultats
            engine.export_results("example_audit")
            
            # Afficher quelques statistiques
            summary = engine.get_summary()
            print(f"📊 Pages avec problèmes: {summary.pages_with_issues}/{summary.total_pages}")
            print(f"⏱️  Temps de réponse moyen: {summary.avg_response_time:.0f}ms")
            
            # Top 3 des problèmes
            top_issues = engine.get_top_issues(3)
            if top_issues:
                print("\n🚨 Top 3 des problèmes:")
                for i, (issue, count) in enumerate(top_issues, 1):
                    print(f"   {i}. {issue}: {count} pages")
        else:
            print("⚠️ Aucune page analysée")
            
    except KeyboardInterrupt:
        print("\n🛑 Audit interrompu par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur: {e}")


if __name__ == "__main__":
    run_example_audit()