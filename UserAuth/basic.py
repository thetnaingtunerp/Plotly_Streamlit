import streamlit as st
import hashlib
import sqlite3
import re
from datetime import datetime, timedelta
import pandas as pd

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'login_attempts' not in st.session_state:
    st.session_state.login_attempts = 0

# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS login_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT,
            success BOOLEAN,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

# Password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Email validation
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

# User registration
def register_user(username, email, password, full_name):
    if not is_valid_email(email):
        return False, "Invalid email format"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT INTO users (username, email, password_hash, full_name)
            VALUES (?, ?, ?, ?)
        ''', (username, email, hash_password(password), full_name))
        conn.commit()
        return True, "Registration successful"
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "Username already exists"
        elif "email" in str(e):
            return False, "Email already registered"
        else:
            return False, "Registration failed"
    finally:
        conn.close()

# User authentication
def authenticate_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT id, username, role, password_hash, is_active 
        FROM users 
        WHERE username = ? OR email = ?
    ''', (username, username))
    
    user = c.fetchone()
    conn.close()
    
    if not user:
        return False, "Invalid credentials"
    
    user_id, db_username, role, db_password_hash, is_active = user
    
    if not is_active:
        return False, "Account is deactivated"
    
    if hash_password(password) != db_password_hash:
        return False, "Invalid credentials"
    
    # Update last login
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('UPDATE users SET last_login = ? WHERE id = ?', 
              (datetime.now(), user_id))
    conn.commit()
    conn.close()
    
    return True, (user_id, db_username, role)

# Login page
def login_page():
    st.title("🔐 Login")
    
    with st.form("login_form"):
        username = st.text_input("Username or Email")
        password = st.text_input("Password", type="password")
        remember_me = st.checkbox("Remember me")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            login_button = st.form_submit_button("Login")
        with col2:
            if st.form_submit_button("Forgot Password?"):
                st.switch_page("pages/forgot_password.py")
        with col3:
            if st.form_submit_button("Register"):
                st.switch_page("pages/register.py")
    
    if login_button:
        if not username or not password:
            st.error("Please enter both username and password")
        else:
            success, result = authenticate_user(username, password)
            if success:
                user_id, db_username, role = result
                st.session_state.authenticated = True
                st.session_state.username = db_username
                st.session_state.user_role = role
                st.session_state.user_id = user_id
                st.session_state.login_attempts = 0
                
                # Store in cookies if remember me
                if remember_me:
                    st.session_state.remember_me = True
                
                st.success(f"Welcome {db_username}!")
                st.rerun()
            else:
                st.session_state.login_attempts += 1
                st.error(result)
                
                # Lock account after 5 failed attempts
                if st.session_state.login_attempts >= 5:
                    st.error("Too many failed attempts. Please try again later.")
                    st.stop()

# Registration page
def register_page():
    st.title("📝 Register")
    
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Username")
            email = st.text_input("Email")
        with col2:
            full_name = st.text_input("Full Name")
            password = st.text_input("Password", type="password")
        
        confirm_password = st.text_input("Confirm Password", type="password")
        terms = st.checkbox("I agree to the Terms and Conditions")
        
        submit = st.form_submit_button("Register")
        
        if submit:
            if not all([username, email, password, full_name]):
                st.error("All fields are required")
            elif password != confirm_password:
                st.error("Passwords do not match")
            elif len(password) < 8:
                st.error("Password must be at least 8 characters")
            elif not terms:
                st.error("You must agree to the terms and conditions")
            else:
                success, message = register_user(username, email, password, full_name)
                if success:
                    st.success(message)
                    st.info("You can now login with your credentials")
                    st.button("Go to Login", on_click=lambda: st.switch_page("app.py"))
                else:
                    st.error(message)

# Logout function
def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Protected route decorator
def protected_route(func):
    def wrapper(*args, **kwargs):
        if not st.session_state.get('authenticated', False):
            st.warning("Please login to access this page")
            login_page()
            st.stop()
        return func(*args, **kwargs)
    return wrapper

# Main app with authentication
def main():
    # Initialize database
    init_db()
    
    # Sidebar for authenticated users
    if st.session_state.authenticated:
        with st.sidebar:
            st.write(f"Welcome, **{st.session_state.username}**")
            st.write(f"Role: **{st.session_state.user_role}**")
            
            if st.button("Logout", type="primary"):
                logout()
            
            st.divider()
            
            # Navigation based on role
            if st.session_state.user_role == 'admin':
                st.page_link("app.py", label="Dashboard", icon="🏠")
                st.page_link("pages/users.py", label="User Management", icon="👥")
                st.page_link("pages/reports.py", label="Reports", icon="📊")
                st.page_link("pages/settings.py", label="Settings", icon="⚙️")
            else:
                st.page_link("app.py", label="Dashboard", icon="🏠")
                st.page_link("pages/profile.py", label="My Profile", icon="👤")
                st.page_link("pages/data.py", label="My Data", icon="📈")
    
    # Main content
    if not st.session_state.authenticated:
        login_page()
    else:
        protected_dashboard()

# Protected dashboard example
@protected_route
def protected_dashboard():
    st.title("🏠 Dashboard")
    
    # Role-based access control
    if st.session_state.user_role == 'admin':
        admin_dashboard()
    else:
        user_dashboard()

def admin_dashboard():
    st.subheader("Admin Panel")
    
    # User management
    conn = sqlite3.connect('users.db')
    users_df = pd.read_sql_query("SELECT id, username, email, role, created_at, last_login FROM users", conn)
    conn.close()
    
    st.dataframe(users_df, use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Users", len(users_df))
    with col2:
        active_users = len(users_df[users_df['last_login'].notna()])
        st.metric("Active Users", active_users)
    with col3:
        admin_count = len(users_df[users_df['role'] == 'admin'])
        st.metric("Admins", admin_count)

def user_dashboard():
    st.subheader(f"Welcome back, {st.session_state.username}!")
    
    # User-specific content
    col1, col2 = st.columns(2)
    
    with col1:
        st.card(
            "📊 Your Statistics",
            "View your activity and performance metrics",
            ["View Details"]
        )
    
    with col2:
        st.card(
            "📁 Recent Files",
            "Access your recently uploaded documents",
            ["Open Files"]
        )

if __name__ == "__main__":
    main()