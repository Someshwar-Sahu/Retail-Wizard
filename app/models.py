from app import db
from sqlalchemy import CheckConstraint

class Login(db.Model):
    __tablename__ = 'login'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), nullable=False, unique=True, index=True)
    password = db.Column(db.LargeBinary, nullable=False)
    role = db.Column(db.String(20), default='cashier')
    is_approved = db.Column(db.Boolean, default=False)

class Shifts(db.Model):
    __tablename__ = 'shifts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), nullable=False)
    cashier = db.Column(db.String(80), nullable=False)
    start_time = db.Column(db.DateTime, default=db.func.current_timestamp())
    end_time = db.Column(db.DateTime, default=None)

class Grocery(db.Model):
    __tablename__ = 'grocery'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(200))
    purchasing_price = db.Column(db.Float, nullable = False)
    selling_price = db.Column(db.Float, nullable = False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    stock = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, default=True)

class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_name = db.Column(db.String(200), nullable=False)
    total = db.Column(db.Float, nullable=False)
    payment_mode = db.Column(db.String(200), nullable=False)
    amount_received = db.Column(db.Float, nullable=False)
    change_returned = db.Column(db.Float, nullable=False)
    card_last4 = db.Column(db.String(4), nullable=False)
    cashier = db.Column(db.String(200), nullable=False)
    discount_applied = db.Column(db.Float, nullable=False)
    coupon_code = db.Column(db.String(200), nullable=True)

    delivery_pincode = db.Column(db.String(10), nullable=True)
    delivery_address = db.Column(db.String(500), nullable=True)
    delivery_fee = db.Column(db.Float, nullable=True, default=0.0)

    stock_items = db.relationship('StockReport', backref='transaction', lazy=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    shift_id = db.Column(db.Integer, db.ForeignKey('shifts.id'), nullable=True)

class StockReport(db.Model):
    __tablename__ = 'stock_report'
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey("grocery.id"), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    change = db.Column(db.Integer, nullable=False)
    purchasing_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey("transaction.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)   
    note = db.Column(db.String(500), nullable=True)
    expense_type = db.Column(db.String(100), nullable=True, default='purchase')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Coupon(db.Model):
    __tablename__ = 'coupons'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(10), nullable=False, unique=True)
    discount_type = db.Column(db.String(10), nullable=False)
    discount_value = db.Column(db.Float, nullable=False)
    usage_limit = db.Column(db.Integer, nullable=False, default=1)
    used_count = db.Column(db.Integer, nullable=False, default=0)
    __table_args__ = (
        CheckConstraint(discount_type.in_(['percent', 'flat']), name='valid_type'),
    )

class DeliveryLocation(db.Model):
    __tablename__ = 'delivery_locations'
    id = db.Column(db.Integer, primary_key  = True, autoincrement=True)
    pincode = db.Column(db.String(10), nullable = False, unique = True)
    delivery_fee = db.Column(db.Float, nullable = False, default = 0.0) 