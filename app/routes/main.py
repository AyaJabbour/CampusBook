from datetime import date
from flask import Blueprint, render_template
from app.models.room import Room
from app.models.user import User
from app.models.reservation import Reservation

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Page d'accueil avec présentation de l'application et statistiques réelles."""
    total_rooms = Room.query.filter_by(is_active=True).count()
    total_users = User.query.count()
    total_reservations = Reservation.query.filter_by(status='confirmed').count()
    
    # 3 salles mises en avant
    featured_rooms = Room.query.filter_by(is_active=True).limit(3).all()

    return render_template(
        'main/index.html',
        total_rooms=total_rooms,
        total_users=total_users,
        total_reservations=total_reservations,
        featured_rooms=featured_rooms
    )


@main_bp.route('/about')
def about():
    """Présentation du projet académique et de l'architecture."""
    return render_template('main/about.html')
