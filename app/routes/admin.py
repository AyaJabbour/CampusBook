from functools import wraps
from datetime import date, datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import current_user, login_required
from app.extensions import db
from app.models.room import Room
from app.models.user import User
from app.models.reservation import Reservation
from app.forms.room_forms import RoomForm
from app.services.reservation_service import ReservationService

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Décorateur pour restreindre l'accès exclusivement aux administrateurs."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@admin_required
def dashboard():
    """Tableau de bord administrateur avec statistiques globales et alertes."""
    today = date.today()
    now_time = datetime.now().time()

    total_active_rooms = Room.query.filter_by(is_active=True).count()
    total_inactive_rooms = Room.query.filter_by(is_active=False).count()
    total_users = User.query.count()
    total_reservations = Reservation.query.count()

    # Réservations futures confirmées
    upcoming_reservations_count = Reservation.query.filter(
        Reservation.status == 'confirmed',
        (Reservation.reservation_date > today) |
        ((Reservation.reservation_date == today) & (Reservation.end_time > now_time))
    ).count()

    # 10 réservations les plus récentes créées
    recent_reservations = Reservation.query.order_by(
        Reservation.created_at.desc()
    ).limit(10).all()

    return render_template(
        'dashboard/admin.html',
        total_active_rooms=total_active_rooms,
        total_inactive_rooms=total_inactive_rooms,
        total_users=total_users,
        total_reservations=total_reservations,
        upcoming_reservations_count=upcoming_reservations_count,
        recent_reservations=recent_reservations
    )


@admin_bp.route('/rooms')
@admin_required
def rooms():
    """Gestion complète des salles par l'administrateur."""
    all_rooms = Room.query.order_by(Room.building, Room.name).all()
    return render_template('dashboard/admin_rooms.html', rooms=all_rooms)


@admin_bp.route('/rooms/create', methods=['GET', 'POST'])
@admin_required
def create_room():
    """Création d'une nouvelle salle d'université."""
    form = RoomForm()
    if form.validate_on_submit():
        room = Room(
            name=form.name.data.strip(),
            building=form.building.data.strip(),
            room_number=form.room_number.data.strip(),
            capacity=form.capacity.data,
            equipment=form.equipment.data.strip() if form.equipment.data else None,
            description=form.description.data.strip() if form.description.data else None,
            image_filename=form.image_filename.data.strip() if form.image_filename.data else None,
            is_active=form.is_active.data
        )
        try:
            db.session.add(room)
            db.session.commit()
            flash(f"La salle '{room.name}' a été créée avec succès !", "success")
            return redirect(url_for('admin.rooms'))
        except Exception as e:
            db.session.rollback()
            flash("Une erreur est survenue lors de la création de la salle.", "danger")

    return render_template('dashboard/room_form.html', form=form, title="Ajouter une salle")


@admin_bp.route('/rooms/<int:room_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_room(room_id: int):
    """Modification d'une salle existante."""
    room = Room.query.get_or_404(room_id)
    form = RoomForm()

    if form.validate_on_submit():
        room.name = form.name.data.strip()
        room.building = form.building.data.strip()
        room.room_number = form.room_number.data.strip()
        room.capacity = form.capacity.data
        room.equipment = form.equipment.data.strip() if form.equipment.data else None
        room.description = form.description.data.strip() if form.description.data else None
        room.image_filename = form.image_filename.data.strip() if form.image_filename.data else None
        room.is_active = form.is_active.data

        try:
            db.session.commit()
            flash(f"La salle '{room.name}' a été mise à jour avec succès !", "success")
            return redirect(url_for('admin.rooms'))
        except Exception:
            db.session.rollback()
            flash("Une erreur est survenue lors de la mise à jour de la salle.", "danger")

    elif request.method == 'GET':
        form.name.data = room.name
        form.building.data = room.building
        form.room_number.data = room.room_number
        form.capacity.data = room.capacity
        form.equipment.data = room.equipment
        form.description.data = room.description
        form.image_filename.data = room.image_filename
        form.is_active.data = room.is_active

    return render_template('dashboard/room_form.html', form=form, title=f"Modifier {room.name}", room=room)


@admin_bp.route('/rooms/<int:room_id>/toggle', methods=['POST'])
@admin_required
def toggle_room(room_id: int):
    """Activation ou désactivation d'une salle."""
    room = Room.query.get_or_404(room_id)
    room.is_active = not room.is_active
    db.session.commit()

    statut = "activée" if room.is_active else "désactivée"
    flash(f"La salle '{room.name}' est maintenant {statut}.", "info")
    return redirect(url_for('admin.rooms'))


@admin_bp.route('/reservations')
@admin_required
def reservations():
    """Consultation globale de toutes les réservations avec filtre de statut."""
    status_filter = request.args.get('status', 'all')
    query = Reservation.query

    if status_filter in ['confirmed', 'cancelled']:
        query = query.filter_by(status=status_filter)

    all_res = query.order_by(Reservation.reservation_date.desc(), Reservation.start_time.desc()).all()
    return render_template('dashboard/admin_reservations.html', reservations=all_res, current_status=status_filter)


@admin_bp.route('/reservations/<int:reservation_id>/cancel', methods=['POST'])
@admin_required
def cancel_reservation(reservation_id: int):
    """Annulation administrative d'une réservation."""
    reservation = Reservation.query.get_or_404(reservation_id)
    success, error = ReservationService.cancel_reservation(reservation)
    if error:
        flash(error, "danger")
    else:
        flash(f"La réservation #{reservation.id} a été annulée par l'administrateur.", "warning")

    return redirect(url_for('admin.reservations'))
