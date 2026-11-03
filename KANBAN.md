# Tableau Kanban & Gestion des Issues — Projet CampusBook

Ce document consigne l'organisation agile du projet **CampusBook**, modélisé selon la méthode Kanban pour une équipe de deux étudiantes (**Étudiante A** et **Étudiante B**).

---

## 1. Vue d'Ensemble du Tableau Kanban

| À faire (To do) | En cours (In progress) | En revue / PR (Review) | Terminé (Done) |
| :--- | :--- | :--- | :--- |
| — | — | — | **Issue #1** : Initialiser le projet Flask (App Factory & Config) |
| — | — | — | **Issue #2** : Configurer SQLAlchemy, Migrations & CLI |
| — | — | — | **Issue #3** : Créer les modèles User, Room et Reservation |
| — | — | — | **Issue #4** : Développer l'authentification & sessions (Flask-Login) |
| — | — | — | **Issue #5** : Afficher et rechercher les salles universitaires |
| — | — | — | **Issue #6** : Ajouter les filtres multicritères de salles |
| — | — | — | **Issue #7** : Développer le formulaire de réservation Flask-WTF |
| — | — | — | **Issue #8** : Implémenter le service de détection des conflits |
| — | — | — | **Issue #9** : Consultation, modification et annulation sécurisées |
| — | — | — | **Issue #10** : Développer l'espace personnel étudiant |
| — | — | — | **Issue #11** : Développer le tableau de bord administrateur |
| — | — | — | **Issue #12** : Écrire et exécuter la suite de tests Pytest (29 tests) |
| — | — | — | **Issue #13** : Peaufiner l'interface responsive Bootstrap 5 & CSS SaaS |
| — | — | — | **Issue #14** : Rédiger la documentation technique complète (README) |
| — | — | — | **Issue #15** : Valider la procédure d'installation propre sur Windows |

---

## 2. Détail Réaliste des 15 Issues

### Issue #1 : Initialiser le projet Flask avec Application Factory
- **Description** : Mettre en place l'architecture modulaire du projet avec une Application Factory (`create_app`), la séparation par environnements dans `config.py` (Dev, Test, Prod), les dépendances `requirements.txt` et le point d'entrée `run.py`.
- **Critères d'acceptation** :
  - `create_app()` instancie Flask et charge la configuration appropriée.
  - Les dépendances sont spécifiées dans `requirements.txt`.
  - `.env.example` et `.gitignore` sont correctement renseignés.
- **Priorité** : Critique (P0)
- **Responsable** : Étudiante A
- **Dépendances** : Aucune
- **Statut** : Done

---

### Issue #2 : Configurer SQLAlchemy, les migrations Alembic et les commandes CLI
- **Description** : Configurer Flask-SQLAlchemy et Flask-Migrate. Créer des commandes CLI réutilisables et idempotentes (`init-db`, `seed-db`, `create-admin`).
- **Critères d'acceptation** :
  - `flask db init`, `flask db migrate`, `flask db upgrade` s'exécutent sans erreur.
  - La commande `flask seed-db` insère les données de démo sans doublons.
  - La commande `flask create-admin` permet de créer un compte administrateur en CLI.
- **Priorité** : Haute (P1)
- **Responsable** : Étudiante A
- **Dépendances** : Issue #1
- **Statut** : Done

---

### Issue #3 : Créer les modèles relationnels User, Room et Reservation
- **Description** : Définir les modèles de base de données avec types stricts, relations bidirectionnelles, clés étrangères avec cascade, et index composites de performance.
- **Critères d'acceptation** :
  - Modèle `User` avec `role` ('student', 'admin'), hash de mot de passe et méthode `is_admin`.
  - Modèle `Room` avec capacité, bâtiment, numéro, équipements et `is_active`.
  - Modèle `Reservation` avec index `(room_id, reservation_date, status)`.
- **Priorité** : Haute (P1)
- **Responsable** : Travail binôme (Étudiante A pour Room, Étudiante B pour Reservation & User)
- **Dépendances** : Issue #2
- **Statut** : Done

---

### Issue #4 : Développer le système d'authentification et de gestion des sessions
- **Description** : Implémenter l'inscription étudiant, la connexion/déconnexion, la protection CSRF et le contrôle des sessions avec Flask-Login.
- **Critères d'acceptation** :
  - Inscription publique limitée strictement au rôle `student`.
  - Mots de passe sécurisés avec PBKDF2/SHA-256 via Werkzeug.
  - Redirections intelligentes et sécurisées (prévention des open redirects).
  - Messages flash clairs de succès ou d'erreur.
- **Priorité** : Haute (P1)
- **Responsable** : Étudiante B
- **Dépendances** : Issue #3
- **Statut** : Done

---

### Issue #5 : Développer l'affichage et la recherche des salles
- **Description** : Créer le catalogue des salles sous forme de cartes responsives, afficher la fiche détaillée d'une salle avec son planning de réservations à venir.
- **Critères d'acceptation** :
  - Les utilisateurs non connectés ou étudiants voient uniquement les salles actives.
  - La fiche de salle affiche les équipements sous forme de badges.
  - Affichage des 10 prochaines réservations pour informer sur l'occupation.
- **Priorité** : Haute (P1)
- **Responsable** : Étudiante A
- **Dépendances** : Issue #3
- **Statut** : Done

---

### Issue #6 : Implémenter les filtres multicritères sur les salles
- **Description** : Permettre le filtrage instantané par mot-clé (nom, numéro), par bâtiment (liste déroulante dynamique), par capacité minimale et par équipement.
- **Critères d'acceptation** :
  - Les filtres peuvent être combinés librement dans l'URL.
  - Un bouton de réinitialisation permet de retrouver l'intégralité du catalogue.
  - Un état vide élégant s'affiche si aucun résultat n'est trouvé.
- **Priorité** : Moyenne (P2)
- **Responsable** : Étudiante A
- **Dépendances** : Issue #5
- **Statut** : Done

---

### Issue #7 : Développer le formulaire de réservation Flask-WTF
- **Description** : Créer le formulaire de réservation avec sélection de la salle, date, heure de début, heure de fin, nombre de participants et motif.
- **Critères d'acceptation** :
  - Le formulaire pré-sélectionne la salle si le paramètre `room_id` est présent.
  - Validation des types et contraintes côté client et serveur.
  - Prévisualisation JavaScript en temps réel de la durée sélectionnée.
- **Priorité** : Haute (P1)
- **Responsable** : Étudiante B
- **Dépendances** : Issue #4, Issue #5
- **Statut** : Done

---

### Issue #8 : Implémenter le service métier de détection des conflits horaires
- **Description** : Développer `ReservationService` avec validation mathématique stricte des chevauchements (`début1 < fin2 ET fin1 > début2`).
- **Critères d'acceptation** :
  - Refus des dates passées.
  - Refus si heure de fin <= heure de début.
  - Refus hors horaires d'ouverture (08:00 - 20:00).
  - Refus si nombre de participants > capacité.
  - Autorisation des créneaux contigus (ex: 10h-11h et 11h-12h).
  - Autorisation de créneaux identiques sur deux salles différentes.
  - Ignorance des réservations annulées.
- **Priorité** : Critique (P0)
- **Responsable** : Étudiante B
- **Dépendances** : Issue #7
- **Statut** : Done

---

### Issue #9 : Gestion des réservations (Consultation, Modification, Annulation)
- **Description** : Permettre à un étudiant de consulter le détail de sa réservation, de la modifier ou de l'annuler, avec contrôle d'intégrité et sécurité 403.
- **Critères d'acceptation** :
  - Un étudiant ne peut pas accéder à l'URL d'une réservation qui ne lui appartient pas (renvoie HTTP 403).
  - La modification ré-exécute le contrôle de conflit en excluant la réservation elle-même.
  - L'annulation libère immédiatement le créneau pour d'autres étudiants.
- **Priorité** : Haute (P1)
- **Responsable** : Étudiante B
- **Dépendances** : Issue #8
- **Statut** : Done

---

### Issue #10 : Développer l'espace personnel étudiant
- **Description** : Construire le tableau de bord étudiant affichant les réservations à venir, l'historique passé et les réservations annulées.
- **Critères d'acceptation** :
  - Compteurs KPI pour chaque statut.
  - Navigation par onglets clairs.
  - Boutons d'action contextuels (Détails, Modifier, Annuler).
- **Priorité** : Moyenne (P2)
- **Responsable** : Étudiante B
- **Dépendances** : Issue #9
- **Statut** : Done

---

### Issue #11 : Développer le tableau de bord administrateur
- **Description** : Créer l'espace d'administration protégé par le décorateur `@admin_required`, avec supervision des KPI, gestion des salles et régulation des réservations.
- **Critères d'acceptation** :
  - Accès formellement interdit aux étudiants (erreur 403 côté serveur).
  - Ajout et modification des salles.
  - Bouton d'activation/désactivation rapide d'une salle en un clic.
  - Consultation globale de toutes les réservations avec option d'annulation administrative.
- **Priorité** : Haute (P1)
- **Responsable** : Étudiante A & Étudiante B
- **Dépendances** : Issue #4, Issue #5, Issue #9
- **Statut** : Done

---

### Issue #12 : Écrire et exécuter la suite de tests automatisés Pytest
- **Description** : Mettre en place `tests/conftest.py` et les suites `test_auth.py`, `test_rooms.py`, `test_reservations.py`, `test_admin.py`.
- **Critères d'acceptation** :
  - 100% des tests réussis sur une base SQLite isolée en mémoire.
  - Couverture des cas nominaux et cas limites (conflits, sécurité 403, validation).
- **Priorité** : Haute (P1)
- **Responsable** : Travail binôme
- **Dépendances** : Issues #1 à #11
- **Statut** : Done

---

### Issue #13 : Harmoniser le design responsive Bootstrap 5 et CSS SaaS
- **Description** : Développer un design moderne, aéré, aux couleurs universitaires bleu nuit (`#0f172a`, `#1e3a8a`, `#2563eb`), cartes arrondies et responsive mobile/tablette.
- **Critères d'acceptation** :
  - Navbar collapsable sur mobile avec indicateur de rôle.
  - Alertes flash auto-fermantes.
  - Pages d'erreur personnalisées 403, 404, 500.
- **Priorité** : Moyenne (P2)
- **Responsable** : Travail binôme
- **Dépendances** : Issue #10, Issue #11
- **Statut** : Done

---

### Issue #14 : Rédiger la documentation technique complète (README.md)
- **Description** : Fournir un guide d'installation Windows pas à pas, l'architecture détaillée, les choix techniques, les limites de SQLite et le workflow Git.
- **Critères d'acceptation** :
  - Toutes les commandes PowerShell prêtes à copier-coller.
  - Comptes de test documentés.
  - Guide complet de contribution à deux.
- **Priorité** : Haute (P1)
- **Responsable** : Travail binôme
- **Dépendances** : Toutes les issues
- **Statut** : Done

---

### Issue #15 : Valider l'installation propre sur un environnement vierge
- **Description** : Vérifier que le dépôt peut être cloné, installé via `requirements.txt`, initialisé et testé sans aucune erreur.
- **Critères d'acceptation** :
  - Démarrage vérifié sur Windows avec Python 3.
  - Exécution complète de `pytest` sans échec.
- **Priorité** : Haute (P1)
- **Responsable** : Travail binôme
- **Dépendances** : Issue #14
- **Statut** : Done

---

## 3. Guide de Configuration dans GitHub Projects

Pour importer ce tableau dans **GitHub Projects** :
1. Sur GitHub, rendez-vous dans l'onglet **Projects** du dépôt, puis cliquez sur **New Project** -> Modèle **Board**.
2. Créez 4 colonnes : `To do`, `In progress`, `Review`, `Done`.
3. Cliquez sur **+ Add item** et convertissez les cartes en **Issues** en copiant-collant les titres, descriptions et critères d'acceptation détaillés ci-dessus.
4. Attribuez les labels (`feature`, `bug`, `documentation`, `test`), la priorité (`P0`, `P1`, `P2`) et les assignees (**Étudiante A** / **Étudiante B**).
