from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('events/index.html')

@main_bp.route('/profile')
def profile():
    return render_template('events/profile.html')

@main_bp.route('/edit-profile')
def edit_profile():
    return render_template('events/edit_profile.html')

@main_bp.route('/404')
def not_found():
    return render_template('errors/404.html'), 404

@main_bp.route('/500')
def internal_error():
    return render_template('errors/500.html'), 500