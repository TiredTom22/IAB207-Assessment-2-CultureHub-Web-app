from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('events/index.html')

@main_bp.route('/profile')
def profile():
    return render_template('events/profile.html')