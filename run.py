import os
from app import create_app, db
from app.models.user import User
from app.models.room import Room
from app.models.reservation import Reservation

app = create_app(os.environ.get('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
    """Rend disponibles les modèles dans la commande 'flask shell'."""
    return {
        'db': db,
        'User': User,
        'Room': Room,
        'Reservation': Reservation
    }


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
