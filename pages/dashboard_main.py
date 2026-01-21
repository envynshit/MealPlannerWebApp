import streamlit as st
from sqlalchemy import text
from db import get_connection
import pandas as pd
import json
import altair as alt


if "logged_in" not in st.session_state:
    st.switch_page("main.py")


st.set_page_config(page_title="NutriScopePH", layout="wide")


# Header
st.markdown("""
<div style='text-align:center; padding:2rem; background:linear-gradient(135deg,#4a90e2,#50c878)'>
    <h1 style='color:white; margin:0'>AI Meal Planner Overview Dashboard</h1>
    <p style='color:#f0f8ff'>Your personalized food planning hub</p>
</div>
""", unsafe_allow_html=True)


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


# Welcome Section
col1, col2 = st.columns([2,1])
with col1:
    st.markdown("""
    <h2>Welcome back!</h2>
    <p>Track your food security assessments and generate personalized meal plans based on your budget and household needs.</p>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div style='background:#; padding:1.5rem; border-radius:10px; border-left:5px solid #50c878'>
        <h3>{st.session_state.user['username']}</h3>
        <p>ID: {st.session_state.user['id']}</p>
    </div>
    """, unsafe_allow_html=True)


# Key Metrics (DB-driven)
st.markdown("<h3> Quick Stats</h3>", unsafe_allow_html=True)
try:
    conn = get_connection()
    metrics = conn.execute(text("""
        SELECT 
            COUNT(DISTINCT s.id) as assessments,
            COUNT(DISTINCT m.id) as meal_plans,
            AVG(s.income_per_person_monthly) as avg_income_pp,
            COUNT(CASE WHEN s.security_level = 'Secure' THEN 1 END) as secure_count
        FROM security_survey s 
        LEFT JOIN meal_plans m ON s.user_id = m.user_id 
        WHERE s.user_id = :uid
    """), {"uid": st.session_state.user['id']}).fetchone()
    conn.close()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Assessments", metrics.assessments or 0)
    with col2: st.metric("Meal Plans", metrics.meal_plans or 0)
    with col3: st.metric("Avg Income/Person", f"₱{metrics.avg_income_pp:,.0f}" if metrics.avg_income_pp else "N/A")
    with col4: st.metric("Secure Results", metrics.secure_count or 0)
except:
    st.columns(4)[0].info(" Data appears after first assessment")


# =====================================================================
# RECENT MEAL PLANS WITH BUDGET & MEALS
# =====================================================================

st.markdown("<h3> Recent Meal Plans</h3>", unsafe_allow_html=True)

try:
    conn = get_connection()
    
    # Get latest meal plans with plan_data
    recent_plans = conn.execute(text("""
        SELECT id, week_start, region, household_size, weekly_budget, 
               total_weekly_cost, plan_data, created_at
        FROM meal_plans 
        WHERE security_id IN (
            SELECT id FROM security_survey WHERE user_id = :uid
        )
        ORDER BY week_start DESC 
        LIMIT 3
    """), {"uid": st.session_state.user['id']}).fetchall()
    
    conn.close()
    
    if recent_plans:
        # Tabs for each meal plan
        plan_tabs = st.tabs([f"Plan {i+1} - {plan.week_start}" for i, plan in enumerate(recent_plans)])
        
        for tab_idx, (tab, plan) in enumerate(zip(plan_tabs, recent_plans)):
            with tab:
                # Parse JSON plan_data
                try:
                    plan_data = json.loads(plan.plan_data) if isinstance(plan.plan_data, str) else plan.plan_data
                except:
                    st.error(f" Error parsing meal plan data")
                    continue
                
                # =========== BUDGET OVERVIEW ===========
                st.subheader(" Budget Overview")
                
                budget_info = plan_data.get('budget', {})
                weekly_budget = budget_info.get('weekly', plan.weekly_budget)
                actual_spent = budget_info.get('actual_spent', plan.total_weekly_cost)
                utilization = budget_info.get('utilization_percent', 0)
                
                budget_col1, budget_col2, budget_col3, budget_col4 = st.columns(4)
                with budget_col1:
                    st.metric(" Weekly Budget", f"₱{weekly_budget:,.2f}")
                with budget_col2:
                    st.metric(" Actual Spent", f"₱{actual_spent:,.2f}")
                with budget_col3:
                    st.metric(" Utilization", f"{utilization:.1f}%")
                with budget_col4:
                    savings = weekly_budget - actual_spent
                    st.metric(" Remaining", f"₱{savings:,.2f}")
                
                st.markdown("---")
                
                # =========== DAILY COST TRENDS ===========
                st.subheader(" Daily Cost Trends")
                
                meal_plan = plan_data.get('meal_plan', {})
                days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                
                daily_data = []
                for day in days_order:
                    if day in meal_plan:
                        day_info = meal_plan[day]
                        daily_data.append({
                            'Day': day,
                            'Cost Per Person': day_info.get('day_total_per_person', 0),
                            'Cost Family': day_info.get('day_total_family', 0),
                            'Budget %': day_info.get('budget_utilization_percent', 0)
                        })
                
                if daily_data:
                    df_daily = pd.DataFrame(daily_data)
                    
                    # Line chart for daily costs
                    chart = alt.Chart(df_daily).mark_line(point=True, color='#2E8B57').encode(
                        x=alt.X('Day:N', sort=days_order),
                        y=alt.Y('Cost Per Person:Q', title='Cost per Person (₱)'),
                        tooltip=['Day', 'Cost Per Person', 'Cost Family', 'Budget %']
                    ).properties(height=300, width=700)
                    
                    st.altair_chart(chart, use_container_width=True)
                    
                    # Show daily breakdown table
                    with st.expander(" Daily Breakdown Details"):
                        st.dataframe(df_daily, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                
                # =========== 7-DAY MEAL PLAN ===========
                st.subheader(" 7-Day Meal Plan")
                
                for day in days_order:
                    if day in meal_plan:
                        day_info = meal_plan[day]
                        day_cost = day_info.get('day_total_per_person', 0)
                        day_budget_util = day_info.get('budget_utilization_percent', 0)
                        
                        with st.expander(f" {day} - ₱{day_cost:.2f} ({day_budget_util:.1f}% budget)"):
                            col1, col2, col3 = st.columns(3)
                            
                            # Breakfast
                            with col1:
                                st.markdown("###  Breakfast")
                                if 'breakfast' in day_info:
                                    breakfast = day_info['breakfast']
                                    st.write(f"**{breakfast.get('name', 'N/A')}**")
                                    st.write(f"₱{breakfast.get('cost', 0):.2f}")
                                else:
                                    st.write("No breakfast planned")
                            
                            # Lunch
                            with col2:
                                st.markdown("###  Lunch")
                                if 'lunch' in day_info:
                                    lunch = day_info['lunch']
                                    st.write(f"**{lunch.get('name', 'N/A')}**")
                                    st.write(f"₱{lunch.get('cost', 0):.2f}")
                                else:
                                    st.write("No lunch planned")
                            
                            # Dinner
                            with col3:
                                st.markdown("###  Dinner")
                                if 'dinner' in day_info:
                                    dinner = day_info['dinner']
                                    st.write(f"**{dinner.get('name', 'N/A')}**")
                                    st.write(f"₱{dinner.get('cost', 0):.2f}")
                                else:
                                    st.write("No dinner planned")
                
                st.markdown("---")
                
                # Summary info
                summary = plan_data.get('summary', {})
                st.info(f"""
                ** Week Summary:**
                - Total Meals: {summary.get('total_meals', 0)}
                - Average Cost/Day: ₱{summary.get('avg_cost_per_day', 0):.2f}
                - Region: {plan.region}
                - Household Size: {plan.household_size} people
                """)
    
    else:
        st.info(" No meal plans yet. Generate your first meal plan to see it here!")

except Exception as e:
    st.error(f" Error loading meal plans: {str(e)}")
    st.info("Make sure your meal plans table has the correct structure")


# Logout
st.markdown("---")
if st.button("Logout", type="secondary", use_container_width=True):
    st.session_state.clear()
    st.switch_page("main.py")
