from datetime import date
from flask import Blueprint, render_template, request, abort
from flask_login import current_user
from app.models.room import Room
from app.models.reservation import Reservation
from app.forms.room_forms import RoomFilterForm

rooms_bp = Blueprint('rooms', __name__, url_prefix='/rooms')


@rooms_bp.route('/')
def index():
    """Affichage du catalogue des salles avec recherche et filtres multicritères."""
    form = RoomFilterForm(request.args)

    # Récupérer la liste des bâtiments disponibles pour alimenter dynamiquement le sélecteur
    buildings = [b[0] for b in Room.query.with_entities(Room.building).distinct().order_by(Room.building).all()]
    form.building.choices = [('', 'Tous les bâtiments')] + [(b, b) for b in buildings]

    # Requête de base : par défaut les utilisateurs voient uniquement les salles actives
    query = Room.query
    if not (current_user.is_authenticated and current_user.is_admin):
        query = query.filter(Room.is_active.is_(True))

    # Filtre par texte (nom ou bâtiment ou numéro)
    search_query = request.args.get('search', '').strip()
    if search_query:
        query = query.filter(
            (Room.name.ilike(f"%{search_query}%")) |
            (Room.building.ilike(f"%{search_query}%")) |
            (Room.room_number.ilike(f"%{search_query}%"))
        )

    # Filtre par bâtiment
    building_selected = request.args.get('building', '').strip()
    if building_selected:
        query = query.filter(Room.building == building_selected)

    # Filtre par capacité minimale
    min_capacity = request.args.get('min_capacity', type=int)
    if min_capacity and min_capacity > 0:
        query = query.filter(Room.capacity >= min_capacity)

    # Filtre par équipement
    equipment_query = request.args.get('equipment', '').strip()
    if equipment_query:
        query = query.filter(Room.equipment.ilike(f"%{equipment_query}%"))

    # Tri par bâtiment puis nom
    rooms = query.order_by(Room.building, Room.name).all()

    return render_template(
        'rooms/index.html',
        rooms=rooms,
        form=form,
        total_found=len(rooms)
    )


@rooms_bp.route('/<int:room_id>')
def detail(room_id: int):
    """Fiche détaillée d'une salle avec planning des réservations à venir."""
    room = Room.query.get_or_404(room_id)

    # Si la salle est inactive et que l'utilisateur n'est pas admin, on bloque l'accès
    if not room.is_active and not (current_user.is_authenticated and current_user.is_admin):
        abort(404)

    # Récupérer les réservations confirmées à venir pour cette salle
    today = date.today()
    upcoming_reservations = Reservation.query.filter(
        Reservation.room_id == room.id,
        Reservation.status == 'confirmed',
        Reservation.reservation_date >= today
    ).order_by(Reservation.reservation_date, Reservation.start_time).limit(10).all()

    return render_template(
        'rooms/detail.html',
        room=room,
        upcoming_reservations=upcoming_reservations
    )
