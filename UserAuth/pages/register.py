# pages/register.py
import streamlit as st
import pandas as pd
import re
import hashlib
import sqlite3
from datetime import datetime
from utils.email_service import send_verification_email
from utils.validators import validate_password_strength, validate_email
import time

# Page configuration
st.set_page_config(
    page_title="Register - Auth System",
    page_icon="📝",
    layout="centered"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main {
        max-width: 500px;
        padding-top: 2rem;
    }
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 3rem;
        font-weight: 600;
    }
    .password-strength {
        margin-top: -10px;
        margin-bottom: 10px;
        font-size: 0.85rem;
    }
    .strength-weak { color: #ff4d4d; }
    .strength-fair { color: #ffa64d; }
    .strength-good { color: #66cc66; }
    .strength-strong { color: #339933; }
    .terms-container {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #4b6bfb;
        margin: 10px 0;
        font-size: 0.9rem;
    }
    .verification-sent {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# Database connection
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# Check if username/email exists
def check_user_exists(username=None, email=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if username:
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return "username"
    
    if email:
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return "email"
    
    conn.close()
    return None

# Generate email verification token
def generate_verification_token(email):
    import secrets
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now().timestamp() + (24 * 3600)  # 24 hours
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Store token in database
    cursor.execute("""
        INSERT INTO verification_tokens (email, token, expires_at) 
        VALUES (?, ?, ?)
    """, (email, token, expires_at))
    
    conn.commit()
    conn.close()
    
    return token

# Register new user
def register_user(user_data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Hash password
        hashed_password = hashlib.sha256(user_data['password'].encode()).hexdigest()
        
        # Generate verification token
        verification_token = generate_verification_token(user_data['email'])
        
        # Insert user
        cursor.execute("""
            INSERT INTO users 
            (username, email, password_hash, full_name, date_of_birth, phone, country, created_at, verification_token) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_data['username'],
            user_data['email'],
            hashed_password,
            user_data['full_name'],
            user_data.get('date_of_birth'),
            user_data.get('phone'),
            user_data.get('country'),
            datetime.now(),
            verification_token
        ))
        
        user_id = cursor.lastrowid
        
        # Insert user preferences
        cursor.execute("""
            INSERT INTO user_preferences (user_id, email_notifications, theme) 
            VALUES (?, ?, ?)
        """, (user_id, user_data.get('email_notifications', True), 'light'))
        
        conn.commit()
        conn.close()
        
        # Send verification email
        send_verification_email(user_data['email'], verification_token, user_data['full_name'])
        
        return True, "Registration successful! Please check your email to verify your account."
    
    except sqlite3.IntegrityError as e:
        return False, "Registration failed. Please try again."
    except Exception as e:
        return False, f"An error occurred: {str(e)}"

# Password strength checker
def check_password_strength(password):
    score = 0
    feedback = []
    
    # Length check
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("At least 8 characters")
    
    # Lowercase check
    if re.search(r'[a-z]', password):
        score += 1
    else:
        feedback.append("Lowercase letters")
    
    # Uppercase check
    if re.search(r'[A-Z]', password):
        score += 1
    else:
        feedback.append("Uppercase letters")
    
    # Digit check
    if re.search(r'\d', password):
        score += 1
    else:
        feedback.append("Numbers")
    
    # Special character check
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    else:
        feedback.append("Special characters")
    
    # Strength levels
    if score == 5:
        return "strong", "Strong password ✓", "#339933"
    elif score >= 3:
        return "good", "Good password", "#66cc66"
    elif score >= 2:
        return "fair", "Fair password", "#ffa64d"
    else:
        return "weak", "Weak password", "#ff4d4d", feedback

# Terms and Conditions
def show_terms_and_conditions():
    terms = """
    ### Terms and Conditions
    
    **1. Acceptance of Terms**
    By registering for an account, you agree to be bound by these Terms and Conditions.
    
    **2. User Account**
    - You must provide accurate and complete registration information
    - You are responsible for maintaining the confidentiality of your account
    - You must notify us immediately of any unauthorized use of your account
    
    **3. Privacy Policy**
    Your personal information will be handled in accordance with our Privacy Policy.
    
    **4. Acceptable Use**
    You agree not to use the service for any unlawful purpose or in any way that could damage the service.
    
    **5. Termination**
    We reserve the right to terminate accounts that violate these terms.
    """
    return terms

# Main registration form
def registration_form():
    st.title("Create Your Account 🚀")
    st.markdown("Join thousands of users who trust our platform")
    
    # Progress bar
    if 'registration_step' not in st.session_state:
        st.session_state.registration_step = 1
    
    # Steps
    steps = ["Personal Info", "Account Details", "Preferences", "Confirmation"]
    
    # Progress indicators
    cols = st.columns(len(steps))
    for i, step in enumerate(steps):
        with cols[i]:
            if i + 1 < st.session_state.registration_step:
                st.success(f"✓ {step}")
            elif i + 1 == st.session_state.registration_step:
                st.info(f"▶ {step}")
            else:
                st.write(f"{i + 1}. {step}")
    
    st.divider()
    
    # Initialize session state for form data
    if 'registration_data' not in st.session_state:
        st.session_state.registration_data = {}
    
    # Step 1: Personal Information
    if st.session_state.registration_step == 1:
        st.subheader("📋 Personal Information")
        
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name*", 
                                      placeholder="John",
                                      help="Enter your first name")
        
        with col2:
            last_name = st.text_input("Last Name*", 
                                     placeholder="Doe",
                                     help="Enter your last name")
        
        full_name = f"{first_name} {last_name}".strip() if first_name and last_name else ""
        
        date_of_birth = st.date_input(
            "Date of Birth",
            min_value=datetime(1900, 1, 1),
            max_value=datetime.now(),
            help="Optional"
        )
        
        phone = st.text_input("Phone Number", 
                             placeholder="+1 (123) 456-7890",
                             help="Optional")
        
        country = st.selectbox(
            "Country",
            ["Select Country", "United States", "Canada", "United Kingdom", "Australia", 
             "Germany", "France", "Japan", "Other"],
            help="Select your country"
        )
        
        if st.button("Next →", type="primary"):
            if not first_name or not last_name:
                st.error("Please fill in all required fields (marked with *)")
            else:
                st.session_state.registration_data.update({
                    'first_name': first_name,
                    'last_name': last_name,
                    'full_name': full_name,
                    'date_of_birth': date_of_birth if date_of_birth else None,
                    'phone': phone,
                    'country': country if country != "Select Country" else None
                })
                st.session_state.registration_step = 2
                st.rerun()
    
    # Step 2: Account Details
    elif st.session_state.registration_step == 2:
        st.subheader("🔐 Account Details")
        
        # Username with real-time validation
        username = st.text_input(
            "Username*", 
            placeholder="johndoe",
            help="Choose a unique username (3-20 characters)",
            key="username_input"
        )
        
        if username:
            if len(username) < 3:
                st.warning("Username must be at least 3 characters")
            elif len(username) > 20:
                st.warning("Username must be less than 20 characters")
            elif not re.match(r'^[a-zA-Z0-9_]+$', username):
                st.warning("Username can only contain letters, numbers, and underscores")
            else:
                exists = check_user_exists(username=username)
                if exists == "username":
                    st.error("Username already taken")
                else:
                    st.success("Username available ✓")
        
        # Email with validation
        email = st.text_input(
            "Email Address*", 
            placeholder="john.doe@example.com",
            help="We'll send a verification email to this address",
            key="email_input"
        )
        
        if email:
            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                st.warning("Please enter a valid email address")
            else:
                exists = check_user_exists(email=email)
                if exists == "email":
                    st.error("Email already registered")
                else:
                    st.success("Email available ✓")
        
        # Password with strength meter
        password = st.text_input(
            "Password*", 
            type="password",
            help="Create a strong password",
            key="password_input"
        )
        
        if password:
            strength, message, color, feedback = check_password_strength(password)
            st.markdown(f"""
            <div class="password-strength">
                Strength: <span class="strength-{strength}" style="color: {color}; font-weight: bold;">{message}</span>
            </div>
            """, unsafe_allow_html=True)
            
            if feedback:
                st.caption(f"Add: {', '.join(feedback)}")
        
        confirm_password = st.text_input(
            "Confirm Password*", 
            type="password",
            help="Re-enter your password",
            key="confirm_password_input"
        )
        
        if password and confirm_password and password != confirm_password:
            st.error("Passwords do not match")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state.registration_step = 1
                st.rerun()
        
        with col2:
            if st.button("Next →", type="primary", use_container_width=True):
                if not username or not email or not password or not confirm_password:
                    st.error("Please fill in all required fields")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                elif check_user_exists(username=username) == "username":
                    st.error("Username already taken")
                elif check_user_exists(email=email) == "email":
                    st.error("Email already registered")
                else:
                    st.session_state.registration_data.update({
                        'username': username,
                        'email': email,
                        'password': password
                    })
                    st.session_state.registration_step = 3
                    st.rerun()
    
    # Step 3: Preferences
    elif st.session_state.registration_step == 3:
        st.subheader("⚙️ Preferences")
        
        email_notifications = st.toggle(
            "Email Notifications",
            value=True,
            help="Receive updates and notifications via email"
        )
        
        newsletter = st.toggle(
            "Subscribe to Newsletter",
            value=True,
            help="Receive our weekly newsletter with tips and updates"
        )
        
        theme = st.radio(
            "Preferred Theme",
            ["Light", "Dark", "System Default"],
            horizontal=True
        )
        
        # Terms and Conditions
        with st.expander("📜 Read Terms and Conditions"):
            st.markdown(show_terms_and_conditions())
        
        terms_accepted = st.checkbox(
            "I agree to the Terms and Conditions*",
            help="You must agree to the terms to continue"
        )
        
        privacy_accepted = st.checkbox(
            "I agree to the Privacy Policy*",
            help="You must agree to the privacy policy"
        )
        
        marketing_consent = st.checkbox(
            "I consent to receive marketing communications",
            value=False
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state.registration_step = 2
                st.rerun()
        
        with col2:
            if st.button("Review Registration →", type="primary", use_container_width=True):
                if not terms_accepted or not privacy_accepted:
                    st.error("You must agree to the Terms and Conditions and Privacy Policy")
                else:
                    st.session_state.registration_data.update({
                        'email_notifications': email_notifications,
                        'newsletter': newsletter,
                        'theme': theme.lower().replace(' ', '_'),
                        'terms_accepted': terms_accepted,
                        'privacy_accepted': privacy_accepted,
                        'marketing_consent': marketing_consent
                    })
                    st.session_state.registration_step = 4
                    st.rerun()
    
    # Step 4: Confirmation
    elif st.session_state.registration_step == 4:
        st.subheader("📋 Review Your Information")
        
        data = st.session_state.registration_data
        
        # Summary table
        summary_data = {
            "Field": ["Full Name", "Email", "Username", "Country", "Date of Birth", "Phone"],
            "Value": [
                data.get('full_name', 'Not provided'),
                data.get('email', 'Not provided'),
                data.get('username', 'Not provided'),
                data.get('country', 'Not provided'),
                str(data.get('date_of_birth', 'Not provided')),
                data.get('phone', 'Not provided')
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        st.table(summary_df)
        
        # Preferences summary
        with st.expander("Preferences"):
            pref_col1, pref_col2 = st.columns(2)
            with pref_col1:
                st.write("**Email Notifications:**", "✓ Yes" if data.get('email_notifications') else "✗ No")
                st.write("**Newsletter:**", "✓ Subscribed" if data.get('newsletter') else "✗ Not subscribed")
            with pref_col2:
                st.write("**Theme:**", data.get('theme', 'light').replace('_', ' ').title())
                st.write("**Marketing Consent:**", "✓ Granted" if data.get('marketing_consent') else "✗ Not granted")
        
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("← Edit Personal Info", use_container_width=True):
                st.session_state.registration_step = 1
                st.rerun()
        
        with col2:
            if st.button("← Edit Account Details", use_container_width=True):
                st.session_state.registration_step = 2
                st.rerun()
        
        with col3:
            register_disabled = not data.get('terms_accepted') or not data.get('privacy_accepted')
            
            if st.button("Complete Registration 🎉", 
                        type="primary", 
                        use_container_width=True,
                        disabled=register_disabled):
                
                # Show loading spinner
                with st.spinner("Creating your account..."):
                    time.sleep(1)  # Simulate processing
                    
                    # Register user
                    success, message = register_user(data)
                    
                    if success:
                        # Show success message
                        st.markdown("""
                        <div class="verification-sent">
                            <h4>✅ Registration Successful!</h4>
                            <p>We've sent a verification email to <strong>{}</strong>.</p>
                            <p>Please check your inbox and click the verification link to activate your account.</p>
                        </div>
                        """.format(data['email']), unsafe_allow_html=True)
                        
                        # Show next steps
                        st.info("""
                        **Next Steps:**
                        1. Check your email inbox (and spam folder)
                        2. Click the verification link
                        3. Return to login page
                        """)
                        
                        # Clear session state after successful registration
                        if 'registration_data' in st.session_state:
                            del st.session_state.registration_data
                        if 'registration_step' in st.session_state:
                            del st.session_state.registration_step
                        
                        # Add delay before showing login button
                        time.sleep(2)
                        
                        if st.button("Go to Login Page", type="secondary", use_container_width=True):
                            st.switch_page("app.py")
                        
                        st.stop()
                    else:
                        st.error(message)
    
    # Footer with login link
    st.divider()
    st.markdown("""
    <div style='text-align: center; margin-top: 2rem;'>
        <p>Already have an account? <a href="/" target="_self">Login here</a></p>
    </div>
    """, unsafe_allow_html=True)

# Alternative simple registration form
def simple_registration_form():
    st.title("Quick Registration")
    
    with st.form("simple_register_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Username*", placeholder="Choose a username")
            email = st.text_input("Email*", placeholder="your.email@example.com")
        
        with col2:
            full_name = st.text_input("Full Name", placeholder="John Doe")
            password = st.text_input("Password*", type="password")
        
        confirm_password = st.text_input("Confirm Password*", type="password")
        
        terms = st.checkbox("I agree to the Terms and Conditions*")
        
        submitted = st.form_submit_button("Register", type="primary")
        
        if submitted:
            if not all([username, email, password, confirm_password, terms]):
                st.error("Please fill in all required fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            else:
                user_data = {
                    'username': username,
                    'email': email,
                    'full_name': full_name,
                    'password': password
                }
                
                success, message = register_user(user_data)
                
                if success:
                    st.success(message)
                    
                    # Show verification instructions
                    st.info("""
                    **Important:** 
                    - Check your email for the verification link
                    - The link expires in 24 hours
                    - Verify your email to complete registration
                    """)
                    
                    if st.button("Go to Login", type="secondary"):
                        st.switch_page("app.py")
                else:
                    st.error(message)

# Main function
def main():
    # Check if user is already logged in
    if st.session_state.get('authenticated', False):
        st.info("You are already logged in!")
        if st.button("Go to Dashboard"):
            st.switch_page("app.py")
        return
    
    # Show registration form
    registration_form()
    
    # Optional: Show simple form as alternative
    # with st.expander("Quick Registration"):
    #     simple_registration_form()

# Run the app
if __name__ == "__main__":
    main()