from urllib.parse import urlsplit
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User
from app.forms.auth_forms import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Inscription d'un nouvel étudiant."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            full_name=form.full_name.data.strip(),
            email=form.email.data.strip().lower(),
            role='student'  # Sécurité : le rôle administrateur ne peut JAMAIS être attribué via le formulaire
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash("Votre compte étudiant a été créé avec succès ! Vous pouvez maintenant vous connecter.", "success")
            return redirect(url_for('auth.login'))
        except Exception:
            db.session.rollback()
            flash("Une erreur est survenue lors de l'enregistrement de votre compte.", "danger")

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Connexion d'un utilisateur existant (étudiant ou administrateur)."""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('reservations.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash(f"Ravi de vous revoir, {user.full_name} !", "success")

            next_page = request.args.get('next')
            # Sécurité contre les redirections ouvertes
            if not next_page or urlsplit(next_page).netloc != '':
                if user.is_admin:
                    next_page = url_for('admin.dashboard')
                else:
                    next_page = url_for('reservations.dashboard')
            return redirect(next_page)
        else:
            flash("Adresse e-mail ou mot de passe incorrect.", "danger")

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Déconnexion de l'utilisateur."""
    logout_user()
    flash("Vous avez été déconnecté avec succès.", "info")
    return redirect(url_for('main.index'))
