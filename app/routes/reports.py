from flask import Blueprint, render_template, redirect, url_for, request, session
from app import db
from app.models import Grocery, Transaction, Expense, StockReport

reports_bp = Blueprint('reports',__name__)

@reports_bp.route('/reports')
def reports():
    if 'username' not in session:
        return redirect(url_for('login.login'))
    return render_template('reports.html')

@reports_bp.route('/reports/sales')
def stock_report():
    if 'username' not in session:
        return redirect(url_for('login.login'))

    data = db.session.query(Grocery.id, Grocery.category, Grocery.name,
                            Grocery.stock, Grocery.purchasing_price, Grocery.selling_price,
                            (Grocery.selling_price - Grocery.purchasing_price).label('profit_per_unit')
                            ).order_by(Grocery.stock.asc()).all()

    return render_template('report_stock.html',data = data)

@reports_bp.route('/reports/profit')
def profit_report():
    if 'username' not in session:
        return redirect(url_for('login.login'))
    
    if session.get('role') != 'admin':
        return "Unauthorized access", 403
    
    data = db.session.query(StockReport.product_name,
                            db.func.sum(StockReport.quantity).label('sold'),
                            db.func.sum(StockReport.quantity * StockReport.selling_price).label('total_sales'),
                            db.func.sum(StockReport.quantity * StockReport.purchasing_price).label('cost'),
                            db.func.sum(StockReport.quantity * (StockReport.selling_price - StockReport.purchasing_price)).label('profit')
                            ).group_by(StockReport.product_name).all()

    return render_template('report_profit.html',data = data)

@reports_bp.route('/reports/transactions')
def transaction_report():
    if 'username' not in session:
        return redirect(url_for('login.login'))
    
    data = db.session.query(Transaction.id,
                            Transaction.customer_name,
                            Transaction.total,
                            Transaction.payment_mode,
                            Transaction.created_at).order_by(Transaction.created_at.desc()).all()

    return render_template('report_transactions.html',data = data)

@reports_bp.route('/reports/items')
def item_sales_report():
    if 'username' not in session:
        return redirect(url_for('login.login'))
    
    data = db.session.query(StockReport.product_name,
                            db.func.sum(StockReport.quantity).label('total_quantity'),
                            db.func.sum(StockReport.quantity * StockReport.selling_price).label('total_sales')
                            ).group_by(StockReport.product_name).order_by(db.func.sum(StockReport.quantity).desc()).all()
    
    return render_template('report_items.html',data = data)

def add_expense(title, amount, note):
    expenses = Expense(title= title, amount=amount, note=note, expense_type = 'operational')
    db.session.add(expenses)
    db.session.commit()

def get_all_expenses():
    return db.session.query(Expense).order_by(Expense.created_at.desc()).all() 

@reports_bp.route('/expenses', methods = ['GET', 'POST'])
def expenses():
    if 'username' not in session:
        return redirect(url_for('login.login'))
    
    if session.get('role') != 'admin':
        return "Unauthorized access", 403
    
    if request.method == 'POST':
        add_expense(request.form['title'],
                    float(request.form['amount']),
                    request.form['note'])

        return redirect(url_for('reports.expenses'))
    
    return render_template('expenses.html', expenses = get_all_expenses())