# CampusBook — Système de Réservation de Salles Universitaires

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.14-blue.svg)
![Flask](https://img.shields.io/badge/framework-Flask%203.1-black.svg)
![Tests](https://img.shields.io/badge/tests-29%2F29%20passed-brightgreen.svg)
![Licence](https://img.shields.io/badge/licence-Académique-green.svg)

---

## 1. Présentation du Projet

**CampusBook** est une application web professionnelle conçue pour moderniser et fluidifier la réservation d'espaces de travail au sein d'une université (salles de cours, laboratoires d'innovation, amphithéâtres et box de travail). 

Elle offre aux étudiants une autonomie complète pour réserver des créneaux en direct, tout en fournissant à l'équipe pédagogique et administrative un tableau de bord de supervision et de régulation.

Ce projet a été conçu et réalisé par deux étudiantes dans le cadre d'un projet universitaire d'ingénierie logicielle et de travail collaboratif.

---

## 2. les Objectifs du Projet

- **Fonctionnel** : Fournir une plateforme opérationnelle, fiable, avec détection mathématique stricte des chevauchements d'horaires et gestion des rôles.
- **Architectural** : Adopter une séparation stricte des responsabilités (Application Factory, Blueprints, Modèles SQLAlchemy, Formulaires Flask-WTF, Services métier transactionnels).
- **Collaboratif** : Démontrer un cycle de développement Git/GitHub en binôme, avec branches de fonctionnalités, commits conventionnels, revues de Pull Requests et suivi Kanban.
- **Qualité & Sécurité** : Couvrir l'application par une suite complète de tests automatisés Pytest (29 tests unitaires et d'intégration), sécuriser les sessions et bloquer les accès non autorisés côté serveur (HTTP 403).

---

## 3. Fonctionnalités Principales

### A. Espace Public & Visiteurs
- **Page d'accueil dynamique** : Présentation des atouts, compteurs en direct issus de la base de données (salles actives, réservations confirmées, utilisateurs enregistrés) et aperçu des salles vedettes.
- **Catalogue des salles** : Consultation sous forme de cartes modernes avec filtres combinables (mots-clés, bâtiment, capacité minimale, équipements).
- **Fiche détaillée d'une salle** : Description, badges d'équipements, capacité et planning des prochaines réservations pour faciliter le choix.

### B. Authentification & Sécurité
- **Inscription étudiante** : Validation stricte des données et hachage sécurisé du mot de passe avec PBKDF2/SHA-256 (aucun mot de passe en clair).
- **Attribution sécurisée des rôles** : Le formulaire d'inscription n'autorise que le rôle `student`. Les comptes `admin` sont gérés via CLI.
- **Connexion & Déconnexion** : Gestion de session Flask-Login avec protection contre les redirections ouvertes et jetons CSRF sur tous les formulaires.

### C. Espace Étudiant
- **Réservation intelligente** : Formulaire interactif avec pré-remplissage de salle, calcul visuel de la durée et contrôle en temps réel.
- **Tableau de bord personnel** : Suivi séparé des réservations à venir, de l'historique passé et des réservations annulées.
- **Gestion des réservations** : Consultation du voucher de réservation, modification autorisée et annulation immédiate qui libère le créneau pour d'autres étudiants.
- **Cloisonnement strict** : Un étudiant ne peut en aucun cas consulter ou modifier la réservation d'un autre étudiant (renvoi d'une erreur HTTP 403).

### D. Espace Administrateur
- **Tableau de bord d'administration** : Indicateurs clés (KPI) sur les salles, les utilisateurs et les réservations du campus.
- **Gestion du parc de salles** : Ajout d'une nouvelle salle, modification des caractéristiques et bascule active/inactive en un clic.
- **Supervision & Régulation** : Consultation de toutes les réservations du campus avec possibilité d'annulation administrative en cas de force majeure.
- **Protection serveur** : Accès réservé exclusivement aux utilisateurs possédant le rôle `admin` (décorateur `@admin_required`).

---

## 4. Technologies Utilisées

| Composant | Technologie | Description |
| :--- | :--- | :--- |
| **Backend** | Python 3 (3.11 à 3.14) | Langage principal robuste et typé |
| **Framework Web** | Flask 3.1 | Micro-framework modulaire avec Blueprints |
| **ORM** | Flask-SQLAlchemy & SQLAlchemy 2.1 | Mapping objet-relationnel et transactions |
| **Migrations** | Flask-Migrate & Alembic | Suivi versionné des schémas de base de données |
| **Authentification** | Flask-Login 0.6 & Werkzeug | Sessions utilisateur et hachage sécurisé |
| **Formulaires** | Flask-WTF 1.3 & WTForms 3.3 | Validation côté serveur et protection CSRF |
| **Base de Données** | SQLite | Base relationnelle légère pour le développement |
| **Interface** | HTML5, CSS3, Bootstrap 5.3, Bootstrap Icons | Interface responsive, accessible et moderne |
| **Typographie** | Plus Jakarta Sans | Police moderne style SaaS |
| **Tests Automatisés**| Pytest 9.2 | 29 tests unitaires et fonctionnels automatisés |
| **Versionnement** | Git & GitHub | Gestion de branches, PR et suivi Kanban |

---

## 5. Architecture Logicielle

Le projet est structuré selon le patron **Application Factory** :

```text
CampusBook/
├── app/
│   ├── __init__.py               # Application Factory create_app() & commandes CLI
│   ├── extensions.py             # Instanciation de db, migrate, login_manager, csrf
│   ├── models/                   # Modèles SQLAlchemy
│   │   ├── __init__.py           # Export des modèles
│   │   ├── user.py               # Modèle User (étudiant / administrateur)
│   │   ├── room.py               # Modèle Room (salle et équipements)
│   │   └── reservation.py        # Modèle Reservation (créneaux et statuts)
│   ├── routes/                   # Blueprints Flask
│   │   ├── __init__.py
│   │   ├── main.py               # Page d'accueil et page À propos
│   │   ├── auth.py               # Inscription, connexion, déconnexion
│   │   ├── rooms.py              # Catalogue, recherche, filtres et détails des salles
│   │   ├── reservations.py       # Réservations et tableau de bord étudiant
│   │   └── admin.py              # Espace d'administration et gestion des salles
│   ├── services/                 # Logique métier pure
│   │   ├── __init__.py
│   │   └── reservation_service.py # Algorithme de détection des conflits horaires
│   ├── forms/                    # Formulaires Flask-WTF
│   │   ├── __init__.py
│   │   ├── auth_forms.py         # Login & Register
│   │   ├── room_forms.py         # Formulaire d'administration de salle & filtres
│   │   └── reservation_forms.py  # Formulaire de réservation
│   ├── templates/                # Gabarits Jinja2
│   │   ├── base.html             # Structure commune, navbar et footer
│   │   ├── main/                 # index.html, about.html
│   │   ├── auth/                 # login.html, register.html
│   │   ├── rooms/                # index.html, detail.html
│   │   ├── reservations/         # create.html, edit.html, detail.html
│   │   ├── dashboard/            # student.html, admin.html, admin_rooms.html, etc.
│   │   └── errors/               # 403.html, 404.html, 500.html
│   └── static/                   # Fichiers statiques
│       ├── css/style.css         # Feuille de style personnalisée
│       └── js/main.js            # Validation client et interactions UI
├── migrations/                   # Fichiers de migration Alembic
├── tests/                        # Suite de tests automatisés
│   ├── conftest.py               # Fixtures Pytest & configuration mémoire
│   ├── test_auth.py              # Tests de sécurité et d'authentification
│   ├── test_rooms.py             # Tests du catalogue et des filtres
│   ├── test_reservations.py      # Tests des règles métier et conflits
│   └── test_admin.py             # Tests des permissions administrateur
├── .env.example                  # Modèle de variables d'environnement
├── .gitignore                    # Fichiers exclus du versionnement Git
├── config.py                     # Configurations (Dev, Testing, Prod)
├── KANBAN.md                     # Découpage agile des 15 issues Kanban
├── pytest.ini                    # Configuration Pytest
├── README.md                     # Documentation technique complète
├── requirements.txt              # Dépendances Python
└── run.py                        # Script d'exécution principal
```

---

## 6. Algorithme de Détection des Conflits Horaires

La vérification des disponibilités constitue le cœur de la fiabilité de l'application.

### Règle Mathématique de Chevauchement
Deux intervalles de temps `[début1, fin1]` et `[début2, fin2]` pour une même salle et une même date se chevauchent si et seulement si :

$$\text{début}_1 < \text{fin}_2 \quad \text{ET} \quad \text{fin}_1 > \text{début}_2$$

Cette condition garantit que :
- Une réservation de `10:00` à `11:00` n'empêche **pas** une réservation de `11:00` à `12:00` dans la même salle (créneaux contigus autorisés car $11:00 < 11:00$ est faux).
- Tout chevauchement même d'une minute (ex: `10:30` à `11:30`) est immédiatement refusé avec un message d'erreur explicite.

### Validations Métier Côté Serveur
1. **Date valide** : Refus systématique de toute date antérieure à aujourd'hui.
2. **Ordre chronologique** : L'heure de fin doit être strictement supérieure à l'heure de début.
3. **Horaires universitaires** : Le créneau doit être inclus entre `OPENING_TIME` (08h00) et `CLOSING_TIME` (20h00).
4. **Capacité maximale** : Le nombre de participants ne peut excéder la capacité autorisée de la salle.
5. **Salle active** : Impossible de réserver une salle passée en maintenance ou inactive.
6. **Statut des réservations** : Les réservations annulées sont automatiquement exclues du calcul de disponibilité.
7. **Modification sans auto-conflit** : Lors de la modification d'un créneau existant, la réservation courante est exclue de la recherche de conflits pour éviter les faux positifs.

---

## 7. Guide d'Installation et de Démarrage sous Windows

Suivez pas à pas ces instructions dans un terminal **PowerShell** ou **CMD**.

### Étape 1 : Cloner le dépôt et ouvrir le dossier
```powershell
cd C:\Users\Dell\.gemini\antigravity\scratch\CampusBook
```

### Étape 2 : Créer et activer l'environnement virtuel Python
```powershell
# Création de l'environnement virtuel
python -m venv .venv

# Activation sous PowerShell
.\.venv\Scripts\Activate.ps1
```

> **Note PowerShell** : Si l'exécution de scripts est restreinte sur votre machine, exécutez préalablement :
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Étape 3 : Installer les dépendances
```powershell
pip install -r requirements.txt
```

### Étape 4 : Configurer le fichier d'environnement
Copiez le modèle `.env.example` en `.env` :
```powershell
Copy-Item .env.example .env
```

### Étape 5 : Initialiser la base de données et les migrations
```powershell
$env:FLASK_APP = "run.py"
flask db upgrade
```

### Étape 6 : Charger les données de démonstration
La commande suivante crée les comptes de démonstration, les salles équipées et quelques réservations de test sans créer de doublons :
```powershell
flask seed-db
```

*(Optionnel)* Pour créer un compte administrateur supplémentaire personnalisé :
```powershell
flask create-admin
```

### Étape 7 : Démarrer l'application
```powershell
python run.py
```
Ouvrez ensuite votre navigateur sur **[http://127.0.0.1:5000](http://127.0.0.1:5000)**.

---

## 8. Comptes de Démonstration pour Évaluation Rapide

| Rôle | Adresse E-mail | Mot de Passe | Capacités |
| :--- | :--- | :--- | :--- |
| **Administrateur** | `admin@campusbook.fr` | `AdminPass123!` | Dashboard admin, gestion des salles, régulation |
| **Étudiant (Alice)** | `alice@campusbook.fr` | `Etudiant123!` | Consulter, réserver, modifier et annuler |
| **Étudiant (Bob)** | `bob@campusbook.fr` | `Etudiant123!` | Compte séparé pour tester le cloisonnement |

---

## 9. Exécution des Tests Automatisés

La suite de tests automatisés s'exécute avec **pytest** sur une base SQLite isolée en mémoire :

```powershell
.\.venv\Scripts\pytest -v
```

### Résultat de l'Exécution Réelle des Tests
```text
tests/test_admin.py::test_student_cannot_access_admin_dashboard PASSED   [  3%]
tests/test_admin.py::test_student_cannot_access_admin_rooms PASSED       [  6%]
tests/test_admin.py::test_admin_access_dashboard PASSED                  [ 10%]
tests/test_admin.py::test_admin_create_room PASSED                       [ 13%]
tests/test_admin.py::test_admin_toggle_room_status PASSED                [ 17%]
tests/test_admin.py::test_admin_can_cancel_any_reservation PASSED        [ 20%]
tests/test_auth.py::test_register_success PASSED                         [ 24%]
tests/test_auth.py::test_register_duplicate_email PASSED                 [ 27%]
tests/test_auth.py::test_login_success PASSED                            [ 31%]
tests/test_auth.py::test_login_wrong_password PASSED                     [ 34%]
tests/test_auth.py::test_logout PASSED                                   [ 37%]
tests/test_auth.py::test_protected_routes_require_login PASSED           [ 41%]
tests/test_reservations.py::test_create_valid_reservation PASSED         [ 44%]
tests/test_reservations.py::test_reject_past_date PASSED                 [ 48%]
tests/test_reservations.py::test_reject_end_time_before_start_time PASSED [ 51%]
tests/test_reservations.py::test_reject_exceeding_capacity PASSED        [ 55%]
tests/test_reservations.py::test_reject_overlapping_reservation PASSED   [ 58%]
tests/test_reservations.py::test_allow_contiguous_slots PASSED           [ 62%]
tests/test_reservations.py::test_allow_same_time_in_different_rooms PASSED [ 65%]
tests/test_reservations.py::test_cancel_releases_slot PASSED             [ 68%]
tests/test_reservations.py::test_cannot_access_or_edit_other_user_reservation PASSED [ 72%]
tests/test_reservations.py::test_reject_inactive_room_reservation PASSED [ 75%]
tests/test_rooms.py::test_rooms_list_active_only_for_guests PASSED       [ 79%]
tests/test_rooms.py::test_rooms_search_by_name PASSED                    [ 82%]
tests/test_rooms.py::test_rooms_filter_by_building PASSED                [ 86%]
tests/test_rooms.py::test_rooms_filter_by_min_capacity PASSED            [ 89%]
tests/test_rooms.py::test_rooms_filter_by_equipment PASSED               [ 93%]
tests/test_rooms.py::test_room_detail_view PASSED                        [ 96%]
tests/test_rooms.py::test_inactive_room_hidden_from_public PASSED        [100%]

============================== 29 passed in 10.46s ==============================
```

---

## 10. Organisation Collaborative & Workflow Git

### A. Répartition des Responsabilités
- **Étudiante A (Gestion des Salles & Socle)** :
  - Mise en place de l'Application Factory et de la structure du projet.
  - Modèle `Room` et intégration de la base de données.
  - Vues catalogue, moteur de recherche et filtrage multicritères.
  - Tests unitaires des salles (`test_rooms.py`).
- **Étudiante B (Gestion des Réservations & Sécurité)** :
  - Modèle `Reservation` et contraintes d'intégrité relationnelle.
  - Algorithme de détection des chevauchements (`ReservationService`).
  - Formulaires Flask-WTF et contrôles serveur.
  - Tableau de bord étudiant et gestion des réservations.
  - Tests unitaires des conflits et permissions (`test_reservations.py`, `test_admin.py`).
- **Travail Commun** :
  - Spécification commune des interfaces et formats de données.
  - Revues de code croisées via Pull Requests.
  - Tests d'intégration de l'application globale.
  - Rédaction de la documentation et préparation de la soutenance.

### B. Stratégie de Branches Git
- `main` : Branche de production protégée, code stable et testé.
- `feature/room-management` : Gestion des salles (Étudiante A).
- `feature/room-search` : Recherche et filtres (Étudiante A).
- `feature/authentication` : Authentification et sessions (Étudiante B).
- `feature/reservation-booking` : Formulaire et workflow de réservation (Étudiante B).
- `feature/reservation-conflicts` : Algorithme de détection des conflits (Étudiante B).
- `feature/admin-dashboard` : Tableau de bord administrateur (Binôme).
- `test/automated-tests` : Suite de tests Pytest (Binôme).
- `docs/project-documentation` : Documentation et guide Kanban (Binôme).

### C. Conventions de Commits (Conventional Commits)
- `feat:` Nouvelle fonctionnalité (ex: `feat: implement reservation conflict detection`)
- `fix:` Correction d'un bogue (ex: `fix: prevent overlapping slots on update`)
- `test:` Ajout ou mise à jour de tests (ex: `test: add contiguous slots verification`)
- `docs:` Documentation (ex: `docs: update installation and kanban guide`)
- `chore:` Configuration et maintenance (ex: `chore: configure alembic migrations`)

---

## 11. Limites Techniques Connues & Concurrence

### Limites de SQLite en Environnement Concurrent
SQLite est une base de données de développement idéale car intégrée et sans serveur requis. Cependant, elle présente des limites inhérentes pour la haute concurrence :
- **Verrouillage au niveau du fichier (File-level lock)** : SQLite place un verrou exclusif sur le fichier de base de données lors d'une écriture (`BEGIN IMMEDIATE`). Si deux requêtes de réservation arrivent à la même milliseconde, l'une attend que l'autre se termine.
- **Race conditions sous forte charge** : Si deux utilisateurs demandent exactement le même créneau au même instant, un léger risque de condition de course existe entre la phase de lecture des conflits (`check_availability`) et la phase d'insertion (`db.session.commit()`).

### Stratégie Recommandée pour la Production (Scalabilité)
Pour un déploiement universitaire à grande échelle :
1. **Migration vers PostgreSQL** : Remplacer SQLite par PostgreSQL via SQLAlchemy.
2. **Verrouillage pessimiste** : Utiliser `with_for_update()` dans la transaction pour verrouiller les créneaux de la salle ciblée :
   ```python
   # Exemple PostgreSQL
   conflicts = Reservation.query.filter(...).with_for_update().all()
   ```
3. **Contrainte d'exclusion native** : Configurer une contrainte d'exclusion PostgreSQL (`EXCLUDE USING gist`) au niveau du schéma SQL avec l'extension `btree_gist` pour interdire physiquement les chevauchements temporels au niveau du moteur SQL.
