import streamlit as st

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in to access the dashboard.")
    st.switch_page("main.py")

st.set_page_config(page_title="AI Meal Planner - Assessment", page_icon="📝")

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

st.header("Household Food Security Assessment (Prototype)")

st.write("Answer the questions below to get an indicative food security score for your household.")

with st.form("food_security_form"):
    st.subheader("Household profile")
    household_size = st.number_input("Number of people in the household", min_value=1, value=4)
    monthly_income = st.number_input("Estimated monthly household income (PHP)", min_value=0, step=1000)
    st.subheader("Food access in the last 30 days")
    q1 = st.selectbox(
        "In the last 30 days, did you worry that your household would not have enough food?",
        ["Yes", "No"]
    )
    q2 = st.selectbox(
        "In the last 30 days, did you or any household member skip meals because there was not enough food?",
        ["Yes", "No"]
    )
    q3 = st.selectbox(
        "In the last 30 days, did you or any household member go a whole day without eating because there was not enough food?",
        ["Yes", "No"]
    )
    submitted = st.form_submit_button("Submit")
    if submitted:
        score = 0
        if q1 == "Yes":
            score += 1
        if q2 == "Yes":
            score += 2
        if q3 == "Yes":
            score += 3

        st.write(f"Your household food security score is: {score}")
        if score == 0:
            st.success("Food Secure")
        elif score <= 2:
            st.warning("Mildly Food Insecure")
        elif score <= 4:
            st.error("Moderately Food Insecure")
        else:
            st.error("Severely Food Insecure")

st.write("---")
if st.button("Log out"):
    st.session_state.logged_in = False
    st.success("Logged out successfully!")
    st.switch_page("main.py")

# Small styled header area and metrics
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
    st.markdown("<div class='dashboard-card'><div class='metric'>4.2</div><div class='metric-small'>Avg Food Security</div></div>", unsafe_allow_html=True)
with mc2:
    st.markdown("<div class='dashboard-card'><div class='metric'>72%</div><div class='metric-small'>Access Rate</div></div>", unsafe_allow_html=True)
with mc3:
    st.markdown("<div class='dashboard-card'><div class='metric'>3</div><div class='metric-small'>Alerts</div></div>", unsafe_allow_html=True)
