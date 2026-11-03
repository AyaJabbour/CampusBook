from datetime import datetime, timezone
from app.extensions import db


class Room(db.Model):
    """Modèle représentant une salle réservable de l'université."""
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    building = db.Column(db.String(50), nullable=False, index=True)
    room_number = db.Column(db.String(20), nullable=False)
    capacity = db.Column(db.Integer, nullable=False, index=True)
    equipment = db.Column(db.String(255), nullable=True)
    image_filename = db.Column(db.String(150), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relation avec les réservations
    reservations = db.relationship(
        'Reservation',
        back_populates='room',
        cascade='all, delete-orphan',
        lazy='dynamic',
        order_by='desc(Reservation.reservation_date)'
    )

    @property
    def equipment_list(self) -> list[str]:
        """Retourne la liste propre des équipements découpés par virgule."""
        if not self.equipment:
            return []
        return [item.strip() for item in self.equipment.split(',') if item.strip()]

    def __repr__(self) -> str:
        return f"<Room {self.id}: {self.name} ({self.building}-{self.room_number})>"
