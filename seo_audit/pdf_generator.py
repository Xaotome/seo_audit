#!/usr/bin/env python3
"""
Générateur de rapports PDF pour l'audit SEO
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from urllib.parse import urlparse

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.platypus import PageBreak, Image, KeepTogether
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class SEOAuditPDFGenerator:
    """Générateur de rapports PDF pour l'audit SEO"""
    
    def __init__(self):
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab non disponible. Installez avec: pip install reportlab")
        
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Créer des styles personnalisés pour le PDF"""
        
        # Style pour le titre principal
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=20,
            textColor=colors.HexColor('#1f4e79'),
            alignment=TA_CENTER
        ))
        
        # Style pour les titres de section
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#2c5aa0'),
            borderWidth=1,
            borderColor=colors.HexColor('#2c5aa0'),
            borderPadding=5
        ))
        
        # Style pour les sous-titres
        self.styles.add(ParagraphStyle(
            name='SubTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=12,
            textColor=colors.HexColor('#444444')
        ))
        
        # Style pour le contenu normal
        self.styles.add(ParagraphStyle(
            name='Content',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY
        ))
        
        # Style pour les informations importantes
        self.styles.add(ParagraphStyle(
            name='Important',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            textColor=colors.HexColor('#d63384'),
            leftIndent=20
        ))
        
        # Style pour les URLs
        self.styles.add(ParagraphStyle(
            name='URL',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=4,
            textColor=colors.HexColor('#0066cc'),
            fontName='Courier'
        ))
    
    def generate_report(self, analysis_data: Dict[str, Any], output_path: str) -> bool:
        """Générer le rapport PDF complet"""
        try:
            # Créer le document PDF
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # Construire le contenu du rapport
            story = []
            
            # Page de couverture
            self._add_cover_page(story, analysis_data)
            story.append(PageBreak())
            
            # Résumé exécutif
            self._add_executive_summary(story, analysis_data)
            story.append(PageBreak())
            
            # Analyse globale
            self._add_global_analysis(story, analysis_data)
            story.append(PageBreak())
            
            # Top des problèmes
            self._add_top_issues(story, analysis_data)
            story.append(PageBreak())
            
            # Détail par page
            self._add_pages_details(story, analysis_data)
            
            # Recommandations
            story.append(PageBreak())
            self._add_recommendations(story, analysis_data)
            
            # Générer le PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Erreur lors de la génération PDF: {e}")
            return False
    
    def _add_cover_page(self, story: List, data: Dict[str, Any]):
        """Ajouter la page de couverture"""
        metadata = data.get('metadata', {})
        domain = metadata.get('domain', 'Site inconnu')
        analysis_date = metadata.get('analysis_date', '')
        total_pages = metadata.get('total_pages', 0)
        
        # Parse date for better formatting
        if analysis_date:
            try:
                date_obj = datetime.fromisoformat(analysis_date.replace('Z', '+00:00'))
                formatted_date = date_obj.strftime('%d/%m/%Y à %H:%M')
            except:
                formatted_date = analysis_date
        else:
            formatted_date = datetime.now().strftime('%d/%m/%Y à %H:%M')
        
        # Titre principal
        story.append(Spacer(1, 3*cm))
        story.append(Paragraph("RAPPORT D'AUDIT SEO", self.styles['MainTitle']))
        story.append(Spacer(1, 1*cm))
        
        # Informations du site
        story.append(Paragraph(f"<b>Site web :</b> {domain}", self.styles['SubTitle']))
        story.append(Paragraph(f"<b>Date d'analyse :</b> {formatted_date}", self.styles['Content']))
        story.append(Paragraph(f"<b>Pages analysées :</b> {total_pages}", self.styles['Content']))
        story.append(Spacer(1, 2*cm))
        
        # Résumé rapide
        summary = data.get('summary', {})
        pages_with_issues = summary.get('pages_with_issues', 0)
        total_issues = summary.get('total_issues', 0)
        avg_response_time = summary.get('avg_response_time', 0)
        
        summary_table = Table([
            ['📊 RÉSUMÉ RAPIDE', ''],
            ['Pages avec problèmes', f"{pages_with_issues}/{total_pages}"],
            ['Total des problèmes', str(total_issues)],
            ['Temps de réponse moyen', f"{avg_response_time:.0f} ms"],
            ['Statut global', self._get_global_status(pages_with_issues, total_pages)]
        ], colWidths=[4*cm, 6*cm])
        
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc'))
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 2*cm))
        
        # Pied de page
        story.append(Paragraph("Générée par l'outil d'Audit SEO", self.styles['Content']))
    
    def _add_executive_summary(self, story: List, data: Dict[str, Any]):
        """Ajouter le résumé exécutif"""
        story.append(Paragraph("RÉSUMÉ EXÉCUTIF", self.styles['SectionTitle']))
        
        metadata = data.get('metadata', {})
        summary = data.get('summary', {})
        
        # Informations générales
        story.append(Paragraph("Informations générales", self.styles['SubTitle']))
        
        domain_info = f"Cette analyse porte sur <b>{metadata.get('domain', 'N/A')}</b> "
        domain_info += f"et couvre <b>{metadata.get('total_pages', 0)} pages</b>. "
        domain_info += f"L'audit a identifié <b>{summary.get('total_issues', 0)} problèmes</b> "
        domain_info += f"répartis sur <b>{summary.get('pages_with_issues', 0)} pages</b>."
        
        story.append(Paragraph(domain_info, self.styles['Content']))
        story.append(Spacer(1, 0.5*cm))
        
        # Performance
        avg_time = summary.get('avg_response_time', 0)
        if avg_time > 0:
            perf_status = "excellente" if avg_time < 500 else "bonne" if avg_time < 1000 else "à améliorer"
            perf_color = "#28a745" if avg_time < 500 else "#ffc107" if avg_time < 1000 else "#dc3545"
            
            perf_info = f"La performance du site est <font color='{perf_color}'><b>{perf_status}</b></font> "
            perf_info += f"avec un temps de réponse moyen de <b>{avg_time:.0f} ms</b>."
            
            story.append(Paragraph("Performance", self.styles['SubTitle']))
            story.append(Paragraph(perf_info, self.styles['Content']))
            story.append(Spacer(1, 0.5*cm))
        
        # Priorités d'action
        top_issues = summary.get('top_issues', [])
        if top_issues:
            story.append(Paragraph("Priorités d'action", self.styles['SubTitle']))
            
            priority_text = "Les problèmes les plus fréquents nécessitant une attention immédiate sont :"
            story.append(Paragraph(priority_text, self.styles['Content']))
            
            for i, (issue, count) in enumerate(top_issues[:5], 1):
                story.append(Paragraph(f"{i}. <b>{issue}</b> ({count} occurrences)", self.styles['Important']))
        
        story.append(Spacer(1, 1*cm))
    
    def _add_global_analysis(self, story: List, data: Dict[str, Any]):
        """Ajouter l'analyse globale"""
        story.append(Paragraph("ANALYSE GLOBALE", self.styles['SectionTitle']))
        
        summary = data.get('summary', {})
        pages = data.get('pages', [])
        
        # Répartition des codes de statut
        status_codes = summary.get('status_codes', {})
        if status_codes:
            story.append(Paragraph("Codes de statut HTTP", self.styles['SubTitle']))
            
            status_data = [['Code de statut', 'Nombre de pages', 'Pourcentage']]
            total_pages = sum(status_codes.values())
            
            for code, count in sorted(status_codes.items()):
                percentage = (count / total_pages * 100) if total_pages > 0 else 0
                status_name = self._get_status_name(int(code))
                status_data.append([f"{code} - {status_name}", str(count), f"{percentage:.1f}%"])
            
            status_table = Table(status_data, colWidths=[5*cm, 3*cm, 3*cm])
            status_table.setStyle(self._get_table_style())
            story.append(status_table)
            story.append(Spacer(1, 0.5*cm))
        
        # Analyse des titres
        self._add_title_analysis(story, pages)
        
        # Analyse des meta descriptions
        self._add_meta_analysis(story, pages)
        
        # Analyse des images
        self._add_images_analysis(story, pages)
    
    def _add_top_issues(self, story: List, data: Dict[str, Any]):
        """Ajouter le top des problèmes"""
        story.append(Paragraph("TOP DES PROBLÈMES", self.styles['SectionTitle']))
        
        summary = data.get('summary', {})
        top_issues = summary.get('top_issues', [])
        
        if not top_issues:
            story.append(Paragraph("Aucun problème majeur détecté.", self.styles['Content']))
            return
        
        story.append(Paragraph("Les problèmes suivants ont été identifiés par ordre de fréquence :", self.styles['Content']))
        story.append(Spacer(1, 0.5*cm))
        
        # Table des problèmes
        issues_data = [['#', 'Problème', 'Occurrences', 'Impact']]
        
        for i, (issue, count) in enumerate(top_issues[:10], 1):
            impact = self._get_issue_impact(issue, count, len(data.get('pages', [])))
            issues_data.append([str(i), issue, str(count), impact])
        
        issues_table = Table(issues_data, colWidths=[1*cm, 8*cm, 2*cm, 2*cm])
        issues_table.setStyle(self._get_table_style())
        story.append(issues_table)
        
        # Recommandations par problème
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph("Explications et recommandations :", self.styles['SubTitle']))
        
        for i, (issue, count) in enumerate(top_issues[:5], 1):
            recommendation = self._get_issue_recommendation(issue)
            story.append(Paragraph(f"<b>{i}. {issue}</b>", self.styles['Content']))
            story.append(Paragraph(recommendation, self.styles['Content']))
            story.append(Spacer(1, 0.3*cm))
    
    def _add_pages_details(self, story: List, data: Dict[str, Any]):
        """Ajouter les détails de chaque page"""
        story.append(Paragraph("DÉTAIL PAR PAGE", self.styles['SectionTitle']))
        
        pages = data.get('pages', [])
        domain = data.get('metadata', {}).get('domain', '')
        
        if not pages:
            story.append(Paragraph("Aucune page analysée.", self.styles['Content']))
            return
        
        for i, page in enumerate(pages, 1):
            # Éviter les pages break excessives
            if i > 1:
                story.append(Spacer(1, 1*cm))
            
            # En-tête de page
            relative_url = self._get_relative_url(page.get('url', ''), domain)
            page_title = f"Page {i}: {relative_url}"
            
            story.append(Paragraph(page_title, self.styles['SubTitle']))
            story.append(Paragraph(page.get('url', ''), self.styles['URL']))
            
            # Informations techniques dans un tableau
            tech_data = [
                ['Statut HTTP', str(page.get('status', 'N/A'))],
                ['Temps de réponse', f"{page.get('responseTime', 0)} ms"],
                ['Taille HTML', self._format_size(page.get('htmlSize', 0))],
                ['Compression', 'Oui' if page.get('isCompressed', False) else 'Non']
            ]
            
            tech_table = Table(tech_data, colWidths=[4*cm, 4*cm])
            tech_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            
            story.append(tech_table)
            story.append(Spacer(1, 0.3*cm))
            
            # SEO On-Page
            self._add_page_seo_details(story, page)
            
            # Structure des titres
            self._add_page_headings_structure(story, page)
            
            # Problèmes de la page
            issues = page.get('issues', [])
            if issues:
                story.append(Paragraph("⚠️ Problèmes détectés", self.styles['SubTitle']))
                for issue in issues:
                    story.append(Paragraph(f"• {issue}", self.styles['Important']))
            else:
                story.append(Paragraph("✅ Aucun problème détecté", self.styles['Content']))
            
            # Séparateur entre pages
            if i < len(pages):
                story.append(Spacer(1, 0.5*cm))
                story.append(Paragraph("_" * 80, self.styles['Content']))
    
    def _add_page_seo_details(self, story: List, page: Dict[str, Any]):
        """Ajouter les détails SEO d'une page"""
        seo_data = []
        
        # Titre
        title = page.get('title', 'Manquant')
        title_len = page.get('titleLen', 0)
        title_status = self._get_title_status(title_len)
        seo_data.append(['Titre', f"{title} ({title_len} car.)", title_status])
        
        # Meta description
        meta_desc = page.get('metaDesc', 'Manquant')
        meta_len = page.get('metaDescLen', 0)
        meta_status = self._get_meta_status(meta_len)
        seo_data.append(['Meta description', f"{meta_desc[:50]}... ({meta_len} car.)" if len(meta_desc) > 50 else f"{meta_desc} ({meta_len} car.)", meta_status])
        
        # H1
        h1_count = page.get('h1Count', 0)
        h1_status = "✅" if h1_count == 1 else "⚠️" if h1_count == 0 else "❌"
        seo_data.append(['Balises H1', str(h1_count), h1_status])
        
        # Mots
        word_count = page.get('wordCount', 0)
        word_status = "✅" if word_count >= 300 else "⚠️"
        seo_data.append(['Nombre de mots', str(word_count), word_status])
        
        # Images sans alt
        img_no_alt = page.get('imgNoAlt', 0)
        img_status = "✅" if img_no_alt == 0 else "❌"
        seo_data.append(['Images sans alt', str(img_no_alt), img_status])
        
        if seo_data:
            seo_table = Table([['Élément SEO', 'Valeur', 'Statut']] + seo_data, 
                             colWidths=[4*cm, 6*cm, 2*cm])
            seo_table.setStyle(self._get_table_style())
            story.append(seo_table)
            story.append(Spacer(1, 0.3*cm))
    
    def _add_page_headings_structure(self, story: List, page: Dict[str, Any]):
        """Ajouter la structure des titres d'une page"""
        headings = page.get('headingsStructure', [])
        if not headings:
            return
        
        story.append(Paragraph("Structure des titres", self.styles['SubTitle']))
        
        for heading in headings[:10]:  # Limiter à 10 titres
            level = heading.get('level', 1)
            text = heading.get('text', '')
            indent = "  " * (level - 1)
            story.append(Paragraph(f"{indent}H{level}: {text}", self.styles['Content']))
        
        # Problèmes de hiérarchie
        hierarchy_issues = page.get('headingsHierarchyIssues', [])
        if hierarchy_issues:
            story.append(Paragraph("Problèmes de hiérarchie:", self.styles['Content']))
            for issue in hierarchy_issues:
                story.append(Paragraph(f"• {issue}", self.styles['Important']))
        
        story.append(Spacer(1, 0.3*cm))
    
    def _add_recommendations(self, story: List, data: Dict[str, Any]):
        """Ajouter les recommandations générales"""
        story.append(Paragraph("RECOMMANDATIONS", self.styles['SectionTitle']))
        
        summary = data.get('summary', {})
        pages = data.get('pages', [])
        top_issues = summary.get('top_issues', [])
        
        if not top_issues:
            story.append(Paragraph("Félicitations ! Votre site présente une excellente optimisation SEO.", self.styles['Content']))
            return
        
        story.append(Paragraph("Actions prioritaires", self.styles['SubTitle']))
        
        recommendations = [
            "Analysez et corrigez les problèmes les plus fréquents en premier lieu.",
            "Concentrez-vous sur les pages avec le plus de trafic pour un impact maximal.",
            "Testez les modifications sur un échantillon avant de les déployer massivement.",
            "Surveillez les performances après chaque modification.",
            "Programmez des audits SEO réguliers pour maintenir la qualité."
        ]
        
        for rec in recommendations:
            story.append(Paragraph(f"• {rec}", self.styles['Content']))
        
        story.append(Spacer(1, 0.5*cm))
        
        # Recommandations spécifiques
        story.append(Paragraph("Recommandations spécifiques", self.styles['SubTitle']))
        
        specific_recs = self._generate_specific_recommendations(summary, pages)
        for rec in specific_recs:
            story.append(Paragraph(f"• {rec}", self.styles['Content']))
    
    def _get_relative_url(self, full_url: str, domain: str) -> str:
        """Obtenir l'URL relative"""
        try:
            parsed_domain = urlparse(domain)
            parsed_url = urlparse(full_url)
            
            if parsed_url.netloc == parsed_domain.netloc:
                path = parsed_url.path or '/'
                if parsed_url.query:
                    path += '?' + parsed_url.query
                return path if path != '/' else '/ (Accueil)'
            return full_url
        except:
            return full_url
    
    def _get_global_status(self, issues: int, total: int) -> str:
        """Obtenir le statut global"""
        if total == 0:
            return "Aucune donnée"
        percentage = (issues / total) * 100
        if percentage < 10:
            return "Excellent"
        elif percentage < 30:
            return "Bon"
        elif percentage < 50:
            return "Moyen"
        else:
            return "Nécessite attention"
    
    def _get_status_name(self, code: int) -> str:
        """Obtenir le nom du code de statut"""
        status_names = {
            200: "OK",
            301: "Redirection permanente",
            302: "Redirection temporaire", 
            404: "Non trouvé",
            500: "Erreur serveur"
        }
        return status_names.get(code, "Autre")
    
    def _get_title_status(self, length: int) -> str:
        """Statut du titre"""
        if length == 0:
            return "❌"
        elif 30 <= length <= 60:
            return "✅"
        else:
            return "⚠️"
    
    def _get_meta_status(self, length: int) -> str:
        """Statut de la meta description"""
        if length == 0:
            return "❌"
        elif 120 <= length <= 160:
            return "✅"
        else:
            return "⚠️"
    
    def _format_size(self, size: int) -> str:
        """Formater la taille en octets"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    
    def _get_table_style(self):
        """Style par défaut pour les tableaux"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
        ])
    
    def _add_title_analysis(self, story: List, pages: List):
        """Analyse des titres"""
        if not pages:
            return
            
        story.append(Paragraph("Analyse des titres", self.styles['SubTitle']))
        
        missing_titles = sum(1 for p in pages if p.get('titleLen', 0) == 0)
        short_titles = sum(1 for p in pages if 0 < p.get('titleLen', 0) < 30)
        long_titles = sum(1 for p in pages if p.get('titleLen', 0) > 65)
        good_titles = len(pages) - missing_titles - short_titles - long_titles
        
        title_stats = f"Sur {len(pages)} pages : {good_titles} titres optimaux, "
        title_stats += f"{short_titles} trop courts, {long_titles} trop longs, {missing_titles} manquants."
        
        story.append(Paragraph(title_stats, self.styles['Content']))
        story.append(Spacer(1, 0.3*cm))
    
    def _add_meta_analysis(self, story: List, pages: List):
        """Analyse des meta descriptions"""
        if not pages:
            return
            
        story.append(Paragraph("Analyse des meta descriptions", self.styles['SubTitle']))
        
        missing_meta = sum(1 for p in pages if p.get('metaDescLen', 0) == 0)
        short_meta = sum(1 for p in pages if 0 < p.get('metaDescLen', 0) < 120)
        long_meta = sum(1 for p in pages if p.get('metaDescLen', 0) > 160)
        good_meta = len(pages) - missing_meta - short_meta - long_meta
        
        meta_stats = f"Sur {len(pages)} pages : {good_meta} meta descriptions optimales, "
        meta_stats += f"{short_meta} trop courtes, {long_meta} trop longues, {missing_meta} manquantes."
        
        story.append(Paragraph(meta_stats, self.styles['Content']))
        story.append(Spacer(1, 0.3*cm))
    
    def _add_images_analysis(self, story: List, pages: List):
        """Analyse des images"""
        if not pages:
            return
            
        story.append(Paragraph("Analyse des images", self.styles['SubTitle']))
        
        total_images_no_alt = sum(p.get('imgNoAlt', 0) for p in pages)
        pages_with_img_issues = sum(1 for p in pages if p.get('imgNoAlt', 0) > 0)
        
        if total_images_no_alt > 0:
            img_stats = f"{total_images_no_alt} images sans attribut alt trouvées sur {pages_with_img_issues} pages. "
            img_stats += "Ceci impacte l'accessibilité et le référencement."
        else:
            img_stats = "Toutes les images ont un attribut alt. Excellent pour l'accessibilité !"
        
        story.append(Paragraph(img_stats, self.styles['Content']))
        story.append(Spacer(1, 0.3*cm))
    
    def _get_issue_impact(self, issue: str, count: int, total_pages: int) -> str:
        """Évaluer l'impact d'un problème"""
        percentage = (count / total_pages) * 100 if total_pages > 0 else 0
        
        if percentage > 50:
            return "Critique"
        elif percentage > 20:
            return "Élevé"
        elif percentage > 5:
            return "Moyen"
        else:
            return "Faible"
    
    def _get_issue_recommendation(self, issue: str) -> str:
        """Obtenir une recommandation pour un problème"""
        recommendations = {
            "Titre manquant": "Ajoutez un titre unique et descriptif à chaque page (30-60 caractères).",
            "Titre trop court": "Allongez vos titres pour qu'ils soient plus descriptifs (minimum 30 caractères).",
            "Titre trop long": "Raccourcissez vos titres pour qu'ils s'affichent correctement dans les SERP (maximum 65 caractères).",
            "Meta description manquante": "Rédigez une meta description attrayante pour chaque page (120-160 caractères).",
            "H1 manquant": "Ajoutez un titre H1 unique sur chaque page pour structurer le contenu.",
            "Balises H1 multiples": "N'utilisez qu'un seul H1 par page, utilisez H2-H6 pour la hiérarchie.",
            "images sans texte alt": "Ajoutez des attributs alt descriptifs à toutes les images pour l'accessibilité.",
            "Nombre de mots insuffisant": "Enrichissez le contenu de vos pages (minimum 300 mots)."
        }
        
        for key, rec in recommendations.items():
            if key.lower() in issue.lower():
                return rec
        
        return "Consultez les bonnes pratiques SEO pour corriger ce problème."
    
    def _generate_specific_recommendations(self, summary: Dict, pages: List) -> List[str]:
        """Générer des recommandations spécifiques"""
        recs = []
        
        # Performance
        avg_time = summary.get('avg_response_time', 0)
        if avg_time > 1000:
            recs.append(f"Optimisez les performances : temps de réponse moyen de {avg_time:.0f}ms est trop élevé.")
        
        # Structure
        pages_without_h1 = sum(1 for p in pages if p.get('h1Count', 0) == 0)
        if pages_without_h1 > 0:
            recs.append(f"Ajoutez des titres H1 sur {pages_without_h1} pages pour améliorer la structure.")
        
        # Contenu
        thin_content_pages = sum(1 for p in pages if p.get('wordCount', 0) < 300)
        if thin_content_pages > 0:
            recs.append(f"Enrichissez le contenu de {thin_content_pages} pages (moins de 300 mots).")
        
        # Images
        total_img_issues = sum(p.get('imgNoAlt', 0) for p in pages)
        if total_img_issues > 0:
            recs.append(f"Ajoutez des attributs alt à {total_img_issues} images pour l'accessibilité.")
        
        return recs[:5]  # Maximum 5 recommandations


def generate_pdf_report(analysis_data_path: str, output_path: str) -> bool:
    """Fonction utilitaire pour générer un rapport PDF"""
    try:
        # Charger les données d'analyse
        with open(analysis_data_path, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        # Créer le générateur et générer le rapport
        generator = SEOAuditPDFGenerator()
        return generator.generate_report(analysis_data, output_path)
        
    except Exception as e:
        print(f"Erreur lors de la génération du rapport PDF: {e}")
        return False


if __name__ == "__main__":
    # Test simple
    import sys
    if len(sys.argv) < 3:
        print("Usage: python pdf_generator.py <analysis_data.json> <output.pdf>")
        sys.exit(1)
    
    success = generate_pdf_report(sys.argv[1], sys.argv[2])
    print("✅ Rapport PDF généré avec succès !" if success else "❌ Erreur lors de la génération")