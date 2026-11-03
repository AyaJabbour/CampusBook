from flask_wtf import FlaskForm
from wtforms import DateField, TimeField, IntegerField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length


class ReservationForm(FlaskForm):
    """Formulaire de création et de modification d'une réservation."""
    room_id = SelectField(
        'Salle à réserver',
        coerce=int,
        validators=[DataRequired(message="Veuillez sélectionner une salle.")]
    )
    reservation_date = DateField(
        'Date de la réservation',
        format='%Y-%m-%d',
        validators=[DataRequired(message="La date est obligatoire.")],
        render_kw={"type": "date"}
    )
    start_time = TimeField(
        'Heure de début',
        format='%H:%M',
        validators=[DataRequired(message="L'heure de début est obligatoire.")],
        render_kw={"type": "time"}
    )
    end_time = TimeField(
        'Heure de fin',
        format='%H:%M',
        validators=[DataRequired(message="L'heure de fin est obligatoire.")],
        render_kw={"type": "time"}
    )
    participants_count = IntegerField(
        'Nombre de participants prévus',
        validators=[
            DataRequired(message="Le nombre de participants est obligatoire."),
            NumberRange(min=1, max=500, message="Le nombre de participants doit être au minimum de 1.")
        ],
        render_kw={"placeholder": "Ex: 6", "min": "1"}
    )
    purpose = TextAreaField(
        'Motif de la réservation',
        validators=[
            DataRequired(message="Le motif de la réservation est obligatoire."),
            Length(min=5, max=255, message="Le motif doit comporter entre 5 et 255 caractères.")
        ],
        render_kw={
            "rows": 3,
            "placeholder": "Ex: Réunion de projet tuteuré en informatique - Préparation de la soutenance."
        }
    )
    submit = SubmitField('Confirmer la réservation')
