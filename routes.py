from flask import request, flash, redirect, url_for, session, render_template
from models import *

def setupRoutes(app):
    def login_required(func):
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                flash('You need to log in to place an order.', 'error')
                return redirect(url_for('login'))
            return func(*args, **kwargs)
        return wrapper

    @app.route('/')
    def index():
        return "Welcome to cafeteria"
    
    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            campus = request.form['campus']

            if get_user_by_username(username):
                flash('Username already exists. Please choose another.', 'error')
            else:
                insert_user(username, password, email, campus)
                flash('Signup successful! You can now login.', 'success')
                return redirect(url_for('login'))

        #return "Signup successful"
        return render_template("signup.html") 
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            user = get_user_by_username(username)

            if user and user['password'] == password:
                session['user_id'] = user['user_id']
                session['username'] = user['username']

                flash('Login successful!', 'success')
                return redirect(url_for('index')) 
            flash('Invalid username or password. Please try again.', 'error')

        return render_template("login.html")
    
    @app.route('/menu_browsing', methods=['GET', 'POST'])
    def menu_browsing():
        if request.method == 'POST':
            cafe_id = request.form.get('cafe_id')
            menu_items = get_menu_items_by_cafe(cafe_id)
        else:
            menu_items = get_all_menu_items()

        cafes = get_all_cafes()  # Assuming you have a function to retrieve all cafes
        return render_template('menu_browsing.html', menu_items=menu_items, cafes=cafes)
    
    @app.route('/place_order', methods=['POST'])
    def place_order():
        try:
            user_id = session.get('user_id')  # Retrieve user_id from the session
            if not user_id:
                flash('User not logged in. Please login first.', 'error')
                return redirect(url_for('login'))  # Redirect to login page if user is not logged in

            order_location = request.form['order_location']
            quantities = [int(quantity) for quantity in request.form.getlist('quantities[]')]
            menu_item_ids = [int(item_id) for item_id in request.form.getlist('menu_items[]')]

            # Validate order_location
            if order_location not in ['dine in cafeteria', 'take out']:
                raise ValueError('Invalid order location')

            # Validate quantities
            if any(q < 1 for q in quantities):
                raise ValueError('Invalid quantity')

            # Fetch menu item details and calculate subtotal for each item
            menu_items = [get_menu_item_by_id(item_id) for item_id in menu_item_ids]
            subtotals = [quantity * item['price'] for quantity, item in zip(quantities, menu_items)]

            # Calculate total amount
            total_amount = sum(subtotals)

            # Insert order into the database
            order_id = insert_order(user_id, order_location, total_amount)

            # Insert order items into the database
            for item_id, quantity, subtotal in zip(menu_item_ids, quantities, subtotals):
                insert_order_item(order_id, item_id, quantity, subtotal)

            flash('Order placed successfully!', 'success')
            return redirect(url_for('index'))  # Replace 'index' with your actual route

        except ValueError as e:
            flash(f'Error placing order: {str(e)}', 'error')
            return redirect(url_for('menu_browsing'))  # Redirect to the menu browsing page on error

    @app.route('/pickup_notification', methods=['POST'])
    def pickup_notification():
        if request.method == 'POST':
            order_id = request.form['order_id']
            pickup_time = request.form['pickup_time']
            notification_status = 'pending'  # You may adjust this based on your logic
            pickup_instruction = request.form['pickup_instruction']

            # Insert pickup notification
            insert_pickup_notification(order_id, pickup_time, notification_status, pickup_instruction)

            return "Pickup notification created successfully"

    # Route to handle order tracking
    @app.route('/order_tracking', methods=['POST'])
    def order_tracking():
        if request.method == 'POST':
            order_id = request.form['order_id']
            status = request.form['status']

            # Insert order tracking entry
            insert_order_tracking(order_id, status)

            return "Order tracking entry created successfully"
