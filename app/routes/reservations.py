from datetime import date, datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.room import Room
from app.models.reservation import Reservation
from app.forms.reservation_forms import ReservationForm
from app.services.reservation_service import ReservationService

reservations_bp = Blueprint('reservations', __name__)


@reservations_bp.route('/dashboard')
@login_required
def dashboard():
    """Tableau de bord de l'étudiant connecté."""
    # Si c'est un administrateur qui accède à /dashboard, on le redirige vers l'espace admin
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))

    today = date.today()
    now_time = datetime.now().time()

    # Toutes les réservations de l'étudiant
    all_reservations = Reservation.query.filter_by(user_id=current_user.id).order_by(
        Reservation.reservation_date.desc(), Reservation.start_time.desc()
    ).all()

    upcoming_reservations = []
    past_reservations = []
    cancelled_reservations = []

    for res in all_reservations:
        if res.is_cancelled:
            cancelled_reservations.append(res)
        elif res.reservation_date > today or (res.reservation_date == today and res.end_time > now_time):
            upcoming_reservations.append(res)
        else:
            past_reservations.append(res)

    # Trier les réservations à venir de la plus proche à la plus lointaine
    upcoming_reservations.sort(key=lambda r: (r.reservation_date, r.start_time))

    return render_template(
        'dashboard/student.html',
        upcoming_reservations=upcoming_reservations,
        past_reservations=past_reservations,
        cancelled_reservations=cancelled_reservations,
        total_upcoming=len(upcoming_reservations),
        total_past=len(past_reservations),
        total_cancelled=len(cancelled_reservations)
    )


@reservations_bp.route('/reservations/create', methods=['GET', 'POST'])
@login_required
def create():
    """Création d'une nouvelle réservation."""
    form = ReservationForm()

    # Charger les salles actives pour le champ de sélection
    active_rooms = Room.query.filter_by(is_active=True).order_by(Room.building, Room.name).all()
    form.room_id.choices = [(r.id, f"{r.name} ({r.building} - {r.room_number}) — {r.capacity} places") for r in active_rooms]

    # Pré-sélection de la salle si passée en paramètre d'URL (?room_id=X)
    preselected_room_id = request.args.get('room_id', type=int)
    selected_room = None
    if request.method == 'GET' and preselected_room_id:
        room_exists = any(r.id == preselected_room_id for r in active_rooms)
        if room_exists:
            form.room_id.data = preselected_room_id
            selected_room = db.session.get(Room, preselected_room_id)

    if form.validate_on_submit():
        reservation, error = ReservationService.create_reservation(
            user_id=current_user.id,
            room_id=form.room_id.data,
            reservation_date=form.reservation_date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            purpose=form.purpose.data,
            participants_count=form.participants_count.data
        )

        if error:
            flash(error, "danger")
        else:
            flash("Votre réservation a été confirmée avec succès !", "success")
            return redirect(url_for('reservations.detail', reservation_id=reservation.id))

    return render_template(
        'reservations/create.html',
        form=form,
        selected_room=selected_room,
        active_rooms=active_rooms
    )


@reservations_bp.route('/reservations/<int:reservation_id>')
@login_required
def detail(reservation_id: int):
    """Consultation d'une réservation (sécurisée par vérification du propriétaire ou admin)."""
    reservation = Reservation.query.get_or_404(reservation_id)

    # Sécurité stricte : un étudiant ne peut consulter que ses propres réservations
    if not current_user.is_admin and reservation.user_id != current_user.id:
        abort(403)

    return render_template('reservations/detail.html', reservation=reservation)


@reservations_bp.route('/reservations/<int:reservation_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(reservation_id: int):
    """Modification d'une réservation existante."""
    reservation = Reservation.query.get_or_404(reservation_id)

    # Sécurité stricte d'accès
    if not current_user.is_admin and reservation.user_id != current_user.id:
        abort(403)

    # Vérification d'éligibilité
    if not reservation.can_be_modified:
        flash("Cette réservation ne peut plus être modifiée car elle est déjà passée ou a été annulée.", "warning")
        return redirect(url_for('reservations.detail', reservation_id=reservation.id))

    form = ReservationForm()
    active_rooms = Room.query.filter_by(is_active=True).order_by(Room.building, Room.name).all()
    # Si la salle actuelle de la réservation n'est pas active, l'inclure tout de même dans les options
    current_room = db.session.get(Room, reservation.room_id)
    room_options = {r.id: f"{r.name} ({r.building} - {r.room_number}) — {r.capacity} places" for r in active_rooms}
    if current_room and current_room.id not in room_options:
        room_options[current_room.id] = f"{current_room.name} (Actuellement inactive)"

    form.room_id.choices = list(room_options.items())

    if form.validate_on_submit():
        success, error = ReservationService.update_reservation(
            reservation=reservation,
            room_id=form.room_id.data,
            reservation_date=form.reservation_date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            purpose=form.purpose.data,
            participants_count=form.participants_count.data
        )

        if error:
            flash(error, "danger")
        else:
            flash("Votre réservation a été modifiée avec succès !", "success")
            return redirect(url_for('reservations.detail', reservation_id=reservation.id))

    elif request.method == 'GET':
        form.room_id.data = reservation.room_id
        form.reservation_date.data = reservation.reservation_date
        form.start_time.data = reservation.start_time
        form.end_time.data = reservation.end_time
        form.participants_count.data = reservation.participants_count
        form.purpose.data = reservation.purpose

    return render_template(
        'reservations/edit.html',
        form=form,
        reservation=reservation
    )


@reservations_bp.route('/reservations/<int:reservation_id>/cancel', methods=['POST'])
@login_required
def cancel(reservation_id: int):
    """Annulation d'une réservation."""
    reservation = Reservation.query.get_or_404(reservation_id)

    # Sécurité d'accès
    if not current_user.is_admin and reservation.user_id != current_user.id:
        abort(403)

    success, error = ReservationService.cancel_reservation(reservation)
    if error:
        flash(error, "danger")
    else:
        flash("La réservation a été annulée avec succès. Le créneau est à nouveau disponible.", "info")

    if current_user.is_admin and request.referrer and 'admin' in request.referrer:
        return redirect(url_for('admin.reservations'))
    return redirect(url_for('reservations.dashboard'))
