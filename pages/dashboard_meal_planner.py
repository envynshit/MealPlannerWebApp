import streamlit as st

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in to access the dashboard.")
    st.switch_page("main.py")

st.set_page_config(page_title="AI Meal Planner - Meal Planner", page_icon="🍽️")

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

st.header("Weekly Meal Planner")
st.write("Generate an income-based weekly meal plan (prototype).")

income = st.number_input("Monthly income (PHP)", min_value=0)
family_size = st.number_input("Family size", min_value=1, value=4)

if st.button("Generate plan"):
    st.write("Here we will show the meal plan for:", income, family_size)

st.write("---")
if st.button("Log out"):
    st.session_state.logged_in = False
    st.success("Logged out successfully!")
    st.switch_page("main.py")

# Add dark-styled metrics and sample meal plan summary
st.markdown(
    """
    <style>
    .dashboard-card {background: linear-gradient(180deg,#1b2733 0%, #0f1518 100%); padding:14px; border-radius:8px; color:#e6eef6}
    .metric {font-size:18px; font-weight:700}
    .metric-small {color:#9fb2c8}
    </style>
    """,
    unsafe_allow_html=True,
)

mc1, mc2, mc3 = st.columns(3)
with mc1:
    st.markdown("<div class='dashboard-card'><div class='metric'>Weekly</div><div class='metric-small'>Plan Count: 2</div></div>", unsafe_allow_html=True)
with mc2:
    st.markdown("<div class='dashboard-card'><div class='metric'>Budget</div><div class='metric-small'>₱2,400</div></div>", unsafe_allow_html=True)
with mc3:
    st.markdown("<div class='dashboard-card'><div class='metric'>Saved</div><div class='metric-small'>₱520</div></div>", unsafe_allow_html=True)
