from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.debug = True
    app.secret_key = 'somesecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sitedata.sqlite'
    db.init_app(app)

    Bootstrap5(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.scalar(db.select(User).where(User.id == user_id))

    from . import views
    app.register_blueprint(views.main_bp)

    from . import auth
    app.register_blueprint(auth.auth_bp)

    # Create all tables and seed demo users on first run
    with app.app_context():
        db.create_all()
        _seed_demo_users()
        
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        return render_template('errors/500.html'), 500

    return app


def _seed_demo_users():
    """Insert hardcoded demo users into the DB if they don't already exist."""
    from .models import User
    from flask_bcrypt import generate_password_hash

    demo_users = [
        {'name': 'admin',    'email': 'admin@culturehub.com',    'phone': '0400000001', 'address': '123 Admin St, Brisbane', 'password': 'password'},
        {'name': 'amogh',    'email': 'amogh@culturehub.com',    'phone': '0400000002', 'address': '456 QUT Ave, Brisbane',   'password': 'qut2026'},
        {'name': 'thompson', 'email': 'thompson@culturehub.com', 'phone': '0400000003', 'address': '789 Hub Rd, Brisbane',    'password': 'qut2026'},
        {'name': 'glenda',   'email': 'glenda@culturehub.com',   'phone': '0400000004', 'address': '321 Culture Ln, Brisbane','password': 'qut2026'},
        {'name': 'sohee',    'email': 'sohee@culturehub.com',    'phone': '0400000005', 'address': '654 Event Blvd, Brisbane','password': 'qut2026'},
    ]

    for u in demo_users:
        exists = db.session.scalar(db.select(User).where(User.name == u['name']))
        if not exists:
            new_user = User(
                name=u['name'],
                email=u['email'],
                phone=u['phone'],
                address=u['address'],
                password_hash=generate_password_hash(u['password']).decode('utf-8')
            )
            db.session.add(new_user)

    db.session.commit()