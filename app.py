import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Restaurant Management System",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #ff6b6b, #ffa500);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    .menu-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .cart-item {
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
</style>
""", unsafe_allow_html=True)

# Database functions
def get_db_connection():
    conn = sqlite3.connect('restaurant.db')
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()    

def create_user(username, email, password):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        password_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    password_hash = hash_password(password)
    user = cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password_hash = ?",
        (username, password_hash)
    ).fetchone()
    conn.close()
    return dict(user) if user else None

def get_menu_items():
    conn = get_db_connection()
    items = conn.execute("SELECT * FROM menu_items WHERE available = TRUE").fetchall()
    conn.close()
    return [dict(item) for item in items]

def create_order(user_id, cart_items, total_amount):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create order
    cursor.execute(
        "INSERT INTO orders (user_id, total_amount) VALUES (?, ?)",
        (user_id, total_amount)
    )
    order_id = cursor.lastrowid
    
    # Add order items
    for item in cart_items:
        cursor.execute(
            "INSERT INTO order_items (order_id, menu_item_id, quantity, price) VALUES (?, ?, ?, ?)",
            (order_id, item['id'], item['quantity'], item['price'])
        )
    
    conn.commit()
    conn.close()
    return order_id

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'page' not in st.session_state:
    st.session_state.page = 'login'

# Header
st.markdown("""
<div class="main-header">
    <h1>🍽️ Restaurant Management System</h1>
    <p>Delicious food at your fingertips!</p>
</div>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.title("Navigation")
    
    if st.session_state.user:
        st.success(f"Welcome, {st.session_state.user['username']}!")
        
        if st.button("🍽️ Menu", use_container_width=True):
            st.session_state.page = 'menu'
        
        if st.button("🛒 Cart", use_container_width=True):
            st.session_state.page = 'cart'
        
        if st.button("💳 Checkout", use_container_width=True):
            st.session_state.page = 'checkout'
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.cart = []
            st.session_state.page = 'login'
            st.rerun()
    else:
        if st.button("🔐 Login", use_container_width=True):
            st.session_state.page = 'login'
        
        if st.button("📝 Sign Up", use_container_width=True):
            st.session_state.page = 'signup'

# Main content
if st.session_state.page == 'login':
    st.header("🔐 Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", use_container_width=True)
        
        if submit:
            if username and password:
                user = authenticate_user(username, password)
                if user:
                    st.session_state.user = user
                    st.session_state.page = 'menu'
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.error("Please fill in all fields")

elif st.session_state.page == 'signup':
    st.header("📝 Sign Up")
    
    with st.form("signup_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Sign Up", use_container_width=True)
        
        if submit:
            if username and email and password and confirm_password:
                if password == confirm_password:
                    if create_user(username, email, password):
                        st.success("Account created successfully! Please login.")
                        st.session_state.page = 'login'
                        st.rerun()
                    else:
                        st.error("Username or email already exists")
                else:
                    st.error("Passwords do not match")
            else:
                st.error("Please fill in all fields")

elif st.session_state.page == 'menu':
    st.header("🍽️ Our Menu")
    
    menu_items = get_menu_items()
    categories = list(set(item['category'] for item in menu_items))
    
    # Category filter
    selected_category = st.selectbox("Filter by category:", ["All"] + categories)
    
    if selected_category != "All":
        menu_items = [item for item in menu_items if item['category'] == selected_category]
    
    # Display menu items
    cols = st.columns(3)
    for idx, item in enumerate(menu_items):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="menu-card">
                <img src="{item['image_url']}" style="width: 100%; border-radius: 5px;">
                <h4>{item['name']}</h4>
                <p>{item['description']}</p>
                <h5>PKR {item['price']:.2f}</h5>
            </div>
            """, unsafe_allow_html=True)
            
            quantity = st.number_input(f"Quantity for {item['name']}", min_value=0, max_value=10, key=f"qty_{item['id']}")
            
            if st.button(f"Add to Cart", key=f"add_{item['id']}", use_container_width=True):
                if quantity > 0:
                    # Check if item already in cart
                    existing_item = next((cart_item for cart_item in st.session_state.cart if cart_item['id'] == item['id']), None)
                    if existing_item:
                        existing_item['quantity'] += quantity
                    else:
                        cart_item = dict(item)
                        cart_item['quantity'] = quantity
                        st.session_state.cart.append(cart_item)
                    st.success(f"Added {quantity} {item['name']} to cart!")
                    st.rerun()

elif st.session_state.page == 'cart':
    st.header("🛒 Your Cart")
    
    if not st.session_state.cart:
        st.info("Your cart is empty. Go to the menu to add items!")
    else:
        total = 0
        for idx, item in enumerate(st.session_state.cart):
            item_total = item['price'] * item['quantity']
            total += item_total
            
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.write(f"*{item['name']}*")
                st.write(f"PKR {item['price']:.2f} each")
            with col2:
                st.write(f"Qty: {item['quantity']}")
            with col3:
                st.write(f"PKR {item_total:.2f}")
            with col4:
                if st.button("Remove", key=f"remove_{idx}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()
            
            st.divider()
        
        st.markdown(f"### Total: PKR {total:.2f}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear Cart", use_container_width=True):
                st.session_state.cart = []
                st.rerun()
        with col2:
            if st.button("Proceed to Checkout", use_container_width=True):
                st.session_state.page = 'checkout'
                st.rerun()

elif st.session_state.page == 'checkout':
    st.header("💳 Checkout")
    
    
    if not st.session_state.cart:
        st.error("Your cart is empty!")
        if st.button("Go to Menu"):
            st.session_state.page = 'menu'
            st.rerun()
    else:
        # Order summary
        st.subheader("Order Summary")
        total = 0
        for item in st.session_state.cart:
            item_total = item['price'] * item['quantity']
            total += item_total
            st.write(f"{item['name']} x {item['quantity']} = PKR {item_total:.2f}")
        
        st.markdown(f"### Total: PKR {total:.2f}")
        
        # Payment form
        st.subheader("Payment Information")
        with st.form("payment_form"):
            col1, col2 = st.columns(2)
            with col1:
                card_number = st.text_input("Card Number", placeholder="1234 5678 9012 3456")
                expiry = st.text_input("Expiry Date", placeholder="MM/YY")
            with col2:
                cvv = st.text_input("CVV", placeholder="123", type="password")
                cardholder_name = st.text_input("Cardholder Name")
            
            # Delivery information
            st.subheader("Delivery Information")
            address = st.text_area("Delivery Address")
            phone = st.text_input("Phone Number")
            
            submit_order = st.form_submit_button("Place Order", use_container_width=True)
            
            if submit_order:
                if card_number and expiry and cvv and cardholder_name and address and phone:
                    # Create order in database
                    order_id = create_order(st.session_state.user['id'], st.session_state.cart, total)
                    
                    # Clear cart
                    st.session_state.cart = []
                    
                    # Show success page
                    st.session_state.page = 'success'
                    st.session_state.order_id = order_id
                    st.session_state.order_total = total
                    st.rerun()
                else:
                    st.error("Please fill in all fields")

elif st.session_state.page == 'success':
    st.markdown("""
    <div class="success-message">
        <h2>🎉 Order Successful!</h2>
        <p>Thank you for your order. Your food is being prepared!</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("Order Details")
    st.write(f"*Order ID:* #{st.session_state.order_id}")
    st.write(f"*Total Amount:* PKR {st.session_state.order_total:.2f}")
    st.write(f"*Estimated Delivery Time:* 30-45 minutes")
    
    st.info("You will receive a confirmation email shortly with tracking information.")
    
    if st.button("Order Again", use_container_width=True):
        st.session_state.page = 'menu'
        st.rerun()

# Footer
st.markdown("---")
st.markdown("© 2025 Restaurant Management System. Made with ❤️ using Streamlit")