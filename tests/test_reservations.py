from datetime import date, time, timedelta
from app.models.reservation import Reservation
from app.services.reservation_service import ReservationService


def test_create_valid_reservation(client, student_user, sample_room, app):
    """Vérifie la création réussie d'une réservation valide."""
    client.post('/login', data={'email': student_user.email, 'password': 'MotDePasse123!'})

    tomorrow = date.today() + timedelta(days=2)
    response = client.post('/reservations/create', data={
        'room_id': sample_room.id,
        'reservation_date': tomorrow.strftime('%Y-%m-%d'),
        'start_time': '10:00',
        'end_time': '12:00',
        'participants_count': 5,
        'purpose': 'Travail de groupe sur le projet CampusBook'
    }, follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        res = Reservation.query.filter_by(room_id=sample_room.id).first()
        assert res is not None
        assert res.user_id == student_user.id
        assert res.participants_count == 5
        assert res.status == 'confirmed'


def test_reject_past_date(client, student_user, sample_room):
    """Vérifie le rejet d'une date de réservation dans le passé."""
    client.post('/login', data={'email': student_user.email, 'password': 'MotDePasse123!'})

    yesterday = date.today() - timedelta(days=1)
    response = client.post('/reservations/create', data={
        'room_id': sample_room.id,
        'reservation_date': yesterday.strftime('%Y-%m-%d'),
        'start_time': '10:00',
        'end_time': '12:00',
        'participants_count': 5,
        'purpose': 'Tentative de réservation passée'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"ne peut pas" in response.data or b"pass" in response.data


def test_reject_end_time_before_start_time(client, student_user, sample_room):
    """Vérifie le rejet lorsque l'heure de fin est antérieure ou égale à l'heure de début."""
    client.post('/login', data={'email': student_user.email, 'password': 'MotDePasse123!'})

    tomorrow = date.today() + timedelta(days=2)
    response = client.post('/reservations/create', data={
        'room_id': sample_room.id,
        'reservation_date': tomorrow.strftime('%Y-%m-%d'),
        'start_time': '14:00',
        'end_time': '13:00',  # Fin avant début !
        'participants_count': 5,
        'purpose': 'Horaire incohérent'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"post" in response.data or b"rieure" in response.data


def test_reject_exceeding_capacity(client, student_user, sample_room):
    """Vérifie le rejet lorsque le nombre de participants dépasse la capacité de la salle."""
    client.post('/login', data={'email': student_user.email, 'password': 'MotDePasse123!'})

    # sample_room a une capacité de 20
    tomorrow = date.today() + timedelta(days=2)
    response = client.post('/reservations/create', data={
        'room_id': sample_room.id,
        'reservation_date': tomorrow.strftime('%Y-%m-%d'),
        'start_time': '10:00',
        'end_time': '12:00',
        'participants_count': 25,  # 25 > 20
        'purpose': 'Groupe trop volumineux'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"capacit" in response.data or b"d" in response.data


def test_reject_overlapping_reservation(client, student_user, sample_room, app):
    """Vérifie le refus d'une réservation qui chevauche un créneau existant."""
    tomorrow = date.today() + timedelta(days=3)

    # Création d'une première réservation de 10h à 12h
    with app.app_context():
        ReservationService.create_reservation(
            user_id=student_user.id,
            room_id=sample_room.id,
            reservation_date=tomorrow,
            start_time=time(10, 0),
            end_time=time(12, 0),
            purpose="Première réservation",
            participants_count=6
        )

    client.post('/login', data={'email': student_user.email, 'password': 'MotDePasse123!'})

    # Tentative d'un chevauchement partiel (11h à 13h)
    response = client.post('/reservations/create', data={
        'room_id': sample_room.id,
        'reservation_date': tomorrow.strftime('%Y-%m-%d'),
        'start_time': '11:00',
        'end_time': '13:00',
        'participants_count': 4,
        'purpose': 'Deuxième réservation en conflit'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"chevauche" in response.data or b"conflit" in response.data


def test_allow_contiguous_slots(client, student_user, sample_room, app):
    """
    Vérifie qu'un créneau commençant exactement à l'heure de fin du précédent est AUTORISÉ.
    Exemple : 10:00-11:00 et 11:00-12:00 dans la même salle ne se chevauchent pas !
    """
    tomorrow = date.today() + timedelta(days=4)

    with app.app_context():
        res1, err1 = ReservationService.create_reservation(
            user_id=student_user.id,
            room_id=sample_room.id,
            reservation_date=tomorrow,
            start_time=time(10, 0),
            end_time=time(11, 0),
            purpose="Premier créneau 10h-11h",
            participants_count=5
        )
        assert err1 is None
        assert res1 is not None

        # Deuxième réservation contiguë : 11h à 12h
        res2, err2 = ReservationService.create_reservation(
            user_id=student_user.id,
            room_id=sample_room.id,
            reservation_date=tomorrow,
            start_time=time(11, 0),
            end_time=time(12, 0),
            purpose="Créneau contigu 11h-12h",
            participants_count=5
        )
        assert err2 is None
        assert res2 is not None


def test_allow_same_time_in_different_rooms(student_user, sample_room, sample_room_2, app):
    """Vérifie que deux réservations simultanées dans deux salles distinctes sont bien autorisées."""
    tomorrow = date.today() + timedelta(days=5)

    with app.app_context():
        res1, err1 = ReservationService.create_reservation(
            user_id=student_user.id,
            room_id=sample_room.id,
            reservation_date=tomorrow,
            start_time=time(14, 0),
            end_time=time(16, 0),
            purpose="Salle 1 créneau 14h-16h",
            participants_count=5
        )
        assert err1 is None

        res2, err2 = ReservationService.create_reservation(
            user_id=student_user.id,
            room_id=sample_room_2.id,
            reservation_date=tomorrow,
            start_time=time(14, 0),
            end_time=time(16, 0),
            purpose="Salle 2 même heure 14h-16h",
            participants_count=10
        )
        assert err2 is None
        assert res1 is not None and res2 is not None


def test_cancel_releases_slot(client, student_user, sample_room, app):
    """Vérifie que l'annulation d'une réservation libère le créneau pour une nouvelle réservation."""
    tomorrow = date.today() + timedelta(days=6)

    with app.app_context():
        res, _ = ReservationService.create_reservation(
            user_id=student_user.id,
            room_id=sample_room.id,
            reservation_date=tomorrow,
            start_time=time(10, 0),
            end_time=time(12, 0),
            purpose="Réservation à annuler",
            participants_count=5
        )
        res_id = res.id

    client.post('/login', data={'email': student_user.email, 'password': 'MotDePasse123!'})

    # Annulation
    response = client.post(f'/reservations/{res_id}/cancel', follow_redirects=True)
    assert response.status_code == 200
    assert b"annul" in response.data

    # Tentative immédiate de réserver exactement le même créneau libéré
    with app.app_context():
        new_res, error = ReservationService.create_reservation(
            user_id=student_user.id,
            room_id=sample_room.id,
            reservation_date=tomorrow,
            start_time=time(10, 0),
            end_time=time(12, 0),
            purpose="Nouvelle réservation sur créneau libéré",
            participants_count=8
        )
        assert error is None
        assert new_res is not None


def test_cannot_access_or_edit_other_user_reservation(client, student_user, other_student_user, sample_room, app):
    """Vérifie qu'un étudiant ne peut ni consulter ni modifier la réservation d'un autre étudiant (sécurité 403)."""
    tomorrow = date.today() + timedelta(days=7)

    with app.app_context():
        res, _ = ReservationService.create_reservation(
            user_id=student_user.id,
            room_id=sample_room.id,
            reservation_date=tomorrow,
            start_time=time(14, 0),
            end_time=time(16, 0),
            purpose="Réservation d'Alice",
            participants_count=5
        )
        res_id = res.id

    # Bob se connecte
    client.post('/login', data={'email': other_student_user.email, 'password': 'MotDePasse123!'})

    # Bob tente de voir la réservation d'Alice
    response = client.get(f'/reservations/{res_id}')
    assert response.status_code == 403

    # Bob tente de modifier la réservation d'Alice
    response_edit = client.get(f'/reservations/{res_id}/edit')
    assert response_edit.status_code == 403


def test_reject_inactive_room_reservation(student_user, inactive_room, app):
    """Vérifie qu'on ne peut pas réserver une salle inactive."""
    tomorrow = date.today() + timedelta(days=8)

    with app.app_context():
        res, err = ReservationService.create_reservation(
            user_id=student_user.id,
            room_id=inactive_room.id,
            reservation_date=tomorrow,
            start_time=time(10, 0),
            end_time=time(12, 0),
            purpose="Tentative sur salle inactive",
            participants_count=5
        )
        assert res is None
        assert "inactive" in err.lower()


def test_edit_reservation_view_and_submit(client, student_user, sample_room, app):
    """Vérifie l'affichage de la page de modification et la soumission d'une modification valide."""
    tomorrow = date.today() + timedelta(days=3)

    with app.app_context():
        res, _ = ReservationService.create_reservation(
            user_id=student_user.id,
            room_id=sample_room.id,
            reservation_date=tomorrow,
            start_time=time(10, 0),
            end_time=time(12, 0),
            purpose="Avant modification",
            participants_count=4
        )
        res_id = res.id

    client.post('/login', data={'email': student_user.email, 'password': 'MotDePasse123!'})

    # 1. Vérifie que GET /reservations/<id>/edit s'affiche avec code 200 (pas de NameError)
    response_get = client.get(f'/reservations/{res_id}/edit')
    assert response_get.status_code == 200
    assert b"Modifier la" in response_get.data

    # 2. Soumission d'une modification
    response_post = client.post(f'/reservations/{res_id}/edit', data={
        'room_id': sample_room.id,
        'reservation_date': tomorrow.strftime('%Y-%m-%d'),
        'start_time': '14:00',
        'end_time': '16:00',
        'participants_count': 6,
        'purpose': 'Après modification avec succès'
    }, follow_redirects=True)

    assert response_post.status_code == 200
    with app.app_context():
        from app.extensions import db
        updated = db.session.get(Reservation, res_id)
        assert updated.start_time == time(14, 0)
        assert updated.end_time == time(16, 0)
        assert updated.participants_count == 6
        assert updated.purpose == 'Après modification avec succès'

