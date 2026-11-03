from datetime import datetime, date, time
from typing import Optional, Tuple, List
from flask import current_app
from app.extensions import db
from app.models.room import Room
from app.models.reservation import Reservation


class ReservationService:
    """Service gérant la logique métier des réservations et la détection des conflits."""

    @staticmethod
    def validate_slot_rules(
        room: Room,
        reservation_date: date,
        start_time: time,
        end_time: time,
        participants_count: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Valide les contraintes de base d'un créneau :
        - La salle doit être active
        - La date ne doit pas être passée
        - L'heure de fin doit être strictement supérieure à l'heure de début
        - Le créneau doit être compris dans les horaires d'ouverture
        - Le nombre de participants ne doit pas dépasser la capacité de la salle
        """
        # Vérification du statut de la salle
        if not room.is_active:
            return False, "Cette salle est actuellement inactive et ne peut pas être réservée."

        today = date.today()
        # Vérification date passée
        if reservation_date < today:
            return False, "La date de réservation ne peut pas être dans le passé."

        # Si c'est aujourd'hui, l'heure de début ne doit pas être déjà dépassée
        if reservation_date == today:
            now_time = datetime.now().time()
            if start_time < now_time:
                return False, "L'heure de début ne peut pas être déjà dépassée pour aujourd'hui."

        # Vérification ordre des heures
        if end_time <= start_time:
            return False, "L'heure de fin doit être strictement postérieure à l'heure de début."

        # Vérification des horaires d'ouverture de l'université
        opening = current_app.config.get('OPENING_TIME', time(8, 0))
        closing = current_app.config.get('CLOSING_TIME', time(20, 0))
        if start_time < opening or end_time > closing:
            return False, f"Les réservations doivent être comprises entre {opening.strftime('%H:%M')} et {closing.strftime('%H:%M')}."

        # Vérification de la capacité
        if participants_count <= 0:
            return False, "Le nombre de participants doit être supérieur à zéro."
        if participants_count > room.capacity:
            return False, f"Le nombre de participants ({participants_count}) dépasse la capacité maximale de la salle ({room.capacity} places)."

        return True, None

    @staticmethod
    def get_conflicting_reservations(
        room_id: int,
        reservation_date: date,
        start_time: time,
        end_time: time,
        exclude_reservation_id: Optional[int] = None
    ) -> List[Reservation]:
        """
        Recherche les réservations actives pour la même salle et la même date
        qui se chevauchent avec l'intervalle [start_time, end_time].
        
        Condition de conflit mathématique :
        Deux intervalles [A, B] et [C, D] se chevauchent si :
        A < D ET B > C
        (les réservations contiguës où A == D ou B == C ne se chevauchent pas).
        """
        query = Reservation.query.filter(
            Reservation.room_id == room_id,
            Reservation.reservation_date == reservation_date,
            Reservation.status == current_app.config.get('STATUS_CONFIRMED', 'confirmed'),
            Reservation.start_time < end_time,
            Reservation.end_time > start_time
        )

        if exclude_reservation_id:
            query = query.filter(Reservation.id != exclude_reservation_id)

        return query.all()

    @classmethod
    def check_availability(
        cls,
        room: Room,
        reservation_date: date,
        start_time: time,
        end_time: time,
        participants_count: int,
        exclude_reservation_id: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Effectue la validation complète (règles métier + détection de conflit).
        """
        # 1. Règles générales
        valid, error = cls.validate_slot_rules(
            room, reservation_date, start_time, end_time, participants_count
        )
        if not valid:
            return False, error

        # 2. Détection de chevauchement
        conflicts = cls.get_conflicting_reservations(
            room_id=room.id,
            reservation_date=reservation_date,
            start_time=start_time,
            end_time=end_time,
            exclude_reservation_id=exclude_reservation_id
        )

        if conflicts:
            conflicting = conflicts[0]
            start_str = conflicting.start_time.strftime('%H:%M')
            end_str = conflicting.end_time.strftime('%H:%M')
            return False, (
                f"Ce créneau chevauche une réservation existante dans cette salle "
                f"de {start_str} à {end_str}."
            )

        return True, None

    @classmethod
    def create_reservation(
        cls,
        user_id: int,
        room_id: int,
        reservation_date: date,
        start_time: time,
        end_time: time,
        purpose: str,
        participants_count: int
    ) -> Tuple[Optional[Reservation], Optional[str]]:
        """
        Crée une réservation de manière transactionnelle après validation stricte.
        """
        room = db.session.get(Room, room_id)
        if not room:
            return None, "Salle introuvable."

        is_available, error_msg = cls.check_availability(
            room=room,
            reservation_date=reservation_date,
            start_time=start_time,
            end_time=end_time,
            participants_count=participants_count
        )

        if not is_available:
            return None, error_msg

        try:
            reservation = Reservation(
                user_id=user_id,
                room_id=room_id,
                reservation_date=reservation_date,
                start_time=start_time,
                end_time=end_time,
                purpose=purpose.strip(),
                participants_count=participants_count,
                status=current_app.config.get('STATUS_CONFIRMED', 'confirmed')
            )
            db.session.add(reservation)
            db.session.commit()
            return reservation, None
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur lors de la création de la réservation : {e}")
            return None, "Une erreur inattendue est survenue lors de l'enregistrement de la réservation."

    @classmethod
    def update_reservation(
        cls,
        reservation: Reservation,
        room_id: int,
        reservation_date: date,
        start_time: time,
        end_time: time,
        purpose: str,
        participants_count: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Modifie une réservation existante avec vérification de non-conflit
        (en excluant la réservation elle-même).
        """
        if not reservation.can_be_modified:
            return False, "Cette réservation ne peut plus être modifiée (soit annulée, soit déjà passée)."

        room = db.session.get(Room, room_id)
        if not room:
            return False, "Salle introuvable."

        is_available, error_msg = cls.check_availability(
            room=room,
            reservation_date=reservation_date,
            start_time=start_time,
            end_time=end_time,
            participants_count=participants_count,
            exclude_reservation_id=reservation.id
        )

        if not is_available:
            return False, error_msg

        try:
            reservation.room_id = room_id
            reservation.reservation_date = reservation_date
            reservation.start_time = start_time
            reservation.end_time = end_time
            reservation.purpose = purpose.strip()
            reservation.participants_count = participants_count
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur lors de la modification de la réservation : {e}")
            return False, "Une erreur inattendue est survenue lors de la mise à jour."

    @classmethod
    def cancel_reservation(cls, reservation: Reservation) -> Tuple[bool, Optional[str]]:
        """
        Annule une réservation sans la supprimer de l'historique.
        """
        if not reservation.can_be_cancelled:
            return False, "Cette réservation ne peut pas être annulée (déjà passée ou déjà annulée)."

        try:
            reservation.status = current_app.config.get('STATUS_CANCELLED', 'cancelled')
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur lors de l'annulation de la réservation : {e}")
            return False, "Une erreur est survenue lors de l'annulation."
