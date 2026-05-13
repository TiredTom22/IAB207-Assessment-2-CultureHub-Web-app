from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from .forms import EventForm
from .models import Event
from . import db
import os
from werkzeug.utils import secure_filename

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