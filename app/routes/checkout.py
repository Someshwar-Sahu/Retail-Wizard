from flask import Blueprint, render_template, redirect, url_for, flash, request, session, abort
from app import db
from app.models import Coupon, Grocery, Transaction, StockReport, DeliveryLocation
from app.routes.invoice_utils import generate_invoice_pdf

checkout_bp = Blueprint('checkout', __name__)

@checkout_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'cart' not in session or not session['cart']:
        flash('Cart is empty.')
        return redirect(url_for('cart.view_cart'))

    cart = session['cart']

    subtotal = 0
    for pid, item in cart.items():
        product = Grocery.query.filter_by(id=pid, is_active=True).first()

        if not product:
            flash(f"Product with id {pid} not found.")
            return redirect(url_for('checkout.checkout'))
        subtotal += product.selling_price * item['quantity']

    delivery_locations = db.session.query(DeliveryLocation).all()

    if request.method == 'GET':
        return render_template('checkout.html', cart=cart, total=subtotal, delivery_locations=delivery_locations)

    try:
        customer = request.form['customer'].strip()
        payment = request.form['payment']

        if not customer:
            flash("Customer name required.")
            return redirect(url_for('checkout.checkout'))

        discount_applied = 0.0
        coupon_code = request.form.get('coupon_code', '').strip().upper()
        coupon = None

        if coupon_code:
            coupon = db.session.query(Coupon).filter_by(code=coupon_code).first()

            if not coupon:
                flash("Invalid coupon code.")
                return redirect(url_for('checkout.checkout'))

            if coupon.usage_limit is not None and coupon.used_count >= coupon.usage_limit:
                flash("Coupon usage limit reached.")
                return redirect(url_for('checkout.checkout'))

            if coupon.discount_type == "percent":
                discount_applied = (subtotal * coupon.discount_value) / 100
            elif coupon.discount_type == "flat":
                discount_applied = coupon.discount_value

            discount_applied = min(discount_applied, subtotal)

        delivery_pincode = request.form.get('delivery_pincode', '')
        delivery_address = request.form.get('delivery_address', '').strip()
        delivery_fee = 0.0

        if delivery_pincode:
            loc = db.session.query(DeliveryLocation).filter_by(pincode=delivery_pincode).first()
            if loc:
                delivery_fee = loc.delivery_fee
                if not delivery_address:
                    flash("Delivery address is required for delivery orders.")
                    return redirect(url_for('checkout.checkout'))
            else:
                delivery_pincode = None 

        final_total = max(subtotal - discount_applied, 0) + delivery_fee

        amount_received = 0.0
        change_returned = 0.0
        card_last4 = "0000"   

        if payment == 'Cash':
            amount_received = float(request.form.get('amount_received', 0))

            if amount_received < final_total:
                flash(f'Insufficient cash! Bill is ₹{final_total}.')
                return redirect(url_for('checkout.checkout'))

            change_returned = amount_received - final_total

        elif payment == 'Card':
            card = request.form.get('card_number', '').strip()

            if len(card) < 4 or not card.isdigit():
                flash('Invalid card number.')
                return redirect(url_for('checkout.checkout'))

            card_last4 = card[-4:]
            amount_received = final_total

        elif payment == 'UPI':
            amount_received = final_total

        else:
            flash("Invalid payment method.")
            return redirect(url_for('checkout.checkout'))

        for pid, item in cart.items():
            product = Grocery.query.filter_by(id=pid, is_active=True).first()

            if not product:
                raise Exception(f"Product '{item['name']}' not available.")

            if product.stock < item['quantity']:
                raise Exception(
                    f"Stock Error: Only {product.stock} units available for '{item['name']}'."
                )

        transaction = Transaction(
            customer_name=customer,
            total=final_total,
            payment_mode=payment,
            amount_received=amount_received,
            change_returned=change_returned,
            card_last4=card_last4,
            cashier=session['username'],
            shift_id=session.get('shift_id'),
            discount_applied=discount_applied,
            coupon_code=coupon_code if coupon else None,
            delivery_pincode=delivery_pincode,
            delivery_address=delivery_address if delivery_pincode else None,
            delivery_fee=delivery_fee
        )

        db.session.add(transaction)
        db.session.flush()  

        for pid, item in cart.items():
            product = Grocery.query.get(pid)
            product.stock -= item['quantity']

            stock_entry = StockReport(
                product_id=product.id,
                product_name=product.name,
                quantity=item['quantity'],
                change=-item['quantity'],
                purchasing_price=product.purchasing_price,
                selling_price=product.selling_price,
                transaction_id=transaction.id
            )
            db.session.add(stock_entry)

        if coupon:
            coupon.used_count += 1

        db.session.commit()
        session.pop('cart', None)

        flash('Order placed successfully! 🖨️ Printing Invoice...')
        return redirect(url_for('checkout.invoice', tid=transaction.id))

    except Exception as e:
        db.session.rollback()
        flash(f'Transaction Failed: {str(e)}')
        print(f'Checkout Error: {e}')
        return redirect(url_for('checkout.checkout'))

@checkout_bp.route('/invoice/<int:tid>')
def invoice(tid):
    if 'username' not in session:
        return redirect(url_for('login.login'))
    
    transaction = db.session.get(Transaction, tid) or abort(404)

    if not transaction:
        return 'Transaction not found', 404
    
    if session.get('role') != 'admin' and transaction.cashier != session['username']:
        return 'Unauthorized access to invoice', 403
    
    pdf_path, qr_path = generate_invoice_pdf(
        invoice_id=tid, 
        customer=transaction.customer_name,
        payment=transaction.payment_mode, 
        items=[(item.product_name, item.quantity, item.selling_price) for item in transaction.stock_items], 
        total=transaction.total, 
        amount_received=transaction.amount_received, 
        change_returned=transaction.change_returned, 
        card_last4=transaction.card_last4,
        delivery_pincode=transaction.delivery_pincode,
        delivery_address=transaction.delivery_address,
        delivery_fee=transaction.delivery_fee
    )

    return render_template(
        "invoice.html",
        transaction=transaction,
        stock_items=transaction.stock_items,
        total=transaction.total,
        pdf_path=pdf_path,
        qr_path=qr_path
    )