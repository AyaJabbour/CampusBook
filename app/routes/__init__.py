from app.routes.main import main_bp
from app.routes.auth import auth_bp
from app.routes.rooms import rooms_bp
from app.routes.reservations import reservations_bp
from app.routes.admin import admin_bp

__all__ = ['main_bp', 'auth_bp', 'rooms_bp', 'reservations_bp', 'admin_bp']
