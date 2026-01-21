import streamlit as st
import hashlib
from sqlalchemy import text
from db import get_connection

st.set_page_config(page_title="NutriScopePH", layout="wide", page_icon="")

st.markdown("""
<div style='text-align:center; padding:4rem'>
    <h1 style='color:#4a90e2'>NutriScopePH</h1>
    <p style='color:#666; font-size:1.3rem'>An AI Food Security Assessment and Planning</p>
</div>
""", unsafe_allow_html=True)

col1, = st.columns([1])

with col1:
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login", use_container_width=True):
        if username and password:
            try:
                conn = get_connection()
                result = conn.execute(
                    text("SELECT id, username FROM users WHERE username=:u AND password_hash=:p"),
                    {"u": username, "p": hashlib.sha256(password.encode()).hexdigest()}
                ).fetchone()
                conn.close()
                
                if result:
                    st.session_state.logged_in = True
                    st.session_state.user = {"id": result[0], "username": result[1]}
                    st.session_state.user_id = result[0]
                    st.success("Welcome!")
                    st.switch_page("pages/dashboard.py")
                else:
                    st.error("Invalid credentials")
            except Exception as e:
                st.error(f"Login error: {e}")
        else:
            st.error("Enter credentials")

st.markdown("Dont have an Account?   [Register](/register)")

