# Bot pour Final Fantasy Brave Exvius

Bot pour automatiser et simuler des combat de Final Fantasy Brave Exvius (FFBE), aujourd'hui disparu.

## Avertissement légal et éthique

- Ce projet est fourni à titre éducatif et pour l'automatisation d'analyses légitimes.
- Je fournis les clés car le jeu (en tout cas sa version global) n'existe plus depuis le 31 octobre 2024.

## Structure du dépôt

- `classes/` : code principal du bot (modules Python tels que `FFBE.py`, `Login.py`, `Tools.py`, `Updater.py`, etc.).
- `data/` : fichiers JSON et YAML de configuration et données (unités, missions, requêtes, variables, etc.).
- `data_dump/` : dump de données issues d'autres ressources (extrait à partir du repos https://github.com/aEnigmatic/ffbe.git).
- `docker/` : `Dockerfile` et fichiers de configuration (ex : `torrc`) pour exécution dans un conteneur avec proxy Tor et renouvellement automatique de l'IP elle retourne une erreur 403.
- `Ressources/IDAScripts/` : scripts permettant d'extraire les clés de décryptage (nécessite AIDA64).

## Exécution (Docker recommandée)

1. Construire et lancer le service avec Docker Compose :

```bash
docker-compose build
docker-compose up -d
```

2. Voir les logs :

```bash
docker-compose logs -f
```

3. Arrêter et nettoyer :

```bash
docker-compose down
```