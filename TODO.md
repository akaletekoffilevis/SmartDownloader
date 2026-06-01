# SmartDownloader — Todo List V1

## 🎯 Priorité : Rapidité même sous faible connexion

---

## Phase 1 — Fondations (Haute priorité)

- [x] Créer la structure du projet
- [ ] `requirements.txt` + config projet (yt-dlp, PySide6, requests)
- [ ] `core/manager.py` — Gestionnaire central (file d'attente, config JSON, historique)
- [ ] `core/downloader.py` — Téléchargement optimisé :
  - Concurrent fragments (--concurrent-fragments 3-5)
  - Sélection auto du meilleur format (av1 > vp9 > h264)
  - Mode "Best Speed" (priorité rapidité réseau)
  - Reprise auto sur échec
  - Limite bande passante réglable
  - Split auto fichiers > 2 Go
- [ ] `data/history.json` + `data/config.json` — Stockage léger

## Phase 2 — UI Principale (Haute priorité)

- [ ] `ui/home.py` — Dashboard avec gros boutons :
  - Coller un lien (auto-détection)
  - Rechercher une vidéo
  - Téléchargements en cours
  - Historique
  - Paramètres
- [ ] `ui/download.py` — Page téléchargement :
  - Champ lien + détection auto presse-papier
  - Choix vidéo/audio
  - Qualité (Best Speed / Meilleure qualité / Personnalisé)
  - Barre de progression + vitesse + temps restant
  - Pause / Resume / Annuler
  - File d'attente (1-2 DL simultanés max)
  - Bouton "Urgent" pour prioriser un DL
- [ ] `ui/settings.py` — Paramètres :
  - Dossier de téléchargement
  - Limite vitesse (KB/s)
  - Nombre max de DL simultanés (1-3)
  - Qualité par défaut
  - Thème (dark uniquement V1)
  - Langue (fr/en)
  - Mode "Best Speed" par défaut

## Phase 3 — Recherche & Playlist (Moyenne priorité)

- [ ] `ui/search.py` — Recherche vidéo intégrée (API YouTube / yt-dlp search) :
  - Champ mot-clé
  - Résultats : thumbnail, titre, durée, auteur
  - Clic = preview + téléchargement direct
- [ ] `ui/playlist.py` — Playlist Manager :
  - Détection auto d'une playlist
  - Liste des vidéos avec checkbox
  - Sélectionner tout
  - Ordre de téléchargement
  - Organisation auto des fichiers (dossier par playlist)

## Phase 4 — Historique (Moyenne priorité)

- [ ] `ui/history.py` — Historique :
  - Liste complète des DL
  - Filtres : vidéo / audio / date / statut
  - Actions : ouvrir fichier, supprimer, re-télécharger
  - Recherche dans l'historique

## Phase 5 — Intelligence & Finitions (Basse priorité)

- [ ] Auto-détection de lien (presse-papier monitor)
- [ ] Mode "Audio seulement" (extraction native, pas de FFmpeg)
- [ ] Planificateur de téléchargement (DL la nuit)
- [ ] Cache DNS intégré
- [ ] Notification fin de téléchargement
- [ ] Tests & débogage
- [ ] Packaging (PyInstaller)

## ❌ Exclu de la V1

| Fonctionnalité | Raison |
|---|---|
| Navigateur intégré (WebEngine) | Trop lourd, ~200 Mo de dépendances |
| Bouton flottant | Dépend du navigateur |
| Thème light | Pas prioritaire, dark suffit |
| Multi-langue avancée | Juste fr/en |
| Cloud sync / Login / Premium | Hors scope |
| Conversion FFmpeg pour audio | Extraction native suffit |

## ⚡ Stratégie vitesse (faible connexion)

1. `--concurrent-fragments 3-5` = fragments parallèles
2. Priorité av1 > vp9 > h264 (meilleure compression réseau)
3. Mode "Best Speed" = format le plus rapide à DL
4. Reprise auto = pas de perte si coupure
5. Limite bande passante = pas de saturation
6. Split 2 Go = pas de corruption HDD
7. File d'attente max 2 = CPU/HDD friendly
