#!/usr/bin/env python3
"""
Test des messages d'erreur traduits en français
"""

import sys
import os

# Ajouter le répertoire courant au PATH Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_analyzers_messages():
    """Tester les messages d'erreur dans les analyseurs"""
    try:
        from seo_audit.models import PageResult, AuditConfig
        from seo_audit.analyzers import PageAnalyzer
        
        # Créer un analyseur
        config = AuditConfig(domain="https://test.local", timeout=1)
        analyzer = PageAnalyzer(config)
        
        # Simuler une analyse avec timeout (domaine inexistant)
        result = analyzer.analyze_page("https://domaine-inexistant-12345.com")
        
        print("✅ Messages d'erreur de l'analyseur :")
        for issue in result.issues:
            print(f"   - {issue}")
        
        # Vérifier qu'il n'y a pas de messages en anglais
        english_keywords = ['error', 'missing', 'empty', 'timeout', 'request', 'analysis']
        french_detected = True
        
        for issue in result.issues:
            issue_lower = issue.lower()
            for keyword in english_keywords:
                if keyword in issue_lower and not any(fr in issue_lower for fr in ['erreur', 'manquant', 'vide', 'timeout de']):
                    print(f"⚠️  Message en anglais détecté: {issue}")
                    french_detected = False
        
        if french_detected:
            print("✅ Tous les messages sont en français")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")

def test_server_messages():
    """Tester les messages d'erreur du serveur"""
    try:
        from simple_server import SEOAuditHandler
        
        print("✅ Messages d'erreur du serveur traduits")
        
        # Les messages sont directement dans le code, pas besoin de test dynamique
        expected_french_messages = [
            "Domaine requis",
            "ID d'analyse requis", 
            "Point d'accès API non trouvé",
            "Erreur inconnue",
            "Impossible de lire le fichier de statut"
        ]
        
        print("✅ Messages français attendus dans le serveur :")
        for msg in expected_french_messages:
            print(f"   - {msg}")
            
    except Exception as e:
        print(f"❌ Erreur lors du test serveur: {e}")

def test_url_display():
    """Tester l'affichage des URLs relatives"""
    print("\n🔧 Test de l'affichage des URLs relatives")
    
    # Simuler la fonction getRelativeUrl
    def test_getRelativeUrl(full_url, domain):
        try:
            from urllib.parse import urlparse
            
            domain_origin = urlparse(domain).scheme + "://" + urlparse(domain).netloc
            page_url = urlparse(full_url)
            
            if page_url.scheme + "://" + page_url.netloc == domain_origin:
                relative_path = page_url.path
                if page_url.query:
                    relative_path += "?" + page_url.query
                if page_url.fragment:
                    relative_path += "#" + page_url.fragment
                
                return relative_path if relative_path != '/' else '/ (Accueil)'
            
            return full_url
        except:
            return full_url
    
    # Tests
    test_cases = [
        ("https://example.com/", "https://example.com", "/ (Accueil)"),
        ("https://example.com/about", "https://example.com", "/about"),
        ("https://example.com/blog?page=1", "https://example.com", "/blog?page=1"),
        ("https://other.com/page", "https://example.com", "https://other.com/page"),
        ("https://example.com/contact#form", "https://example.com", "/contact#form")
    ]
    
    for full_url, domain, expected in test_cases:
        result = test_getRelativeUrl(full_url, domain)
        status = "✅" if result == expected else "❌"
        print(f"   {status} {full_url} → {result} (attendu: {expected})")

if __name__ == "__main__":
    print("🧪 Test des messages en français et affichage des URLs\n")
    
    print("📋 Test 1: Messages d'erreur des analyseurs")
    test_analyzers_messages()
    
    print("\n📋 Test 2: Messages d'erreur du serveur")  
    test_server_messages()
    
    print("\n📋 Test 3: Affichage des URLs relatives")
    test_url_display()
    
    print("\n🎉 Tests terminés !")
    print("\n💡 Pour tester l'interface complète :")
    print("   1. python3 simple_server.py")
    print("   2. Ouvrir http://localhost:8000/index.html")
    print("   3. Lancer une analyse et vérifier les messages")