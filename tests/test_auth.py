from flask import url_for
from app.models.user import User


def test_register_success(client, app):
    """Vérifie qu'un étudiant peut s'inscrire avec succès."""
    response = client.post('/register', data={
        'full_name': 'Camille Martin',
        'email': 'camille@campusbook.fr',
        'password': 'MonMotDePasseFort123',
        'password_confirm': 'MonMotDePasseFort123'
    }, follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        user = User.query.filter_by(email='camille@campusbook.fr').first()
        assert user is not None
        assert user.full_name == 'Camille Martin'
        assert user.role == 'student'  # Ne peut pas être admin
        assert user.check_password('MonMotDePasseFort123')


def test_register_duplicate_email(client, student_user):
    """Vérifie que l'inscription avec un email déjà existant est refusée."""
    response = client.post('/register', data={
        'full_name': 'Autre Nom',
        'email': student_user.email,
        'password': 'MonMotDePasseFort123',
        'password_confirm': 'MonMotDePasseFort123'
    })
    assert response.status_code == 200
    assert b"Cette adresse e-mail est d" in response.data


def test_login_success(client, student_user):
    """Vérifie la connexion avec les bons identifiants."""
    response = client.post('/login', data={
        'email': student_user.email,
        'password': 'MotDePasse123!'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Ravi de vous revoir" in response.data


def test_login_wrong_password(client, student_user):
    """Vérifie que la connexion échoue en cas de mauvais mot de passe."""
    response = client.post('/login', data={
        'email': student_user.email,
        'password': 'MauvaisMotDePasse'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Adresse e-mail ou mot de passe incorrect" in response.data


def test_logout(client, student_user):
    """Vérifie la déconnexion d'un utilisateur."""
    # Connexion préalable
    client.post('/login', data={
        'email': student_user.email,
        'password': 'MotDePasse123!'
    }, follow_redirects=True)

    # Déconnexion
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"Vous avez" in response.data


def test_protected_routes_require_login(client):
    """Vérifie que l'accès aux pages privées sans authentification redirige vers la connexion."""
    protected_urls = ['/dashboard', '/reservations/create', '/reservations/1']
    for url in protected_urls:
        response = client.get(url, follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.headers['Location']
