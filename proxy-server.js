#!/usr/bin/env node

/**
 * Micro-serveur proxy CORS ultra-simple pour SEO Audit Tool
 * Usage: node proxy-server.js
 * Puis ouvrir: http://localhost:3001/index.html
 */

const http = require('http');
const https = require('https');
const url = require('url');
const fs = require('fs');
const path = require('path');

const PORT = 3001;

// MIME types pour servir les fichiers statiques
const mimeTypes = {
    '.html': 'text/html',
    '.js': 'text/javascript',
    '.css': 'text/css',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon'
};

const server = http.createServer((req, res) => {
    // Headers CORS pour tous les endpoints
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, User-Agent');
    
    // Répondre aux requêtes OPTIONS (preflight)
    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    const parsedUrl = url.parse(req.url, true);
    const pathname = parsedUrl.pathname;

    console.log(`${req.method} ${pathname}`);

    // Route proxy pour contourner CORS
    if (pathname.startsWith('/proxy/')) {
        const targetUrl = decodeURIComponent(pathname.substring(7)); // Enlever '/proxy/'
        
        if (!targetUrl || !targetUrl.startsWith('http')) {
            res.writeHead(400, {'Content-Type': 'application/json'});
            res.end(JSON.stringify({error: 'URL invalide'}));
            return;
        }

        console.log(`📡 Proxy vers: ${targetUrl}`);

        // Variable pour éviter les réponses multiples
        let responseFinished = false;
        
        // Fonction pour envoyer une réponse d'erreur (une seule fois)
        const sendErrorResponse = (statusCode, errorMessage) => {
            if (responseFinished) return;
            responseFinished = true;
            
            console.error(`❌ ${errorMessage}: ${targetUrl}`);
            res.writeHead(statusCode, {'Content-Type': 'application/json'});
            res.end(JSON.stringify({
                error: errorMessage,
                url: targetUrl
            }));
        };

        // Choisir le bon module selon le protocole
        const requester = targetUrl.startsWith('https://') ? https : http;
        
        const proxyReq = requester.request(targetUrl, {
            method: req.method,
            headers: {
                'User-Agent': 'SEO-Audit-Tool/1.0 (Local Proxy)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
                'Accept-Encoding': 'identity', // Pas de compression pour simplifier
                'Cache-Control': 'no-cache'
            },
            timeout: 15000
        }, (proxyRes) => {
            if (responseFinished) return;
            
            try {
                // Copier les headers de réponse (sauf ceux qui posent problème)
                const allowedHeaders = ['content-type', 'content-length', 'last-modified', 'etag'];
                allowedHeaders.forEach(header => {
                    if (proxyRes.headers[header]) {
                        res.setHeader(header, proxyRes.headers[header]);
                    }
                });

                res.writeHead(proxyRes.statusCode || 200);
                responseFinished = true;
                
                proxyRes.pipe(res);
                
                proxyRes.on('end', () => {
                    // Pas de log pour chaque succès pour éviter le spam
                });
                
            } catch (error) {
                sendErrorResponse(500, 'Erreur lors du traitement de la réponse');
            }
        });

        proxyReq.on('error', (err) => {
            sendErrorResponse(500, `Erreur de connexion: ${err.message}`);
        });

        proxyReq.on('timeout', () => {
            proxyReq.destroy();
            sendErrorResponse(408, 'Timeout de connexion (15s)');
        });

        // Gestion de la fermeture de connexion côté client
        req.on('close', () => {
            if (!responseFinished) {
                console.log(`🔌 Client déconnecté: ${targetUrl}`);
                proxyReq.destroy();
                responseFinished = true;
            }
        });
        
        // Si c'est une requête POST/PUT, transférer le body
        if (req.method === 'POST' || req.method === 'PUT') {
            req.pipe(proxyReq);
        } else {
            proxyReq.end();
        }
        return;
    }

    // Servir les fichiers statiques
    let filePath = path.join(__dirname, pathname === '/' ? 'index.html' : pathname.substring(1));
    
    // Vérifier que le fichier existe
    fs.stat(filePath, (err, stats) => {
        if (err || !stats.isFile()) {
            res.writeHead(404, {'Content-Type': 'text/html'});
            res.end(`
                <h1>404 - Fichier non trouvé</h1>
                <p>Fichier demandé: ${pathname}</p>
                <p><a href="/">Retour à l'accueil</a></p>
            `);
            return;
        }

        // Déterminer le type MIME
        const ext = path.extname(filePath);
        const contentType = mimeTypes[ext] || 'text/plain';

        // Lire et servir le fichier
        fs.readFile(filePath, (err, content) => {
            if (err) {
                res.writeHead(500, {'Content-Type': 'text/html'});
                res.end('Erreur serveur');
                return;
            }

            res.writeHead(200, {'Content-Type': contentType});
            res.end(content);
        });
    });
});

server.listen(PORT, 'localhost', () => {
    console.log(`
🚀 Serveur proxy SEO Audit démarré !

📍 Interface web: http://localhost:${PORT}/
🔗 Proxy CORS:   http://localhost:${PORT}/proxy/[URL]

Exemple d'utilisation du proxy:
  http://localhost:${PORT}/proxy/https://example.com

Pour arrêter le serveur: Ctrl+C
    `);
});

// Gestion des erreurs du serveur
server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
        console.error(`❌ Erreur: Le port ${PORT} est déjà utilisé.`);
        console.error(`Essayez: PORT=${PORT + 1} node proxy-server.js`);
    } else {
        console.error(`❌ Erreur serveur: ${err.message}`);
    }
    process.exit(1);
});

// Gestion des erreurs non capturées
process.on('uncaughtException', (err) => {
    console.error(`❌ Erreur non capturée: ${err.message}`);
    console.error(err.stack);
    server.close(() => {
        process.exit(1);
    });
});

process.on('unhandledRejection', (reason, promise) => {
    console.error(`❌ Promesse rejetée: ${reason}`);
    console.error(promise);
});

// Gestion propre de l'arrêt
process.on('SIGINT', () => {
    console.log('\n👋 Arrêt du serveur proxy...');
    server.close(() => {
        console.log('✅ Serveur fermé proprement');
        process.exit(0);
    });
});

process.on('SIGTERM', () => {
    server.close(() => {
        process.exit(0);
    });
});