from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from app import db
from app.models import Grocery

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/add-to-cart', methods=['POST'])
def add_to_cart():

    pid = int(request.form.get('product_id'))
    qty_to_add = int(request.form.get('quantity') or 0)

    if qty_to_add <= 0:
        flash("Invalid quantity.")
        return redirect(url_for('products.products'))

    product = Grocery.query.filter_by(id= pid, is_active = True).first()

    if not product:
        flash('Product not found')
        return redirect(url_for('products.products'))

    cart = session.get('cart', {})

    pid_str = str(pid)

    current_in_cart = cart.get(pid_str, {}).get('quantity', 0)
    total_requested = current_in_cart + qty_to_add

    if total_requested > product.stock:
        flash(f'Only {product.stock} units available. You already have {current_in_cart} in cart.')
        return redirect(url_for('products.products'))

    if pid_str in cart:
        cart[pid_str]['quantity'] = total_requested
    else:
        cart[pid_str] = {
            'id': product.id,
            'name': product.name,
            'price': float(product.selling_price),
            'quantity': qty_to_add
        }

    session['cart'] = cart

    session.modified = True

    flash(f'Added {qty_to_add} {product.name} to cart.')
    return redirect(url_for('products.products'))

@cart_bp.route('/cart')
def view_cart():

    cart = session.get('cart', {})
    total = sum(i['price'] * i['quantity'] for i in cart.values())

    return render_template('cart.html', cart=cart, total=total)

@cart_bp.route('/remove-from-cart/<pid>')
def remove_from_cart(pid):

    cart = session.get('cart', {})
    cart.pop(str(pid), None)

    session['cart'] = cart

    return redirect(url_for('cart.view_cart'))
