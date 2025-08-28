# 🚀 SEO Audit Tool - Proxy Local Simple

## Installation et utilisation ultra-rapide

### Prérequis
- **Node.js** (version 14 ou plus récente)
- Aucune dépendance externe !

### Démarrage rapide

```bash
# 1. Lancer le serveur proxy (dans le terminal)
node proxy-server.js

# 2. Ouvrir dans le navigateur
# http://localhost:3001/
```

**C'est tout !** 🎉

## Pourquoi cette solution ?

### ❌ **Problèmes des proxies publics :**
- Souvent en panne ou lents
- Limités en requêtes
- Bloqués par les sites
- Non fiables

### ✅ **Avantages du proxy local :**
- **Fiable à 100%** - Sous votre contrôle
- **Rapide** - Pas d'intermédiaire externe
- **Illimité** - Aucune restriction
- **Simple** - 1 seul fichier de 100 lignes
- **Sécurisé** - Aucune donnée externe

## Comment ça marche

```
Navigateur → Proxy local (Port 3001) → Site web cible
```

Le micro-serveur Node.js agit comme un simple relai qui :
1. Reçoit votre requête depuis le navigateur
2. Fait la vraie requête HTTP vers le site cible
3. Retourne le résultat avec les bons headers CORS

## Fonctionnalités

- ✅ **Serveur de fichiers** - Sert l'interface web
- ✅ **Proxy CORS** - Contourne les restrictions navigateur
- ✅ **Gestion d'erreurs** - Messages clairs
- ✅ **Logging** - Voir les requêtes en temps réel
- ✅ **Timeout** - Évite les blocages
- ✅ **Arrêt propre** - Ctrl+C pour arrêter

## Structure des fichiers

```
seo_audit/
├── proxy-server.js     # Serveur proxy (100 lignes)
├── package.json        # Configuration Node.js
├── index.html          # Interface SEO Tool
└── README_PROXY.md     # Cette documentation
```

## Utilisation avancée

### Variables d'environnement
```bash
PORT=3001 node proxy-server.js  # Changer le port
```

### Mode développement
```bash
npm start    # Alias pour node proxy-server.js
npm run dev  # Même chose
```

### Logs détaillés
Le serveur affiche en temps réel :
- 📡 Requêtes proxy vers les sites externes
- 📁 Fichiers statiques servis
- ❌ Erreurs de connexion
- ⏱️ Timeouts

## Dépannage

### Le serveur ne démarre pas
```bash
# Vérifier que le port 3001 est libre
netstat -an | grep 3001

# Ou changer de port
PORT=3002 node proxy-server.js
```

### Erreur "Proxy local indisponible"
1. Vérifiez que `node proxy-server.js` tourne
2. Vérifiez l'URL: `http://localhost:3001/`
3. Pas `file://` mais bien `http://`

### Site web ne se charge pas
- Certains sites bloquent les requêtes automatisées
- Essayez avec un autre site pour tester
- Vérifiez les logs du serveur

## Performance

- ⚡ **Démarrage** : < 1 seconde
- 🔥 **Mémoire** : < 20 MB
- 🚀 **Vitesse** : Pas de limitation artificielle
- 🎯 **Fiabilité** : Dépend uniquement de votre machine

---

**Cette solution simple remplace tous les proxies CORS publics peu fiables !** 🎯