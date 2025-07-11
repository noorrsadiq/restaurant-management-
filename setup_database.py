import sqlite3
import hashlib
from datetime import datetime

def setup_database():
    """Initialize the restaurant database with tables and sample data"""
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()

    # Enable foreign key constraint support
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create menu items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            image_url TEXT,
            available INTEGER DEFAULT 1
        )
    ''')
    
    # Create orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create order items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            menu_item_id INTEGER,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (menu_item_id) REFERENCES menu_items (id)
        )
    ''')
    
    # Sample menu items with 'available' field included
    sample_items = [
        ("Margherita Pizza", "Classic pizza with tomato sauce, mozzarella, and fresh basil", 1400, "Pizza", "/placeholder.svg?height=200&width=300", 1),
        ("Pepperoni Pizza", "Traditional pizza with pepperoni and mozzarella cheese", 4060, "Pizza", "/placeholder.svg?height=200&width=300", 1),
        ("Caesar Salad", "Fresh romaine lettuce with Caesar dressing and croutons", 1120, "Salads", "/placeholder.svg?height=200&width=300", 1),
        ("Grilled Chicken Burger", "Juicy grilled chicken with lettuce, tomato, and mayo", 840, "Burgers", "/placeholder.svg?height=200&width=300", 1),
        ("Beef Burger", "Classic beef burger with cheese, lettuce, and tomato", 500, "Burgers", "/placeholder.svg?height=200&width=300", 1),
        ("Spaghetti Carbonara", "Creamy pasta with bacon, eggs, and parmesan cheese", 1500, "Pasta", "/placeholder.svg?height=200&width=300", 1),
        ("Fish and Chips", "Crispy battered fish with golden fries", 700, "Main Course", "/placeholder.svg?height=200&width=300", 1),
        ("Chocolate Cake", "Rich chocolate cake with chocolate frosting", 560, "Desserts", "/placeholder.svg?height=200&width=300", 1),
        ("Tiramisu", "Classic Italian dessert with coffee and mascarpone", 650, "Desserts", "/placeholder.svg?height=200&width=300", 1),
        ("Fresh Orange Juice", "Freshly squeezed orange juice", 930, "Beverages", "/placeholder.svg?height=200&width=300", 1),
        ("Coffee", "Premium roasted coffee", 700, "Beverages", "/placeholder.svg?height=200&width=300", 1),
        ("Iced Tea", "Refreshing iced tea with lemon", 420, "Beverages", "/placeholder.svg?height=200&width=300", 1)
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO menu_items (name, description, price, category, image_url, available)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', sample_items)
    
    conn.commit()
    conn.close()
    print("✅ Database setup completed successfully!")

if __name__ == "__main__":
    setup_database()
