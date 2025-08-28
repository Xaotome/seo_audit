#!/usr/bin/env python3
"""
Installation des dépendances pour l'export PDF
"""

import subprocess
import sys
import os

def install_reportlab():
    """Installer ReportLab pour la génération PDF"""
    print("🔧 Installation de ReportLab pour l'export PDF...")
    
    try:
        # Essayer d'importer ReportLab
        import reportlab
        print("✅ ReportLab est déjà installé")
        return True
    except ImportError:
        pass
    
    try:
        # Installer ReportLab
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', 
            'reportlab', '--upgrade'
        ])
        
        # Vérifier l'installation
        import reportlab
        print("✅ ReportLab installé avec succès !")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation: {e}")
        return False
    except ImportError:
        print("❌ Installation échouée - ReportLab non disponible")
        return False

def test_pdf_generation():
    """Tester la génération PDF"""
    try:
        from seo_audit.pdf_generator import SEOAuditPDFGenerator
        
        # Données de test
        test_data = {
            'metadata': {
                'domain': 'https://test.example.com',
                'analysis_date': '2024-01-15T10:30:00',
                'total_pages': 5,
                'analysis_id': 'test_audit'
            },
            'summary': {
                'total_pages': 5,
                'pages_with_issues': 2,
                'avg_response_time': 456,
                'total_issues': 8,
                'top_issues': [
                    ['Titre manquant', 2],
                    ['Meta description manquante', 1]
                ],
                'status_codes': {'200': 4, '404': 1}
            },
            'pages': [
                {
                    'url': 'https://test.example.com/',
                    'status': 200,
                    'responseTime': 234,
                    'title': 'Accueil - Test Site',
                    'titleLen': 19,
                    'metaDesc': 'Site de test pour l\'audit SEO',
                    'metaDescLen': 28,
                    'h1Count': 1,
                    'wordCount': 450,
                    'issues': [],
                    'issuesCount': 0,
                    'headingsStructure': [
                        {'level': 1, 'text': 'Bienvenue', 'position': 0},
                        {'level': 2, 'text': 'À propos', 'position': 1}
                    ],
                    'headingsHierarchyIssues': [],
                    'imgNoAlt': 0,
                    'linksInternal': 3,
                    'linksExternal': 1,
                    'htmlSize': 12450,
                    'isCompressed': True
                },
                {
                    'url': 'https://test.example.com/about',
                    'status': 200,
                    'responseTime': 367,
                    'title': '',
                    'titleLen': 0,
                    'metaDesc': '',
                    'metaDescLen': 0,
                    'h1Count': 0,
                    'wordCount': 89,
                    'issues': ['Titre manquant', 'H1 manquant', 'Meta description manquante'],
                    'issuesCount': 3,
                    'headingsStructure': [],
                    'headingsHierarchyIssues': ['Aucun titre trouvé'],
                    'imgNoAlt': 2,
                    'linksInternal': 1,
                    'linksExternal': 0,
                    'htmlSize': 3420,
                    'isCompressed': False
                }
            ]
        }
        
        # Générer un PDF de test
        generator = SEOAuditPDFGenerator()
        test_file = 'test_report.pdf'
        
        success = generator.generate_report(test_data, test_file)
        
        if success and os.path.exists(test_file):
            file_size = os.path.getsize(test_file)
            print(f"✅ PDF de test généré : {test_file} ({file_size} octets)")
            
            # Nettoyer le fichier de test
            os.remove(test_file)
            return True
        else:
            print("❌ Erreur lors de la génération du PDF de test")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test PDF: {e}")
        return False

def main():
    """Installation et test des fonctionnalités PDF"""
    print("🚀 Configuration de l'export PDF pour l'audit SEO\n")
    
    # Étape 1: Installer ReportLab
    if not install_reportlab():
        print("\n❌ Impossible d'installer ReportLab")
        print("Essayez manuellement :")
        print("   pip install reportlab")
        sys.exit(1)
    
    print()
    
    # Étape 2: Tester la génération PDF
    if not test_pdf_generation():
        print("\n❌ Le test de génération PDF a échoué")
        sys.exit(1)
    
    print("\n🎉 Configuration PDF terminée avec succès !")
    print("\n📋 Fonctionnalités disponibles :")
    print("   ✅ Génération de rapports PDF complets")
    print("   ✅ Export via l'interface web (mode serveur)")
    print("   ✅ Rapports avec résumé exécutif et détails par page")
    print("   ✅ Structure des titres et recommandations")
    
    print("\n🚀 Pour utiliser l'export PDF :")
    print("   1. python3 simple_server.py")
    print("   2. Ouvrir http://localhost:8000/index.html")  
    print("   3. Lancer une analyse SEO")
    print("   4. Cliquer sur le bouton 'PDF' pour télécharger le rapport")
    
    print("\n💡 Le rapport PDF contient :")
    print("   📄 Page de couverture avec résumé")
    print("   📊 Résumé exécutif détaillé")
    print("   📈 Analyse globale et statistiques")
    print("   🔝 Top des problèmes avec recommandations")
    print("   📝 Détail complet de chaque page")
    print("   🎯 Recommandations personnalisées")

if __name__ == '__main__':
    main()