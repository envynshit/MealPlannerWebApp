import streamlit as st

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in to access the dashboard.")
    st.switch_page("main.py")

st.set_page_config(page_title="AI Meal Planner - Dashboard Index", page_icon="📊")

# Horizontal navigation buttons
cols = st.columns(3)
with cols[0]:
    if st.button("Main"):
        st.switch_page("pages/dashboard_main.py")
with cols[1]:
    if st.button("Assessment"):
        st.switch_page("pages/dashboard_assessment.py")
with cols[2]:
    if st.button("Meal Planner"):
        st.switch_page("pages/dashboard_meal_planner.py")

# Basic dark theme / layout to match prototype style
st.markdown(
    """
    <style>
    .dashboard-card {background: linear-gradient(180deg,#1b2733 0%, #11161b 100%); padding:18px; border-radius:10px; color:#e6eef6}
    .metric {font-size:20px; font-weight:700}
    .metric-small {color:#9fb2c8}
    .section-title {font-size:20px; color:#cfe6ff; margin-bottom:8px}
    .topbar {display:flex; gap:12px; align-items:center}
    </style>
    """,
    unsafe_allow_html=True,
)

cols = st.columns([1,2,1])
with cols[0]:
    # small avatar placeholder (avoid passing empty path to st.image)
    st.markdown("<div style='width:48px;height:48px;border-radius:50%;background:#2b3b45'></div>", unsafe_allow_html=True)
with cols[1]:
    st.markdown("<div class='topbar'><h2 style='margin:0;color:#dbeffd'>Dashboard</h2></div>", unsafe_allow_html=True)
with cols[2]:
    st.text_input("Search", key="dash_search")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("<div class='dashboard-card'><div class='metric'>$12,000.00</div><div class='metric-small'>Total AdSense</div></div>", unsafe_allow_html=True)
with c2:
    st.markdown("<div class='dashboard-card'><div class='metric'>741,570</div><div class='metric-small'>Total News</div></div>", unsafe_allow_html=True)
with c3:
    st.markdown("<div class='dashboard-card'><div class='metric'>172,510</div><div class='metric-small'>Total Video</div></div>", unsafe_allow_html=True)

import pandas as pd
import altair as alt
months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
values = [30,45,50,60,55,70,65,80,90,95,120,140]
df = pd.DataFrame({"month": months, "value": values})
chart = alt.Chart(df).mark_line(point=True).encode(x="month", y="value").properties(height=240)
st.altair_chart(chart, use_container_width=True)

st.title("Dashboard Index")

st.write("---")
st.write("Welcome to your food security and meal planning dashboard. Use the navigation above to choose a section.")

if st.button("Log out"):
    st.session_state.logged_in = False
    st.success("Logged out successfully!")
    st.switch_page("main.py")





