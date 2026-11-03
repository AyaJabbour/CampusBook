import os
from datetime import time
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    """Configuration de base de l'application CampusBook."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'campusbook-dev-insecure-secret-key-12345')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(basedir, 'campusbook.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    
    # Horaires d'ouverture de l'université
    OPENING_TIME = time(8, 0)   # 08:00
    CLOSING_TIME = time(20, 0)  # 20:00
    
    # Durée maximale d'une réservation (en heures)
    MAX_RESERVATION_HOURS = 4
    
    # Rôles utilisateurs
    ROLE_STUDENT = 'student'
    ROLE_ADMIN = 'admin'
    ROLES = [ROLE_STUDENT, ROLE_ADMIN]
    
    # Statuts de réservation
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'
    RESERVATION_STATUSES = [STATUS_CONFIRMED, STATUS_CANCELLED]


class DevelopmentConfig(Config):
    """Configuration pour l'environnement de développement."""
    DEBUG = True


class TestingConfig(Config):
    """Configuration pour l'environnement de test automatisé."""
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Configuration pour la production."""
    DEBUG = False
    TESTING = False
    # En production, SECRET_KEY doit obligatoirement être spécifiée
    SECRET_KEY = os.environ.get('SECRET_KEY')


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
