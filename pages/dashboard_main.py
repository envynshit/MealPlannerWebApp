import streamlit as st

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in to access the dashboard.")
    st.switch_page("main.py")

st.set_page_config(page_title="AI Meal Planner - Main Dashboard", page_icon="🏠")

# Horizontal navigation buttons
cols = st.columns(4)
with cols[0]:
    if st.button("Main"):
        st.switch_page("pages/dashboard_main.py")
with cols[1]:
    if st.button("Assessment"):
        st.switch_page("pages/dashboard_assessment.py")
with cols[2]:
    if st.button("Meal Planner"):
        st.switch_page("pages/dashboard_meal_planner.py")
with cols[3]:
    if st.button("Index"):
        st.switch_page("pages/dashboard.py")

st.title("Main Dashboard")
st.header("Welcome to the AI Meal Planner Prototype")
st.write("Use the navigation above to move between dashboard sections.")

if st.button("Log out"):
    st.session_state.logged_in = False
    st.success("Logged out successfully!")
    st.switch_page("main.py")

# Inject dark dashboard style and sample cards/chart
st.markdown(
    """
    <style>
    .dashboard-card {background: linear-gradient(180deg,#1b2733 0%, #0f1518 100%); padding:18px; border-radius:10px; color:#e6eef6}
    .metric {font-size:20px; font-weight:700}
    .metric-small {color:#9fb2c8}
    .section-title {font-size:20px; color:#cfe6ff; margin-bottom:8px}
    </style>
    """,
    unsafe_allow_html=True,
)

mc1, mc2, mc3 = st.columns(3)
with mc1:
    st.markdown("<div class='dashboard-card'><div class='metric'>$8,430.00</div><div class='metric-small'>Monthly Savings</div></div>", unsafe_allow_html=True)
with mc2:
    st.markdown("<div class='dashboard-card'><div class='metric'>128</div><div class='metric-small'>Active Plans</div></div>", unsafe_allow_html=True)
with mc3:
    st.markdown("<div class='dashboard-card'><div class='metric'>42</div><div class='metric-small'>New Users</div></div>", unsafe_allow_html=True)

import pandas as pd
import altair as alt
df = pd.DataFrame({"month": ["Jan","Feb","Mar","Apr","May","Jun"], "value":[10,20,30,25,35,45]})
chart = alt.Chart(df).mark_area(opacity=0.6).encode(x="month", y="value")
st.altair_chart(chart, use_container_width=True)
