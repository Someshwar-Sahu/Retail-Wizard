import re
import bcrypt
from functools import wraps
from flask import redirect, session, url_for
from app import db
from app.models import Login
from flask import Blueprint, redirect, url_for, flash, request, session
from app.models import Coupon

auth_bp = Blueprint('auth', __name__)

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session:
                return redirect(url_for('login.login'))

            if session.get('role') != required_role:
                flash("Access denied!")
                return redirect(url_for('dashboard.dashboard'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def is_strong_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"\d",password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

def store_user(fullname, username, password, role="cashier", is_approved=False):

    exsisting_user_count = Login.query.count() 

    if exsisting_user_count == 0:
        role = "admin"
        is_approved = True

    if not is_strong_password(password):
        return False, "❌ Password must be at least 8 characters, contain 1 number and 1 symbol."

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds= 14))

    try:
        new_user = Login(
            full_name=fullname,
            username=username,
            password=hashed,
            role=role,
            is_approved=is_approved
        )

        db.session.add(new_user)
        db.session.commit()

        msg = f"✅ User {username} created successfully." if is_approved else f"⏳ Account created for {username}. Please wait for admin approval."
        return True, msg
    
    except Exception as e:
        db.session.rollback()
        print(f"\n🚨 REAL DATABASE ERROR: {str(e)}\n") 
        return False, f"Database Error: Check your terminal!"
    
def verify_user(username, password):

    user = Login.query.filter_by(username=username).first()

    if user and bcrypt.checkpw(password.encode(), user.password):
        return True
    
    return False

def reset_password(username, new_password):

    user = Login.query.filter_by(username=username).first()

    if not user:
        return False
    
    if not is_strong_password(new_password):
        return False

    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt(rounds=14))

    user.password = hashed
    db.session.commit()

    return True

@auth_bp.route("/api/validate_coupon", methods=["POST"])
def validate_coupon():
    data = request.json
    code = data.get('code','').strip().upper()
    cart_total = float(data.get('total',0))

    coupon = Coupon.query.filter_by(code=code).first()

    if not coupon:
        return {"valid": False, "message": "❌ Invalid coupon code."}

    if coupon.usage_limit >= 0 and coupon.used_count >= coupon.usage_limit:
        return {"valid": False, "message": "⚠️ Coupon usage limit reached."}

    disc_type = coupon.discount_type
    disc_value = coupon.discount_value
    discount_amount = 0

    if disc_type == "percent":
        discount_amount = (cart_total * disc_value) / 100
    else:
        discount_amount = disc_value

    if discount_amount > cart_total:
        discount_amount = cart_total

    new_total = cart_total - discount_amount

    return {
        'valid': True,
        'discount_amount': round(discount_amount, 2),
        'new_total': round(new_total, 2),
        'message': f"✅ Coupon applied! You saved Rs. {discount_amount:.2f}."
    }
