from flask import Blueprint

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return '<h1>CultureHub Webpage Here</h1>'