# Makefile pour l'outil d'audit SEO

.PHONY: help install test clean run example

# Variables
PYTHON := python3
DOMAIN := https://httpbin.org

help:	## Afficher cette aide
	@echo "🔍 SEO Audit Tool - Commandes disponibles:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:	## Installer les dépendances
	$(PYTHON) install.py

test:	## Lancer les tests unitaires
	$(PYTHON) -m pytest tests/ -v

test-basic:	## Tester les imports de base
	$(PYTHON) -c "from seo_audit.models import PageResult; print('✅ Tests de base OK')"

run:	## Lancer un audit sur le domaine par défaut
	$(PYTHON) run_audit.py $(DOMAIN) --limit 5 --verbose

example:	## Lancer l'exemple programmatique
	$(PYTHON) example.py

audit:	## Audit personnalisé (make audit DOMAIN=https://example.com)
	$(PYTHON) run_audit.py $(DOMAIN) --limit 10 --format html --verbose

clean:	## Nettoyer les fichiers temporaires
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -f *.csv *.json *.html audit_*

structure:	## Afficher la structure du projet
	@echo "📁 Structure du projet:"
	@tree -I '__pycache__|*.pyc|*.csv|*.json|*.html' || find . -type f -name "*.py" | head -20

demo:	## Démonstration complète de l'outil
	@echo "🚀 Démonstration de l'outil d'audit SEO"
	@echo "1. Test des imports..."
	@$(PYTHON) -c "from seo_audit.models import PageResult; print('✅ Imports OK')"
	@echo "2. Aide de la CLI..."
	@$(PYTHON) run_audit.py --help | head -10
	@echo "3. Audit exemple (limité à 3 pages)..."
	@$(PYTHON) run_audit.py $(DOMAIN) --limit 3 --verbose