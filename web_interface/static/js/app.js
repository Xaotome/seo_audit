// JavaScript principal pour l'interface web SEO Audit Tool

// Configuration globale
const CONFIG = {
    REFRESH_INTERVAL: 5000,
    WEBSOCKET_TIMEOUT: 30000,
    MAX_RETRIES: 3
};

// Variables globales
let socketConnection = null;
let retryCount = 0;
let refreshTimer = null;

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Initialiser l'application
function initializeApp() {
    // Initialiser les tooltips Bootstrap
    initializeTooltips();
    
    // Initialiser les animations
    initializeAnimations();
    
    // Gérer les formulaires
    initializeForms();
    
    // Initialiser les utilitaires
    initializeUtilities();
    
    console.log('SEO Audit Tool - Interface initialisée');
}

// Initialiser les tooltips Bootstrap
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialiser les animations
function initializeAnimations() {
    // Animation au scroll pour les cartes
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    });

    // Observer toutes les cartes
    document.querySelectorAll('.card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
}

// Initialiser la gestion des formulaires
function initializeForms() {
    // Validation en temps réel
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
        
        // Validation des champs URL
        const urlInputs = form.querySelectorAll('input[type="url"]');
        urlInputs.forEach(input => {
            input.addEventListener('input', validateUrlInput);
            input.addEventListener('blur', validateUrlInput);
        });
        
        // Validation des champs numériques
        const numberInputs = form.querySelectorAll('input[type="number"]');
        numberInputs.forEach(input => {
            input.addEventListener('input', validateNumberInput);
        });
    });
}

// Initialiser les utilitaires
function initializeUtilities() {
    // Gestion du mode sombre (optionnel)
    initializeDarkMode();
    
    // Gestion de la copie dans le presse-papiers
    initializeClipboard();
    
    // Gestion des notifications
    initializeNotifications();
}

// Gérer la soumission de formulaire
function handleFormSubmit(event) {
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    
    if (submitButton) {
        // Désactiver le bouton et afficher le spinner
        submitButton.disabled = true;
        const originalContent = submitButton.innerHTML;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>En cours...';
        
        // Restaurer le bouton en cas d'erreur
        setTimeout(() => {
            if (submitButton.disabled) {
                submitButton.disabled = false;
                submitButton.innerHTML = originalContent;
            }
        }, 60000); // 1 minute timeout
    }
}

// Valider les champs URL
function validateUrlInput(event) {
    const input = event.target;
    const url = input.value.trim();
    
    if (url && !isValidUrl(url)) {
        input.classList.add('is-invalid');
        showFieldError(input, 'URL invalide. Utilisez le format: https://example.com');
    } else {
        input.classList.remove('is-invalid');
        hideFieldError(input);
    }
}

// Valider les champs numériques
function validateNumberInput(event) {
    const input = event.target;
    const value = parseFloat(input.value);
    const min = parseFloat(input.min);
    const max = parseFloat(input.max);
    
    if (isNaN(value) || (min && value < min) || (max && value > max)) {
        input.classList.add('is-invalid');
    } else {
        input.classList.remove('is-invalid');
    }
}

// Vérifier si une URL est valide
function isValidUrl(string) {
    try {
        const url = new URL(string);
        return url.protocol === 'http:' || url.protocol === 'https:';
    } catch (_) {
        return false;
    }
}

// Afficher une erreur de champ
function showFieldError(input, message) {
    hideFieldError(input); // Supprimer l'erreur existante
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    errorDiv.setAttribute('data-field-error', 'true');
    
    input.parentNode.appendChild(errorDiv);
}

// Masquer une erreur de champ
function hideFieldError(input) {
    const existingError = input.parentNode.querySelector('[data-field-error="true"]');
    if (existingError) {
        existingError.remove();
    }
}

// Initialiser le mode sombre
function initializeDarkMode() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', toggleDarkMode);
        
        // Charger la préférence sauvegardée
        if (localStorage.getItem('darkMode') === 'enabled') {
            enableDarkMode();
        }
    }
}

// Activer le mode sombre
function enableDarkMode() {
    document.body.classList.add('dark-mode');
    localStorage.setItem('darkMode', 'enabled');
}

// Désactiver le mode sombre
function disableDarkMode() {
    document.body.classList.remove('dark-mode');
    localStorage.setItem('darkMode', 'disabled');
}

// Basculer le mode sombre
function toggleDarkMode() {
    if (document.body.classList.contains('dark-mode')) {
        disableDarkMode();
    } else {
        enableDarkMode();
    }
}

// Initialiser la gestion du presse-papiers
function initializeClipboard() {
    const copyButtons = document.querySelectorAll('[data-clipboard-target]');
    copyButtons.forEach(button => {
        button.addEventListener('click', handleClipboardCopy);
    });
}

// Gérer la copie dans le presse-papiers
function handleClipboardCopy(event) {
    const button = event.target;
    const targetSelector = button.getAttribute('data-clipboard-target');
    const target = document.querySelector(targetSelector);
    
    if (target) {
        const text = target.textContent || target.value;
        
        navigator.clipboard.writeText(text).then(() => {
            showToast('Copié dans le presse-papiers', 'success');
            
            // Feedback visuel temporaire
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-check"></i>';
            setTimeout(() => {
                button.innerHTML = originalText;
            }, 2000);
        }).catch(() => {
            showToast('Erreur lors de la copie', 'error');
        });
    }
}

// Initialiser le système de notifications
function initializeNotifications() {
    // Créer le conteneur de toasts s'il n'existe pas
    if (!document.querySelector('.toast-container')) {
        const container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
}

// Afficher un toast
function showToast(message, type = 'info', duration = 5000) {
    const container = document.querySelector('.toast-container');
    if (!container) return;
    
    const toastId = 'toast-' + Date.now();
    const bgClass = {
        success: 'bg-success',
        error: 'bg-danger',
        warning: 'bg-warning',
        info: 'bg-info'
    }[type] || 'bg-info';
    
    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white ${bgClass}" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${getIconForType(type)} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: duration });
    toast.show();
    
    // Nettoyer après fermeture
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

// Obtenir l'icône pour un type de notification
function getIconForType(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-triangle',
        warning: 'exclamation-circle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Formater une durée en secondes
function formatDuration(seconds) {
    if (!seconds || seconds < 0) return '0s';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    }
    return `${secs}s`;
}

// Formater une taille en bytes
function formatBytes(bytes) {
    if (!bytes || bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// Formater un nombre avec des séparateurs
function formatNumber(number) {
    return new Intl.NumberFormat('fr-FR').format(number);
}

// Debounce function pour optimiser les événements
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function pour limiter la fréquence d'exécution
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// Utilitaire pour faire des requêtes AJAX
async function makeRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
        ...options
    };
    
    try {
        const response = await fetch(url, defaultOptions);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        } else {
            return await response.text();
        }
    } catch (error) {
        console.error('Request failed:', error);
        throw error;
    }
}

// Afficher un indicateur de chargement
function showLoading(element, message = 'Chargement...') {
    const spinner = document.createElement('div');
    spinner.className = 'text-center py-4';
    spinner.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Chargement...</span>
        </div>
        <p class="mt-2 text-muted">${message}</p>
    `;
    spinner.setAttribute('data-loading', 'true');
    
    element.appendChild(spinner);
}

// Masquer l'indicateur de chargement
function hideLoading(element) {
    const loadingElement = element.querySelector('[data-loading="true"]');
    if (loadingElement) {
        loadingElement.remove();
    }
}

// Gestion globale des erreurs
window.addEventListener('error', function(event) {
    console.error('Erreur JavaScript:', event.error);
    
    // Ne pas afficher les erreurs en production
    if (window.location.hostname !== 'localhost') {
        return;
    }
    
    showToast('Une erreur inattendue s\'est produite', 'error');
});

// Gestion des promesses non gérées
window.addEventListener('unhandledrejection', function(event) {
    console.error('Promise rejetée:', event.reason);
    showToast('Erreur de connexion ou de traitement', 'error');
});

// Export des fonctions utilitaires globales
window.SEOAudit = {
    showToast,
    formatDuration,
    formatBytes,
    formatNumber,
    makeRequest,
    showLoading,
    hideLoading,
    debounce,
    throttle
};