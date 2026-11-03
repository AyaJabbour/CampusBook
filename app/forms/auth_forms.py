from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User


class LoginForm(FlaskForm):
    """Formulaire de connexion."""
    email = StringField(
        'Adresse e-mail universitaire',
        validators=[
            DataRequired(message="L'adresse e-mail est obligatoire."),
            Email(message="Veuillez saisir une adresse e-mail valide.")
        ],
        render_kw={"placeholder": "etudiant@univ-paris.fr", "autofocus": True}
    )
    password = PasswordField(
        'Mot de passe',
        validators=[
            DataRequired(message="Le mot de passe est obligatoire.")
        ],
        render_kw={"placeholder": "••••••••"}
    )
    remember_me = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')


class RegisterForm(FlaskForm):
    """Formulaire d'inscription étudiant."""
    full_name = StringField(
        'Nom complet',
        validators=[
            DataRequired(message="Le nom complet est obligatoire."),
            Length(min=3, max=100, message="Le nom doit comporter entre 3 et 100 caractères.")
        ],
        render_kw={"placeholder": "Camille Dupont", "autofocus": True}
    )
    email = StringField(
        'Adresse e-mail universitaire',
        validators=[
            DataRequired(message="L'adresse e-mail est obligatoire."),
            Email(message="Veuillez saisir une adresse e-mail valide."),
            Length(max=120)
        ],
        render_kw={"placeholder": "etudiant@univ-paris.fr"}
    )
    password = PasswordField(
        'Mot de passe',
        validators=[
            DataRequired(message="Le mot de passe est obligatoire."),
            Length(min=6, message="Le mot de passe doit comporter au moins 6 caractères.")
        ],
        render_kw={"placeholder": "Au moins 6 caractères"}
    )
    password_confirm = PasswordField(
        'Confirmer le mot de passe',
        validators=[
            DataRequired(message="Veuillez confirmer votre mot de passe."),
            EqualTo('password', message="Les deux mots de passe ne correspondent pas.")
        ],
        render_kw={"placeholder": "Retapez votre mot de passe"}
    )
    submit = SubmitField("S'inscrire")

    def validate_email(self, email):
        """Vérifie que l'adresse e-mail n'est pas déjà utilisée."""
        user = User.query.filter_by(email=email.data.strip().lower()).first()
        if user:
            raise ValidationError("Cette adresse e-mail est déjà associée à un compte.")
