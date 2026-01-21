import streamlit as st
import hashlib
from sqlalchemy import text
from db import get_connection


st.set_page_config(page_title="Register", layout="wide", page_icon="")


st.markdown("""
<div style='text-align:center; padding:4rem'>
    <h1 style='color:#50c878'>Create Account</h1>
    <p style='color:#666; font-size:1.3rem'>Join NutriScope PH</p>
</div>
""", unsafe_allow_html=True)


col1, = st.columns([1])


with col1:
    st.subheader("Sign Up")
    with st.form("register_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")
        
        submitted = st.form_submit_button("Register", use_container_width=True)
        
        if submitted:
            if not all([username, email, password, confirm]):
                st.error("Fill all fields")
            elif password != confirm:
                st.error("Passwords don't match")
            elif len(password) < 6:
                st.error("Password too short (min 6 chars)")
            else:
                try:
                    conn = get_connection()
                    pw_hash = hashlib.sha256(password.encode()).hexdigest()
                    
                    # Check duplicate
                    exists = conn.execute(
                        text("SELECT 1 FROM users WHERE username=:u OR email=:e"),
                        {"u": username, "e": email}
                    ).fetchone()
                    
                    if exists:
                        st.error("Username or email already taken")
                    else:
                        conn.execute(
                            text("INSERT INTO users (username, email, password_hash) VALUES (:u, :e, :h)"),
                            {"u": username, "e": email, "h": pw_hash}
                        )
                        st.success("Registered! Please login.")
                        st.switch_page("main.py")
                    conn.close()
                except Exception as e:
                    st.error(f"Error: {e}")


st.markdown("[Back to Login](/main.py)")
