import datetime
import bcrypt
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from app import db
from app.models import Login, Shifts
from app.routes.auth import verify_user, store_user

login_bp = Blueprint('login', __name__)


@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash("Username and password are required.")
            return redirect(url_for('login.login'))

        if verify_user(username, password):

            user = Login.query.filter_by(username=username).first()
            if not user.is_approved:
                flash("Your account is pending approval. Please wait for an admin to approve your account.")
                return redirect(url_for('login.login'))

            role = user.role

            if role != 'admin':
                existing_shift = Shifts.query.filter_by(
                    username=username,
                    end_time=None
                ).first()

                if existing_shift:
                    session['shift_id'] = existing_shift.id
                else:
                    new_shift = Shifts(
                        username=username,
                        cashier=username,
                        start_time=datetime.datetime.now()
                    )
                    db.session.add(new_shift)
                    db.session.commit()
                    session['shift_id'] = new_shift.id

            session['username'] = username
            session['role'] = role

            return redirect(url_for('dashboard.dashboard'))

        flash('Invalid username or password')

    return render_template('login.html')

@login_bp.route('/logout')
def logout():
    if 'username' not in session:
        return redirect(url_for('login.login'))

    shift_id = session.get('shift_id')

    if shift_id and session.get('role') != 'admin':
        shift = Shifts.query.get(shift_id)
        if shift and not shift.end_time:
            shift.end_time = datetime.datetime.now()
            db.session.commit()

    session.clear()
    return redirect(url_for('login.login'))

@login_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if 'username' not in session:
        return redirect(url_for('login.login'))

    user = Login.query.filter_by(username=session['username']).first()

    if not user:
        session.clear()
        return redirect(url_for('login.login'))

    if user.role == 'admin':
        flash("Admin password must be reset from admin panel.")
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()

        if not current_password or not new_password:
            flash("All fields are required.")
            return redirect(url_for('login.change_password'))

        if not bcrypt.checkpw(current_password.encode(), user.password):
            flash("Current password is incorrect.")
            return redirect(url_for('login.change_password'))

        hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
        user.password = hashed
        db.session.commit()

        flash("Password updated successfully.")
        return redirect(url_for('dashboard.dashboard'))

    return render_template('change_password.html')


@login_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not fullname or not username or not password:
            flash("All fields are required.")
            return redirect(url_for('login.register'))

        success, message = store_user(
            fullname=fullname,
            username=username,
            password=password
        )

        if success:
            if Login.query.count() == 1:
                first_user = Login.query.filter_by(username=username).first()
                if first_user:
                    first_user.role = 'admin'
                    first_user.is_approved = True
                    db.session.commit()

            flash(message)
            return redirect(url_for('login.login'))

        flash(message)

    return render_template('register.html')