from flask import render_template, url_for, flash, redirect, request, abort
from app import app, db, bcrypt, mail
from app.forms import RegistrationForm, LoginForm, CustomerForm, ProductForm, OrderForm
from app.models import User, Customer, Product, Order, OrderItem
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

def send_order_confirmation(order):
    msg = Message('Order Confirmation', sender='noreply@example.com', recipients=[order.customer.email])
    msg.body = f"Your order {order.id} has been received and is being processed."
    mail.send(msg)

@app.route("/")
@app.route("/home")
def home():
    return render_template('index.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/dashboard")
@login_required
def dashboard():
    customers = Customer.query.filter_by(author=current_user)
    return render_template('dashboard.html', title='Dashboard', customers=customers)

@app.route("/customer/new", methods=['GET', 'POST'])
@login_required
def new_customer():
    form = CustomerForm()
    if form.validate_on_submit():
        customer = Customer(name=form.name.data, email=form.email.data, phone=form.phone.data, address=form.address.data, author=current_user)
        db.session.add(customer)
        db.session.commit()
        flash('Customer has been added!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_customer.html', title='New Customer', form=form)

@app.route("/customer/<int:customer_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    if customer.author != current_user:
        abort(403)
    form = CustomerForm()
    if form.validate_on_submit():
        customer.name = form.name.data
        customer.email = form.email.data
        customer.phone = form.phone.data
        customer.address = form.address.data
        db.session.commit()
        flash('Customer has been updated!', 'success')
        return redirect(url_for('dashboard'))
    elif request.method == 'GET':
        form.name.data = customer.name
        form.email.data = customer.email
        form.phone.data = customer.phone
        form.address.data = customer.address
    return render_template('edit_customer.html', title='Edit Customer', form=form)

@app.route("/products")
@login_required
def products():
    products = Product.query.all()
    return render_template('products.html', title='Products', products=products)

@app.route("/product/new", methods=['GET', 'POST'])
@login_required
def new_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(name=form.name.data, description=form.description.data, price=form.price.data, stock=form.stock.data, category=form.category.data)
        db.session.add(product)
        db.session.commit()
        flash('Product has been added!', 'success')
        return redirect(url_for('products'))
    return render_template('add_product.html', title='New Product', form=form)

@app.route("/product/<int:product_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm()
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.category = form.category.data
        db.session.commit()
        flash('Product has been updated!', 'success')
        return redirect(url_for('products'))
    elif request.method == 'GET':
        form.name.data = product.name
        form.description.data = product.description
        form.price.data = product.price
        form.stock.data = product.stock
        form.category.data = product.category
    return render_template('edit_product.html', title='Edit Product', form=form)

@app.route("/sales_report")
@login_required
def sales_report():
    # Logic to generate sales report
    return render_template('sales_report.html', title='Sales Report')

@app.route("/orders")
@login_required
def orders():
    orders = Order.query.all()
    return render_template('orders.html', title='Orders', orders=orders)

@app.route("/order/new", methods=['GET', 'POST'])
@login_required
def new_order():
    form = OrderForm()
    if form.validate_on_submit():
        order = Order(customer_id=form.customer.data, user_id=current_user.id)
        db.session.add(order)
        db.session.commit()
        send_order_confirmation(order)
        flash('Order has been placed!', 'success')
        return redirect(url_for('orders'))
    return render_template('add_order.html', title='New Order', form=form)

@app.route("/order/<int:order_id>")
@login_required
def order(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('order.html', title='Order Details', order=order)
