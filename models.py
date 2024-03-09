import sqlite3
from datetime import datetime

def get_db_connection():
    db = 'cafeteriaOrder.db'
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = [
        '''
        CREATE TABLE users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(50) NOT NULL,
        password VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL,
        campus TEXT CHECK (campus IN ('campus a', 'campus b')) NOT NULL
        );
        ''',
        '''
        CREATE TABLE cafes (
            cafe_id INTEGER PRIMARY KEY,
            cafe_name VARCHAR(100) NOT NULL,
            location VARCHAR(255) NOT NULL
        );
        '''  ,   
        '''
        CREATE TABLE menu_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name VARCHAR(100) NOT NULL,
            description TEXT,
            diet_info TEXT CHECK (diet_info IN ('veg', 'non-veg', 'gluten-free')) NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            item_count INTEGER NOT NULL,
            cafe_id INTEGER,
            FOREIGN KEY (cafe_id) REFERENCES cafes(cafe_id)
        );
        ''',
        '''
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT CHECK (status IN ('placed', 'preparing', 'ready', 'picked', 'completed')) NOT NULL,
            order_location TEXT CHECK (order_location IN ('dine in cafeteria', 'take out')) NOT NULL,
            total_amt DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        );
        ''',
        '''
        CREATE TABLE order_items (
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            item_id INTEGER,
            quantity INT NOT NULL,
            sub_total DECIMAL(10, 2) NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (item_id) REFERENCES menu_items(item_id)
        );
        ''',
        '''
        CREATE TABLE pickup_notifications (
            notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            pickup_time TIMESTAMP,
            notification_status TEXT CHECK (notification_status IN ('pending', 'sent', 'completed')) NOT NULL,
            pickup_instruction VARCHAR(255) NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        );
        ''',
        '''
        CREATE TABLE order_tracking (
            tracking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            status TEXT CHECK (status IN ('placed', 'preparing', 'ready', 'picked', 'completed')) NOT NULL,
            status_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        );
        '''
    ]
    try:
        for sql_stmt in sql:
            cursor.execute(sql_stmt)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()

def get_user_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    conn.close()
    return user

def insert_user(username, password, email, campus):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password, email, campus) VALUES (?, ?, ?, ?)",
            (username, password, email, campus)
        )
        conn.commit()
        print("User registered successfully!")
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()

def get_all_menu_items():
    conn = get_db_connection() 
    cursor = conn.cursor()
    menu_items = None
    try:
        cursor.execute("SELECT * FROM menu_items")
        menu_items = cursor.fetchall()
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()
    return menu_items

def get_all_cafes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cafes = None
    try:
        cursor.execute("SELECT * FROM cafes")
        cafes = cursor.fetchall()
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()
    return cafes
    
def get_menu_items_by_cafe(cafe_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    menu_items = None
    try:
        cursor.execute("SELECT * FROM menu_items WHERE cafe_id = ?", (cafe_id,))
        menu_items = cursor.fetchall()
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()
    return menu_items

def get_menu_item_by_id(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM menu_items WHERE item_id = ?", (item_id,))
        menu_item = cursor.fetchone()
        return menu_item
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return None
    finally:
        conn.close()

def insert_order(user_id, order_location, total_amount):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO orders (user_id, order_location, total_amt, status)
            VALUES (?, ?, ?, 'placed')
        """, (user_id, order_location, total_amount))
        conn.commit()

        # Return the order ID of the newly inserted order
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return None
    finally:
        conn.close()

def insert_order_item(order_id, item_id, quantity, sub_total):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO order_items (order_id, item_id, quantity, sub_total)
            VALUES (?, ?, ?, ?)
        """, (order_id, item_id, quantity, sub_total))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()

def insert_pickup_notification(order_id, pickup_time, notification_status, pickup_instruction):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO pickup_notifications (order_id, pickup_time, notification_status, pickup_instruction)
            VALUES (?, ?, ?, ?)
        """, (order_id, pickup_time, notification_status, pickup_instruction))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()

def insert_order_tracking(order_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO order_tracking (order_id, status)
            VALUES (?, ?)
        """, (order_id, status))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()

def get_pickup_notifications():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM pickup_notifications")
        pickup_notifications = cursor.fetchall()
        return pickup_notifications
    except sqlite3.Error as e:
        print(f"Error fetching pickup notifications: {e}")
    finally:
        conn.close()

def get_order_tracking():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM order_tracking")
        order_tracking = cursor.fetchall()
        return order_tracking
    except sqlite3.Error as e:
        print(f"Error fetching order tracking data: {e}")
    finally:
        conn.close()

def get_order_tracking_by_order_id(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM order_tracking WHERE order_id = ?", (order_id,))
        order_tracking_data = cursor.fetchall()
        return order_tracking_data
    except sqlite3.Error as e:
        print(f"Error fetching order tracking data: {e}")
    finally:
        conn.close()