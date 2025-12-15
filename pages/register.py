import streamlit as st
import hashlib
from db import get_connection

st.set_page_config(page_title="AI Meal Planner - Register", page_icon="🍽️")

st.title("AI Meal Planner")
st.subheader("Register")

username = st.text_input("Username")
email = st.text_input("Email")
password = st.text_input("Password", type="password")
confirm_password = st.text_input("Confirm Password", type="password")

def create_users_table(conn):
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL UNIQUE,
            email VARCHAR(255) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
        """
    )
    conn.commit()

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode('utf-8')).hexdigest()

if st.button("Register"):
    # Basic validation
    if not username or not email or not password or not confirm_password:
        st.error("Please fill in all fields.")
    elif password != confirm_password:
        st.error("Passwords do not match.")
    elif len(password) < 6:
        st.error("Password must be at least 6 characters long.")
    else:
        try:
            conn = get_connection()
        except Exception as e:
            st.error(f"Could not connect to database: {e}")
        else:
            try:
                create_users_table(conn)
                cursor = conn.cursor(dictionary=True)

                # Check existing username or email
                cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
                existing = cursor.fetchone()
                if existing:
                    st.error("Username or email already exists. Please choose another.")
                else:
                    pw_hash = hash_password(password)
                    cursor.execute(
                        "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                        (username, email, pw_hash),
                    )
                    conn.commit()
                    st.success("Registration successful! You can now log in.")
                    if st.button("Go to Login"):
                        st.session_state.logged_in = False
                        st.switch_page("main.py")
            except Exception as e:
                st.error(f"Registration failed: {e}")
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
                try:
                    conn.close()
                except Exception:
                    pass

st.markdown("Already have an account? [Log in here](/)")