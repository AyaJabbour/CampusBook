from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(UserMixin, db.Model):
    """Modèle représentant un utilisateur (étudiant ou administrateur)."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relation avec les réservations
    reservations = db.relationship(
        'Reservation',
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='dynamic',
        order_by='desc(Reservation.reservation_date)'
    )

    def set_password(self, password: str) -> None:
        """Hache et enregistre le mot de passe."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Vérifie la validité du mot de passe fourni."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        """Indique si l'utilisateur a le rôle administrateur."""
        return self.role == 'admin'

    @property
    def is_student(self) -> bool:
        """Indique si l'utilisateur a le rôle étudiant."""
        return self.role == 'student'

    def __repr__(self) -> str:
        return f"<User {self.id}: {self.email} ({self.role})>"
