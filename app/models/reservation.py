from datetime import datetime, date, timezone
from app.extensions import db


class Reservation(db.Model):
    """Modèle représentant une réservation d'une salle par un utilisateur."""
    __tablename__ = 'reservations'

    __table_args__ = (
        db.Index('idx_reservation_room_date_status', 'room_id', 'reservation_date', 'status'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id', ondelete='CASCADE'), nullable=False, index=True)
    reservation_date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    purpose = db.Column(db.String(255), nullable=False)
    participants_count = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='confirmed', index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relations
    user = db.relationship('User', back_populates='reservations')
    room = db.relationship('Room', back_populates='reservations')

    @property
    def is_confirmed(self) -> bool:
        """Vérifie si la réservation est confirmée."""
        return self.status == 'confirmed'

    @property
    def is_cancelled(self) -> bool:
        """Vérifie si la réservation est annulée."""
        return self.status == 'cancelled'

    @property
    def is_past(self) -> bool:
        """Indique si la date/heure de fin de la réservation est déjà dépassée."""
        today = date.today()
        if self.reservation_date < today:
            return True
        if self.reservation_date == today:
            now_time = datetime.now().time()
            return self.end_time <= now_time
        return False

    @property
    def can_be_cancelled(self) -> bool:
        """Indique si la réservation est éligible à l'annulation."""
        return self.is_confirmed and not self.is_past

    @property
    def can_be_modified(self) -> bool:
        """Indique si la réservation est éligible à la modification."""
        return self.is_confirmed and not self.is_past

    def __repr__(self) -> str:
        return (
            f"<Reservation {self.id}: Room {self.room_id} on {self.reservation_date} "
            f"[{self.start_time}-{self.end_time}] ({self.status})>"
        )
