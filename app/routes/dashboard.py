from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, session
from sqlalchemy import func
from app import db
from app.models import Transaction, Expense, Grocery, StockReport
from app.routes.admin_access import LOW_STOCK_THRESHOLD

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login.login'))

    today_sales = 0
    gross_revenue = 0
    gross_profit = 0
    inventory_expense = 0
    operational_expense = 0
    net_profit = 0
    low_stock = 0
    total_products = 0
    sales_dates = []
    sales_values = []

    if session.get('role') == 'admin':

        today_sales = db.session.query(
            func.sum(Transaction.total)
        ).filter(
            func.date(Transaction.created_at) == func.date('now')
        ).scalar() or 0

        gross_revenue = db.session.query(
            func.sum(Transaction.total)
        ).scalar() or 0

        gross_profit = db.session.query(
            func.sum(
                StockReport.quantity *
                (StockReport.selling_price - StockReport.purchasing_price)
            )
        ).scalar() or 0

        inventory_expense = db.session.query(
            func.sum(Expense.amount)
        ).filter(
            Expense.expense_type == 'purchase'
        ).scalar() or 0

        operational_expense = db.session.query(
            func.sum(Expense.amount)
        ).filter(
            Expense.expense_type == 'operational'
        ).scalar() or 0

        net_profit = gross_profit - operational_expense

        low_stock = db.session.query(
            func.count(Grocery.id)
        ).filter(
            Grocery.stock <= LOW_STOCK_THRESHOLD
        ).scalar() or 0

        total_products = db.session.query(
            func.count(Grocery.id)
        ).scalar() or 0

        dates_map = {}
        for i in range(6, -1, -1):
            date_str = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            dates_map[date_str] = 0

        weekly_data = db.session.query(
            func.date(Transaction.created_at).label('sale_date'),
            func.sum(Transaction.total)
        ).filter(
            Transaction.created_at >= (datetime.now() - timedelta(days=6))
        ).group_by(
            func.date(Transaction.created_at)
        ).all()

        for date_val, total_val in weekly_data:
            date_key = str(date_val)
            if date_key in dates_map:
                dates_map[date_key] = float(total_val)

        sales_dates = list(dates_map.keys())
        sales_values = list(dates_map.values())

    return render_template(
        'dashboard.html',
        today_sales=today_sales,
        gross_revenue=gross_revenue,
        gross_profit=gross_profit,
        inventory_expense=inventory_expense,
        operational_expense=operational_expense,
        net_profit=net_profit,
        low_stock=low_stock,
        total_products=total_products,
        sales_dates=sales_dates,
        sales_values=sales_values
    )

@dashboard_bp.route('/')
def home():
    return redirect(url_for("dashboard.dashboard")) if 'username' in session else redirect(url_for("login.login"))