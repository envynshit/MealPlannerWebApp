import streamlit as st
import pandas as pd
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from decimal import Decimal

from module2_meal_planner_optimized import AIWeeklyMealPlannerWithML

DB_CONFIG = {
    "host": "localhost",
    "port": 5000,
    "database": "meal_planner",
    "user": "postgres",
    "password": "database1"
}

def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def get_latest_security_id():
    """Get the latest/most recent security_id from security_survey table"""
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT id FROM security_survey
            ORDER BY id DESC
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return result['id']
        return None
    except Exception as e:
        st.error(f"Error loading latest security ID: {e}")
        if conn:
            conn.close()
        return None

def get_security_data(security_id):
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT id, region, household_size, monthly_income, security_level
            FROM security_survey
            WHERE id = %s
        """, (security_id,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return dict(result)
        return None
    except Exception as e:
        st.error(f"Error loading security data: {e}")
        if conn:
            conn.close()
        return None

def save_meal_plan(security_id, security_level, region, household_size,
                   monthly_income, weekly_budget, total_weekly_cost, allergies, meal_plan_data):
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        cursor = conn.cursor()
        
        today = datetime.now()
        week_start = today.strftime('%Y-%m-%d')
        
        plan_json = json.dumps(meal_plan_data, default=str)
        allergies_str = ', '.join(allergies) if allergies else None
        
        monthly_income = float(monthly_income) if isinstance(monthly_income, Decimal) else float(monthly_income)
        weekly_budget = float(weekly_budget) if isinstance(weekly_budget, Decimal) else float(weekly_budget)
        total_weekly_cost = float(total_weekly_cost) if isinstance(total_weekly_cost, Decimal) else float(total_weekly_cost)
        
        cursor.execute("""
            INSERT INTO meal_plans
            (security_id, security_level, region, household_size, monthly_income,
             week_start, weekly_budget, total_weekly_cost, allergies, plan_data, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            security_id, security_level, region, household_size, monthly_income,
            week_start, weekly_budget, total_weekly_cost, allergies_str, plan_json, 'Generated'
        ))
        
        plan_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        return plan_id
        
    except Exception as e:
        if conn:
            conn.close()
        st.error(f"Error saving to database: {str(e)}")
        return None

st.set_page_config(
    page_title="NutriScope PH",
    layout="wide"
)

st.markdown("""
<div style='text-align:center; padding:2rem; background:linear-gradient(135deg,#ff9a56,#ff6b6b)'>
    <h1 style='color:white'>AI Meal Planner</h1>
    <p style='color:#f8f1f1'>Personalized 7-day meal plans with budget optimization & allergies</p>
</div>
""", unsafe_allow_html=True)


if 'meal_planner' not in st.session_state:
    st.session_state.meal_planner = AIWeeklyMealPlannerWithML()
if 'plan_generated' not in st.session_state:
    st.session_state.plan_generated = False
if 'meal_plan_data' not in st.session_state:
    st.session_state.meal_plan_data = None
if 'plan_id' not in st.session_state:
    st.session_state.plan_id = None

st.markdown("---")
# Navigation Bar
cols = st.columns(4)
with cols[0]:
    if st.button("Security Assesment Overview", use_container_width=True): st.switch_page("pages/dashboard.py")
with cols[1]:
    if st.button("Security Assessment", use_container_width=True): st.switch_page("pages/dashboard_assessment.py")
with cols[2]:
    if st.button("Meal Planner", use_container_width=True): st.switch_page("pages/dashboard_meal_planner.py")
with cols[3]:
    if st.button("Meal Planner Overview", use_container_width=True): st.switch_page("pages/dashboard_main.py")
# AUTO-LOAD LATEST SECURITY ID
latest_security_id = get_latest_security_id()

if latest_security_id:
    security_id = latest_security_id
    security_data = get_security_data(security_id)
    
    if security_data:   
        region = security_data['region']
        household_size = security_data['household_size']
        monthly_income = float(security_data['monthly_income'])
        
        st.subheader("Your Information")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Survey ID", security_id)
        with col2:
            st.metric("Region", region)
        with col3:
            st.metric("Household Size", f"{household_size} people")
        with col4:
            st.metric("Monthly Income", f"₱{monthly_income:,.2f}")
        
        st.markdown("---")
        
        st.subheader("Meal Plan Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Food Security Level")
            security_level = st.selectbox(
                "Select your food security classification",
                [
                    "Food Secure",
                    "Mildly Food Insecure",
                    "Moderately Food Insecure",
                    "Severely Food Insecure"
                ],
                label_visibility="collapsed",
                help="Your food security classification from the survey"
            )
        
        with col2:
            st.subheader("Weekly Budget")
            auto_budget = (monthly_income * 0.25) / 4.33
            
            weekly_budget = st.number_input(
                "Edit your weekly budget (₱)",
                min_value=100.0,
                max_value=float(monthly_income),
                value=auto_budget,
                step=50.0,
                label_visibility="collapsed",
                help="Adjust your weekly budget as needed"
            )
            st.info(f"Base Calculation (25% of income ÷ 4.33 weeks): ₱{auto_budget:.2f}")
        
        st.markdown("---")
        
        st.subheader("Allergies & Restrictions")
        allergies = st.multiselect(
            "Select any allergies or restrictions",
            [
                "Peanuts",
                "Tree nuts",
                "Dairy",
                "Eggs",
                "Fish",
                "Shellfish",
                "Soy",
                "Wheat",
                "Sesame",
                "Gluten"
            ],
            help="Select all allergies that apply - we'll avoid these in your meal plan"
        )
        
        st.markdown("---")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("Generate Meal Plan", use_container_width=True, key="generate_btn"):
                with st.spinner("AI is creating your personalized meal plan..."):
                    try:
                        meal_planner = st.session_state.meal_planner
                        
                        # FIXED: Use correct method name
                        user_data = {
                            'income': monthly_income,
                            'family_size': household_size,
                            'region': region,
                            'security_level': security_level
                        }
                        
                        meal_plan = meal_planner.generate_weekly_meal_plan(
                            user_data,
                            custom_weekly_budget=weekly_budget,
                            allergies=allergies
                        )
                        
                        st.session_state.meal_plan_data = meal_plan
                        st.session_state.plan_generated = True
                        
                        total_weekly_cost = meal_plan.get('summary', {}).get('total_cost', 0)
                        
                        plan_id = save_meal_plan(
                            security_id=security_id,
                            security_level=security_level,
                            region=region,
                            household_size=household_size,
                            monthly_income=monthly_income,
                            weekly_budget=weekly_budget,
                            total_weekly_cost=total_weekly_cost,
                            allergies=allergies,
                            meal_plan_data=meal_plan
                        )
                        
                        st.session_state.plan_id = plan_id
                        st.success(f"Meal plan generated and saved! (Plan ID: {plan_id})")
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        with col2:
            if st.checkbox("Debug Info"):
                st.write(f"ID: {security_id}")
                st.write(f"Region: {region}")
                st.write(f"Budget: ₱{weekly_budget:.2f}")

        st.markdown("---")
        
        if st.session_state.plan_generated and st.session_state.meal_plan_data:
            meal_plan = st.session_state.meal_plan_data
            
            st.subheader("Budget Summary")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Weekly Budget", f"₱{weekly_budget:.2f}")
            
            with col2:
                actual_cost = meal_plan.get('summary', {}).get('total_cost', 0)
                st.metric("Actual Cost", f"₱{actual_cost:.2f}")
            
            with col3:
                utilization = (actual_cost / weekly_budget * 100) if weekly_budget > 0 else 0
                st.metric("Budget Utilization", f"{utilization:.1f}%")
            
            with col4:
                savings = weekly_budget - actual_cost
                st.metric("Remaining Budget", f"₱{savings:.2f}")
            
            st.markdown("---")
            
            st.subheader("7-Day Meal Plan")
            
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            
            for day in days:
                if day in meal_plan.get('meal_plan', {}):
                    day_data = meal_plan['meal_plan'][day]
                    day_cost = day_data.get('day_total_per_person', 0)
                    
                    with st.expander(f"{day} - ₱{day_cost:.2f}"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("###  Breakfast")
                            if 'breakfast' in day_data:
                                breakfast = day_data['breakfast']
                                st.write(f"**{breakfast.get('name', 'N/A')}**")
                                st.write(f"₱{breakfast.get('cost', 0):.2f}")
                            else:
                                st.write("No breakfast planned")
                        
                        with col2:
                            st.markdown("###  Lunch")
                            if 'lunch' in day_data:
                                lunch = day_data['lunch']
                                st.write(f"**{lunch.get('name', 'N/A')}**")
                                st.write(f"₱{lunch.get('cost', 0):.2f}")
                            else:
                                st.write("No lunch planned")
                        
                        with col3:
                            st.markdown("###  Dinner")
                            if 'dinner' in day_data:
                                dinner = day_data['dinner']
                                st.write(f"**{dinner.get('name', 'N/A')}**")
                                st.write(f"₱{dinner.get('cost', 0):.2f}")
                            else:
                                st.write("No dinner planned")
            
            st.markdown("---")
            
            st.subheader(" Export Options")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                csv_data = []
                for day in days:
                    if day in meal_plan.get('meal_plan', {}):
                        day_data = meal_plan['meal_plan'][day]
                        csv_data.append({
                            'Day': day,
                            'Breakfast': day_data.get('breakfast', {}).get('name', 'N/A'),
                            'Lunch': day_data.get('lunch', {}).get('name', 'N/A'),
                            'Dinner': day_data.get('dinner', {}).get('name', 'N/A'),
                            'Daily Cost': day_data.get('day_total_per_person', 0)
                        })
                
                csv_df = pd.DataFrame(csv_data)
                st.download_button(
                    label="Download as CSV",
                    data=csv_df.to_csv(index=False),
                    file_name=f"meal_plan_{security_id}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                json_data = json.dumps(meal_plan, indent=2, default=str)
                st.download_button(
                    label="Download as JSON",
                    data=json_data,
                    file_name=f"meal_plan_{security_id}_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
            
            with col3:
                st.info(f"Plan ID: {st.session_state.plan_id}\nSaved to database successfully!")
        
        else:
            st.info("**INSTRUCTIONS:**\n\n1️ Review your information above\n\n2️ Adjust budget & select allergies\n\n3️ Click ' Generate Meal Plan'\n\nYour meal plan will be automatically saved!")

    else:
        st.error("Error loading user data")
        st.warning("Please check if the security survey data exists in the database.")

else:
    st.error("No users found in security_survey table")
    st.warning("**What to do:**\n\n1. Complete Module 1 (Food Security Survey) first\n\n2. Make sure data is saved in the database\n\n3. Come back to Module 2")

    # Logout
st.markdown("---")
if st.button("Logout", type="secondary", use_container_width=True):
    st.session_state.clear()
    st.switch_page("main.py")
