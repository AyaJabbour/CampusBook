from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class RoomForm(FlaskForm):
    """Formulaire d'ajout et de modification d'une salle par un administrateur."""
    name = StringField(
        'Nom de la salle',
        validators=[
            DataRequired(message="Le nom de la salle est obligatoire."),
            Length(max=100, message="Le nom ne doit pas dépasser 100 caractères.")
        ],
        render_kw={"placeholder": "Ex: Salle Ada Lovelace"}
    )
    building = StringField(
        'Bâtiment',
        validators=[
            DataRequired(message="Le bâtiment est obligatoire."),
            Length(max=50, message="Le nom du bâtiment ne doit pas dépasser 50 caractères.")
        ],
        render_kw={"placeholder": "Ex: Bâtiment Turing"}
    )
    room_number = StringField(
        'Numéro ou localisation',
        validators=[
            DataRequired(message="Le numéro ou la localisation est obligatoire."),
            Length(max=20, message="La localisation ne doit pas dépasser 20 caractères.")
        ],
        render_kw={"placeholder": "Ex: A-204"}
    )
    capacity = IntegerField(
        'Capacité maximale (places assises)',
        validators=[
            DataRequired(message="La capacité est obligatoire."),
            NumberRange(min=1, max=500, message="La capacité doit être comprise entre 1 et 500.")
        ],
        render_kw={"placeholder": "Ex: 25"}
    )
    equipment = StringField(
        'Équipements (séparés par des virgules)',
        validators=[
            Optional(),
            Length(max=255, message="Les équipements ne doivent pas dépasser 255 caractères.")
        ],
        render_kw={"placeholder": "Ex: Vidéoprojecteur, Wi-Fi HD, Tableau blanc, Prises secteur"}
    )
    description = TextAreaField(
        'Description détaillée',
        validators=[Optional()],
        render_kw={"rows": 4, "placeholder": "Description de la salle, configuration, usages recommandés..."}
    )
    image_filename = StringField(
        'Nom de fichier image (optionnel)',
        validators=[Optional(), Length(max=150)],
        render_kw={"placeholder": "Ex: room_turing.jpg"}
    )
    is_active = BooleanField('Salle active et disponible à la réservation', default=True)
    submit = SubmitField('Enregistrer la salle')


class RoomFilterForm(FlaskForm):
    """Formulaire de recherche et de filtrage des salles."""
    search = StringField(
        'Recherche par nom ou mot-clé',
        validators=[Optional()],
        render_kw={"placeholder": "Ex: Turing, Lovelace, Projet..."}
    )
    building = SelectField(
        'Bâtiment',
        choices=[('', 'Tous les bâtiments')],
        validators=[Optional()]
    )
    min_capacity = IntegerField(
        'Capacité minimale',
        validators=[Optional(), NumberRange(min=1)],
        render_kw={"placeholder": "Ex: 10", "min": "1"}
    )
    equipment = StringField(
        'Équipement requis',
        validators=[Optional()],
        render_kw={"placeholder": "Ex: Vidéoprojecteur, Tableau..."}
    )
    submit = SubmitField('Filtrer')
