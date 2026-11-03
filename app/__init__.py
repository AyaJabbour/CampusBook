import os
from flask import Flask, render_template
import click
from app.extensions import db, migrate, login_manager, csrf
from config import config_by_name
from app.models.user import User
from app.models.room import Room
from app.models.reservation import Reservation


def create_app(config_name: str = None) -> Flask:
    """Application Factory Flask."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Initialisation des extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Configuration du chargeur d'utilisateur Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Enregistrement des Blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.rooms import rooms_bp
    from app.routes.reservations import reservations_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(rooms_bp)
    app.register_blueprint(reservations_bp)
    app.register_blueprint(admin_bp)

    # Enregistrement des gestionnaires d'erreurs HTTP
    register_error_handlers(app)

    # Enregistrement des commandes CLI personnalisées
    register_cli_commands(app)

    # Variables globales pour les templates Jinja2
    @app.context_processor
    def inject_globals():
        return {
            'app_name': 'CampusBook',
            'opening_time_str': app.config.get('OPENING_TIME').strftime('%H:%M'),
            'closing_time_str': app.config.get('CLOSING_TIME').strftime('%H:%M')
        }

    return app


def register_error_handlers(app: Flask) -> None:
    """Enregistre les pages d'erreurs personnalisées."""
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        db.session.rollback()
        return render_template('errors/500.html'), 500


def register_cli_commands(app: Flask) -> None:
    """Enregistre les commandes CLI pour l'initialisation et la gestion."""

    @app.cli.command("init-db")
    def init_db():
        """Initialise la base de données (création des tables)."""
        db.create_all()
        click.echo("[OK] Base de donnees initialisee avec succes.")

    @app.cli.command("create-admin")
    @click.option("--name", prompt="Nom complet de l'administrateur", default="Administrateur Campus")
    @click.option("--email", prompt="Adresse e-mail universitaire", default="admin@campusbook.fr")
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    def create_admin(name, email, password):
        """Crée un compte administrateur en toute sécurité."""
        db.create_all()
        clean_email = email.strip().lower()
        existing = User.query.filter_by(email=clean_email).first()
        if existing:
            click.echo(f"[X] Erreur : un utilisateur avec l'adresse '{clean_email}' existe deja.")
            return

        admin = User(
            full_name=name.strip(),
            email=clean_email,
            role='admin'
        )
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        click.echo(f"[OK] Administrateur '{clean_email}' cree avec succes !")

    @app.cli.command("seed-db")
    def seed_db():
        """Insère les données de démonstration sans créer de doublons."""
        db.create_all()
        from datetime import date, time, timedelta

        # 1. Vérification / Création de l'administrateur par défaut
        admin_email = "admin@campusbook.fr"
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin = User(
                full_name="Admin Principal",
                email=admin_email,
                role="admin"
            )
            admin.set_password("AdminPass123!")
            db.session.add(admin)
            click.echo(f"  + Compte administrateur créé : {admin_email} / AdminPass123!")
        else:
            click.echo(f"  = Compte administrateur déjà existant ({admin_email}).")

        # 2. Vérification / Création des étudiants de démonstration
        students_data = [
            ("Alice Martin", "alice@campusbook.fr", "Etudiant123!"),
            ("Bob Dupont", "bob@campusbook.fr", "Etudiant123!"),
            ("Clara Leroy", "clara@campusbook.fr", "Etudiant123!")
        ]
        created_students = []
        for name, email, pwd in students_data:
            st = User.query.filter_by(email=email).first()
            if not st:
                st = User(full_name=name, email=email, role="student")
                st.set_password(pwd)
                db.session.add(st)
                created_students.append(st)
                click.echo(f"  + Compte étudiant créé : {email} / {pwd}")
            else:
                created_students.append(st)
        db.session.commit()

        # 3. Vérification / Création des salles de démonstration
        rooms_data = [
            {
                "name": "Salle Ada Lovelace",
                "building": "Bâtiment Turing",
                "room_number": "T-101",
                "capacity": 30,
                "equipment": "Vidéoprojecteur 4K, Wi-Fi Haut Débit, Tableau blanc, Prises individuelles",
                "description": "Salle informatique moderne équipée pour les travaux pratiques, TD interactifs et soutenances de groupe.",
                "image_filename": "room_lovelace.jpg",
                "is_active": True
            },
            {
                "name": "Amphithéâtre Marie Curie",
                "building": "Bâtiment Sciences",
                "room_number": "SC-001",
                "capacity": 150,
                "equipment": "Système audio professionnel, Micro sans fil, Double projecteur, Climatisation",
                "description": "Grand amphithéâtre universitaire adapté aux conférences, cours magistraux et présentations de projets majeurs.",
                "image_filename": "room_curie.jpg",
                "is_active": True
            },
            {
                "name": "Salle Alan Turing",
                "building": "Bâtiment Turing",
                "room_number": "T-204",
                "capacity": 16,
                "equipment": "Écran interactif tactile, Wi-Fi, Caméra visio 360°, Tableau blanc",
                "description": "Espace collaboratif conçu pour les réunions d'équipes projet, ateliers de réflexion et soutenances restreintes.",
                "image_filename": "room_turing.jpg",
                "is_active": True
            },
            {
                "name": "Lab Innovation Shannon",
                "building": "Bâtiment Numérique",
                "room_number": "NUM-310",
                "capacity": 20,
                "equipment": "Imprimante 3D, Postes de travail double écran, Wi-Fi, Vidéoprojecteur",
                "description": "Laboratoire dédié au prototypage, hackathons d'étudiants et projets de recherche appliquée.",
                "image_filename": "room_shannon.jpg",
                "is_active": True
            },
            {
                "name": "Box de Travail B-01",
                "building": "Bibliothèque Universitaire",
                "room_number": "BU-12",
                "capacity": 6,
                "equipment": "Tableau blanc magnétique, Prises USB/secteur, Insonorisation renforcée",
                "description": "Petit box calme pour travaux en petit groupe ou révisions d'examens.",
                "image_filename": "room_box.jpg",
                "is_active": True
            },
            {
                "name": "Salle de Réunion Euler (En maintenance)",
                "building": "Bâtiment Mathématiques",
                "room_number": "M-105",
                "capacity": 12,
                "equipment": "Tableau velleda, Vidéoprojecteur",
                "description": "Salle temporairement indisponible pour travaux d'aménagement électrique.",
                "image_filename": "room_euler.jpg",
                "is_active": False
            }
        ]

        seeded_rooms = []
        for r_data in rooms_data:
            existing_room = Room.query.filter_by(name=r_data["name"]).first()
            if not existing_room:
                room = Room(**r_data)
                db.session.add(room)
                seeded_rooms.append(room)
                click.echo(f"  + Salle créée : {room.name} ({room.building})")
            else:
                seeded_rooms.append(existing_room)
        db.session.commit()

        # 4. Vérification / Création de quelques réservations de démonstration cohérentes
        student_alice = User.query.filter_by(email="alice@campusbook.fr").first()
        room_lovelace = Room.query.filter_by(name="Salle Ada Lovelace").first()
        room_turing = Room.query.filter_by(name="Salle Alan Turing").first()

        tomorrow = date.today() + timedelta(days=1)
        day_after = date.today() + timedelta(days=2)

        if student_alice and room_lovelace:
            res1 = Reservation.query.filter_by(
                room_id=room_lovelace.id,
                reservation_date=tomorrow,
                start_time=time(10, 0)
            ).first()
            if not res1:
                res1 = Reservation(
                    user_id=student_alice.id,
                    room_id=room_lovelace.id,
                    reservation_date=tomorrow,
                    start_time=time(10, 0),
                    end_time=time(12, 0),
                    purpose="Préparation du projet web CampusBook avec Alice et son binôme",
                    participants_count=8,
                    status="confirmed"
                )
                db.session.add(res1)
                click.echo(f"  + Réservation démo ajoutée pour {tomorrow} de 10:00 à 12:00")

        if student_alice and room_turing:
            res2 = Reservation.query.filter_by(
                room_id=room_turing.id,
                reservation_date=day_after,
                start_time=time(14, 0)
            ).first()
            if not res2:
                res2 = Reservation(
                    user_id=student_alice.id,
                    room_id=room_turing.id,
                    reservation_date=day_after,
                    start_time=time(14, 0),
                    end_time=time(16, 0),
                    purpose="Revue de code et préparation des tests fonctionnels",
                    participants_count=6,
                    status="confirmed"
                )
                db.session.add(res2)
                click.echo(f"  + Réservation démo ajoutée pour {day_after} de 14:00 à 16:00")

        db.session.commit()
        click.echo("[OK] Donnees de demonstration chargees avec succes !")
