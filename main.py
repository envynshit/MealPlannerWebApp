import streamlit as st
import hashlib
from db import get_connection

st.set_page_config(page_title="AI Meal Planner - Login", page_icon="🍽️")
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
st.title("AI Meal Planner")

st.subheader("Login")

username = st.text_input("Username")

password = st.text_input("Password", type="password")

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

if st.button("Log in"):
    if not username or not password:
        st.error("Please enter both username and password.")
    else:
        try:
            conn = get_connection()
            import sqlite3
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
        except Exception as e:
            st.error(f"Database connection error: {e}")
        else:
            try:
                pw_hash = hash_password(password)
                cursor.execute(
                    "SELECT id, username FROM users WHERE username = ? AND password_hash = ?",
                    (username, pw_hash),
                )
                user = cursor.fetchone()
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = {"id": user["id"], "username": user["username"]}
                    st.success("Logged in successfully!")
                    st.switch_page("pages/dashboard.py")
                else:
                    st.error("Invalid username or password.")
            except Exception as e:
                st.error(f"Login failed: {e}")
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
                try:
                    conn.close()
                except Exception:
                    pass

st.markdown("Don't have an account? [Register here](/register)")

