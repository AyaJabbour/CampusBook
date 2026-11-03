import pytest
from app import create_app, db
from app.models.user import User
from app.models.room import Room


@pytest.fixture
def app():
    """Crée une instance de l'application configurée pour les tests avec base SQLite en mémoire."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Client de test Flask."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner Flask."""
    return app.test_cli_runner()


@pytest.fixture
def student_user(app):
    """Crée un étudiant de test standard."""
    user = User(
        full_name="Étudiante Alice",
        email="alice.test@campusbook.fr",
        role="student"
    )
    user.set_password("MotDePasse123!")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def other_student_user(app):
    """Crée un second étudiant de test pour vérifier le cloisonnement des données."""
    user = User(
        full_name="Étudiant Bob",
        email="bob.test@campusbook.fr",
        role="student"
    )
    user.set_password("MotDePasse123!")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def admin_user(app):
    """Crée un administrateur de test."""
    admin = User(
        full_name="Administrateur Campus",
        email="admin.test@campusbook.fr",
        role="admin"
    )
    admin.set_password("AdminSecret123!")
    db.session.add(admin)
    db.session.commit()
    return admin


@pytest.fixture
def sample_room(app):
    """Crée une salle de test active."""
    room = Room(
        name="Salle Test Turing",
        building="Bâtiment Info",
        room_number="INFO-101",
        capacity=20,
        equipment="Vidéoprojecteur, Wi-Fi, Tableau blanc",
        description="Salle de test pour les réservations informatiques",
        is_active=True
    )
    db.session.add(room)
    db.session.commit()
    return room


@pytest.fixture
def sample_room_2(app):
    """Crée une deuxième salle de test active."""
    room = Room(
        name="Salle Test Lovelace",
        building="Bâtiment Info",
        room_number="INFO-102",
        capacity=30,
        equipment="Double écran, Wi-Fi",
        description="Deuxième salle de test pour vérifier la simultanéité",
        is_active=True
    )
    db.session.add(room)
    db.session.commit()
    return room


@pytest.fixture
def inactive_room(app):
    """Crée une salle inactive."""
    room = Room(
        name="Salle Maintenance",
        building="Bâtiment B",
        room_number="B-000",
        capacity=10,
        equipment="Aucun",
        is_active=False
    )
    db.session.add(room)
    db.session.commit()
    return room
