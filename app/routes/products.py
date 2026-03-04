from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from app import db
from app.models import Grocery, Expense
import pandas as pd
from sqlalchemy import or_
from app.routes.admin_access import LOW_STOCK_THRESHOLD
import re

products_bp = Blueprint('products', __name__)

def delete_product(pid):
    product = db.session.get(Grocery, pid)
    if product:
        db.session.delete(product)
        db.session.commit()

def add_stock_expense_with_cursor(product_name, quantity, price, action = 'Stock Purchase', expense_type = 'purchase'):
    total_cost = quantity*price
    title = f'{action} - {product_name}'
    note = f'{quantity} units @ ₹{price} each'
    transaction = Expense(title=title, amount=total_cost, note=note, expense_type=expense_type)
    db.session.add(transaction) 

@products_bp.route('/products',methods=['GET','POST'])
def products():
    if 'username' not in session:
        return redirect(url_for('login.login'))

    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        purchasing_price = float(request.form.get('purchasing_price'))
        selling_price = float(request.form.get('selling_price'))
        quantity = int(request.form.get('quantity'))

        existing_product = Grocery.query.filter_by(name = name).first()

        if existing_product:

            existing_product.purchasing_price = purchasing_price
            existing_product.selling_price = selling_price

            existing_product.stock += quantity
            existing_product.quantity += quantity

            add_stock_expense_with_cursor(name,quantity=quantity,price=purchasing_price, action='Restock', expense_type='purchase')

        else:
            new_product = Grocery(name=name,category=category,purchasing_price=purchasing_price,selling_price=selling_price,quantity=quantity,stock=quantity)

            add_stock_expense_with_cursor(name,quantity=quantity,price=purchasing_price, action='Stock Purchase', expense_type='purchase')

            db.session.add(new_product)

        db.session.commit()

        return redirect(url_for('products.products'))
    
    search_query = request.args.get('q','').strip()
    if search_query:
        like_query = f'%{search_query}%'
        products = db.session.query(Grocery)\
                            .filter(
                                Grocery.is_active == True,
                                or_(Grocery.name.ilike(like_query),
                                    Grocery.category.ilike(like_query))
                            )\
                            .order_by(Grocery.stock.asc()).all()
    else:
        products = db.session.query(Grocery).filter(Grocery.is_active == True).order_by(Grocery.name).all()

    low_stock_products = db.session.query(Grocery).filter(Grocery.stock <= LOW_STOCK_THRESHOLD).all()

    return render_template('products.html', products=products,
                           low_stock_products = low_stock_products,
                            low_stock_threshold = LOW_STOCK_THRESHOLD,
                            search_query = search_query)

def clean_number(value):
    if isinstance(value, (int,float)):
        return value
    numbers = re.findall(r'[\d\.]+',str(value))
    if numbers:
        return float(numbers[0])
    return 0

@products_bp.route('/import-products',methods=['POST'])
def import_products():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('products.products'))

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('products.products'))
    
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
        
        else:
            flash('Invalid file format')
            return redirect(url_for('products.products'))

        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(r"[^\w]", "_", regex=True)   
            .str.replace(r"_+", "_", regex=True)      
            .str.strip("_")
        )

        COLUMN_ALIASES = {
            "name": ["product_name", "name", "item", "title"],
            "category": ["category", "department"],
            "purchasing_price": ["purchasing_price", "price", "cost", "purchase_price"],
            "selling_price": ["selling_price", "final_price", "mrp", "sale_price"],
            "quantity": ["quantity", "stock", "stock_available", "qty"]
        }

        mapped_columns = {}

        for db_col, aliases in COLUMN_ALIASES.items():
            for alias in aliases:
                if alias in df.columns:
                    mapped_columns[alias] = db_col
                    break

        df.rename(columns=mapped_columns, inplace=True)

        for _, row in df.iterrows():

            def get_val(key,default = 0):
                val = row.get(key)
                if pd.isna(val):
                    return default
                return val
            
            name = str(get_val('name', 'Unknown')).strip()
            category = str(get_val('category', 'General')).strip()

            qty = int(clean_number(get_val('quantity', 0)))
            purchasing_price = float(clean_number(get_val('purchasing_price', 0)))
            selling_price = float(clean_number(get_val('selling_price', 0)))

            existing_product = Grocery.query.filter_by(name=name).first()

            if existing_product:

                existing_product.purchasing_price = purchasing_price
                existing_product.selling_price = selling_price

                existing_product.stock += qty
                existing_product.quantity += qty
            else:
                
                new_product = Grocery(
                    name=name,
                    category=category,
                    purchasing_price=purchasing_price,
                    selling_price=selling_price,
                    quantity=qty,
                    stock=qty
                )
                
                db.session.add(new_product)
        
        db.session.commit()

        flash('Products imported successfully')

        
    except Exception as e:
        flash(f'Error: {str(e)}')
        print(f'Import Error: {str(e)}')

    return redirect(url_for('products.products'))

@products_bp.route('/edit-product/<int:pid>',methods=['GET','POST'])
def edit_product(pid):
    if 'username' not in session:
        return redirect(url_for('login.login'))
    
    product = db.session.get(Grocery, pid)

    if not product or not product.is_active:
        return 'Product not available', 404
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.category = request.form.get('category')

        new_purchasing_price = float(request.form.get('purchasing_price'))
        new_selling_price = float(request.form.get('selling_price'))
        added_qty = int(request.form.get('added_quantity', 0))

        product.selling_price = new_selling_price

        if added_qty > 0:
            
            product.purchasing_price = new_purchasing_price

            product.quantity += added_qty
            product.stock += added_qty

            add_stock_expense_with_cursor(
                product.name,
                added_qty,
                new_purchasing_price,
                action='Restock',
                expense_type='purchase'
            )
        else:
            pass

        db.session.commit()
        return redirect(url_for('products.products'))
    
    return render_template('edit_product.html',product=product)

@products_bp.route("/delete-product/<int:pid>")
def delete_product_route(pid):
    if 'username' not in session:
        return redirect(url_for('login.login'))

    product = db.session.get(Grocery, pid)

    if not product:
        flash("Product not found.")
        return redirect(url_for("products.products"))

    product.is_active = False
    db.session.commit()

    flash("Product removed from active list.")
    return redirect(url_for("products.products"))