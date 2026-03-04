from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from app import db
from app.models import DeliveryLocation, Coupon
import random, string

features_bp = Blueprint('features', __name__)

@features_bp.route('/coupons', methods=['GET', 'POST'])
def manage_coupons():
    if 'username' not in session or session.get('role') != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
    
    if request.method == 'POST':
        code = request.form.get('code','').strip().upper()

        if not code:
            code = ''.join(random.choices(string.ascii_upper + string.digits, k = 8))

        disc_type = request.form['discount_type']
        value = float(request.form['discount_value'])
        limit = int(request.form['usage_limit'])

        try:
            new_coupon = Coupon(code=code, discount_type=disc_type, discount_value=value, usage_limit=limit)

            db.session.add(new_coupon)
            db.session.commit()

            flash(f'✅ Coupon {code} created successfully!', 'success')
        except Exception as e:
            flash(f"❌ Error: Coupon code '{code}' already exists.")

    coupons = db.session.query(Coupon).order_by(Coupon.id.desc()).all()

    return render_template("manage_coupons.html", coupons=coupons)
    
@features_bp.route('/delete_coupon/<int:cid>')
def delete_coupons(cid):
    if session.get('role') == 'admin':
        coupon = db.session.query(Coupon).filter_by(id=cid).first()
        if coupon:
            db.session.delete(coupon)
            db.session.commit()
            flash(f'✅ Coupon {coupon.code} deleted successfully!', 'success')
        else:
            flash(f'❌ Coupon with ID {cid} not found.', 'danger')
    else:
        flash('Access denied. Admins only.', 'danger')
    return redirect(url_for('features.manage_coupons'))

@features_bp.route('/delivery', methods=['GET', 'POST'])
def manage_delivery():
    if 'username' not in session or session.get('role') != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        pincode = request.form.get('pincode','').strip()
        fee = float(request.form.get('delivery_fee', 0.0))

        if not pincode:
            flash('❌ Pincode cannot be empty.', 'danger')

        else:
            try:
                new_loc = DeliveryLocation(pincode = pincode, delivery_fee = fee)
                db.session.add(new_loc)
                db.session.commit()
                flash(f'✅ Delivery location {pincode} added successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f"❌ Error: Pincode '{pincode}' already exists.", 'danger')

    locations = db.session.query(DeliveryLocation).order_by(DeliveryLocation.id.desc()).all()

    return render_template('manage_delivery.html', locations=locations)

@features_bp.route('/delete_delivery/<int:did>')
def delete_delivery(did):
    if session.get('role') == 'admin':
        loc = db.session.query(DeliveryLocation).filter_by(id = did).first()

        if loc:
            db.session.delete(loc)
            db.session.commit()
            flash(f'✅ Delivery location {loc.pincode} deleted successfully!', 'success')
        
        else:
            flash(f'❌ Delivery location with ID {did} not found.', 'danger')

    else:
        flash('Access denied. Admins only.', 'danger')

    return redirect(url_for('features.manage_delivery'))