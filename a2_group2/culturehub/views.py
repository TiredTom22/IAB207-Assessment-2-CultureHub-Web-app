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
    events = db.session.scalar(db.select(Event)).all()
    return render_template('events/index.html', events=events)

@main_bp.route('/profile')
def profile():
    return render_template('events/profile.html')

@main_bp.route('/edit-profile')
def edit_profile():
    return render_template('events/edit_profile.html')

@main_bp.route('/event/create', methods=['GET', 'POST'])
@login_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        # Handle image upload
        image_filename = None
        if form.image.data:
            image_file = form.image.data
            image_filename = secure_filename(image_file.filename)
            image_file.save(os.path.join('culturehub/static/images', image_filename))

        # Create new event
        event = Event(
            name=form.name.data,
            category=form.category.data,
            date=form.date.data,
            location=form.location.data,
            description=form.description.data,
            image=image_filename,
            tickets_available=form.tickets_available.data,
            price=form.price.data,
            acknowledgement=form.acknowledgement.data,
            user_id=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        flash('Event created successfully!')
        return redirect(url_for('main.index'))
    
    return render_template('events/create.html', form=form)