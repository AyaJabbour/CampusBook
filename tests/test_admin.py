from app.models.room import Room
from app.models.reservation import Reservation
from datetime import date, time, timedelta


def test_student_cannot_access_admin_dashboard(client, student_user):
    """Vérifie qu'un simple étudiant reçoit une erreur 403 s'il tente d'accéder à l'administration."""
    client.post('/login', data={'email': student_user.email, 'password': 'MotDePasse123!'})
    response = client.get('/admin/')
    assert response.status_code == 403


def test_student_cannot_access_admin_rooms(client, student_user):
    """Vérifie qu'un étudiant ne peut pas accéder à la gestion des salles."""
    client.post('/login', data={'email': student_user.email, 'password': 'MotDePasse123!'})
    response = client.get('/admin/rooms')
    assert response.status_code == 403


def test_admin_access_dashboard(client, admin_user):
    """Vérifie que l'administrateur accède avec succès au tableau de bord."""
    client.post('/login', data={'email': admin_user.email, 'password': 'AdminSecret123!'})
    response = client.get('/admin/')
    assert response.status_code == 200
    assert b"Tableau de Bord Administrateur" in response.data


def test_admin_create_room(client, admin_user, app):
    """Vérifie que l'administrateur peut créer une nouvelle salle."""
    client.post('/login', data={'email': admin_user.email, 'password': 'AdminSecret123!'})

    response = client.post('/admin/rooms/create', data={
        'name': 'Nouvelle Salle Admin',
        'building': 'Bâtiment Innovation',
        'room_number': 'INN-404',
        'capacity': 40,
        'equipment': 'Projecteur, Caméra 360',
        'description': 'Salle collaborative haute technologie',
        'is_active': 'y'
    }, follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        room = Room.query.filter_by(name='Nouvelle Salle Admin').first()
        assert room is not None
        assert room.capacity == 40
        assert room.is_active is True


def test_admin_toggle_room_status(client, admin_user, sample_room, app):
    """Vérifie que l'administrateur peut désactiver puis réactiver une salle."""
    client.post('/login', data={'email': admin_user.email, 'password': 'AdminSecret123!'})

    # sample_room est active au départ
    assert sample_room.is_active is True

    # Désactivation
    response = client.post(f'/admin/rooms/{sample_room.id}/toggle', follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        from app.extensions import db
        room = db.session.get(Room, sample_room.id)
        assert room.is_active is False

    # Réactivation
    response2 = client.post(f'/admin/rooms/{sample_room.id}/toggle', follow_redirects=True)
    assert response2.status_code == 200
    with app.app_context():
        from app.extensions import db
        room = db.session.get(Room, sample_room.id)
        assert room.is_active is True


def test_admin_can_cancel_any_reservation(client, admin_user, student_user, sample_room, app):
    """Vérifie que l'administrateur peut annuler administrativement une réservation."""
    tomorrow = date.today() + timedelta(days=2)

    with app.app_context():
        from app.services.reservation_service import ReservationService
        res, _ = ReservationService.create_reservation(
            user_id=student_user.id,
            room_id=sample_room.id,
            reservation_date=tomorrow,
            start_time=time(14, 0),
            end_time=time(16, 0),
            purpose="Projet étudiant",
            participants_count=4
        )
        res_id = res.id

    client.post('/login', data={'email': admin_user.email, 'password': 'AdminSecret123!'})

    response = client.post(f'/admin/reservations/{res_id}/cancel', follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        from app.extensions import db
        updated_res = db.session.get(Reservation, res_id)
        assert updated_res.status == 'cancelled'
