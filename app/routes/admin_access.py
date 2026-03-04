from sqlalchemy import func
from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.models import Login, Transaction, Shifts
from app.routes.auth import reset_password, store_user
from app.routes.auth import role_required

admin_access_bp = Blueprint('admin_access', __name__)

LOW_STOCK_THRESHOLD = 1

@admin_access_bp.route('/admin/create-user', methods=['GET', 'POST'])
@role_required('admin')
def create_user():
    if request.method == 'POST':
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        success, msg = store_user(fullname, username, password, role, is_approved = True)
        flash(msg)
        return redirect(url_for('admin_access.create_user'))

    pending_users = Login.query.filter_by(is_approved = False).all()
    return render_template('create_user.html', pending_users=pending_users)

@admin_access_bp.route('/admin/approve-user/<int:uid>')
@role_required('admin')
def approve_user(uid):
    user = db.session.get(Login,uid)

    if user:
        user.is_approved = True
        db.session.commit()
        flash(f"✅ Approved {user.username}")
    
    return redirect(url_for('admin_access.create_user'))

@admin_access_bp.route('/admin/reject-user/<int:uid>')
@role_required('admin')
def reject_user(uid):
    user = db.session.get(Login, uid)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash(f"🗑️ User request for {user.username} rejected and deleted.")
    return redirect(url_for('admin_access.create_user'))

@admin_access_bp.route('/reports/cashiers')
@role_required('admin')
def cashier_report():

    data = db.session.query(
        Transaction.cashier,
        func.count(Transaction.id).label('bills'),
        func.coalesce(func.sum(Transaction.total), 0).label('total_sales')
    ).group_by(
        Transaction.cashier
    ).order_by(
        func.sum(Transaction.total).desc()
    ).all()

    return render_template('report_cashiers.html', data=data)


@admin_access_bp.route("/reports/shifts")
@role_required("admin")
def shift_report():

    hours_calculation = func.round(
        (func.julianday(Shifts.end_time) - func.julianday(Shifts.start_time)) * 24,
        2
    ).label('hours_worked')

    data = db.session.query(
        Shifts.id,
        Shifts.username,
        Shifts.start_time,
        Shifts.end_time,
        hours_calculation,
        func.count(Transaction.id).label('bills'),
        func.coalesce(func.sum(Transaction.total), 0).label('total_sales')
    ).outerjoin(
        Transaction, Transaction.shift_id == Shifts.id
    ).filter(
        Shifts.end_time != None
    ).group_by(
        Shifts.id
    ).order_by(
        Shifts.start_time.desc()
    ).all()

    return render_template('report_shifts.html', data=data)


@admin_access_bp.route("/admin/reset-password", methods=["GET", "POST"])
@role_required("admin")
def admin_reset_password():
    if request.method == 'POST':
        username = request.form['username']
        new_password = request.form['password']

        success = reset_password(username, new_password)

        if success:
            flash(f'Password reset for {username}')
        else:
            flash('User not found.')

    return render_template('admin_reset_password.html')