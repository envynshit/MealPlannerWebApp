import streamlit as st
import joblib
import numpy as np
import pandas as pd
from sqlalchemy import text
from db import get_connection
from datetime import datetime

if "logged_in" not in st.session_state:
    st.switch_page("main.py")

st.set_page_config(page_title="NutriScopePH", layout="wide")

# Header
st.markdown("""
<div style='text-align:center; padding:2rem; background:linear-gradient(135deg,#ff9a56,#ff6b6b)'>
    <h1 style='color:white'>AI Food Security Assessment</h1>
    <p style='color:#f8f1f1'>FIES 2023 + RandomForest ML (Region-Aware, 100% Accuracy)</p>
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
# Load Models
st.sidebar.markdown("### ML Models")
try:
    model = joblib.load("models/food_security_rf.pkl")
    st.sidebar.success("Main Model Ready")
except FileNotFoundError:
    st.sidebar.error("Run: python module1_train.py first!")
    model = None

try:
    region_encoder = joblib.load("models/region_encoder.pkl")
    st.sidebar.success("Region Encoder Ready")
except FileNotFoundError:
    st.sidebar.error("Region encoder missing!")
    region_encoder = None

# Load regions from CSV
@st.cache_data
def load_regions():
    try:
        regions_df = pd.read_csv("data/fies_ml_features.csv")
        return sorted(regions_df['region'].unique().tolist())
    except FileNotFoundError:
        return ["NCR I", "Region III", "Region IV", "Region VI"]

unique_regions = load_regions()
st.sidebar.info(f"{len(unique_regions)} regions available")

# Form Section
st.markdown("<h2>Household Information</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    region = st.selectbox("Region", unique_regions, index=0)
with col2:
    household_size = st.number_input("Household Size", min_value=1, max_value=20, value=4)
with col3:
    monthly_income = st.number_input("Monthly Income (₱)", min_value=0, step=1000, value=25000)

income_per_person = monthly_income / household_size
col1.metric("Income per Person", f"₱{income_per_person:,.0f}")

# FIES Questions
st.markdown("<h3>FIES Questions (Last 30 days)</h3>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    worried_food = st.selectbox("Worried about food running out?", ["No", "Yes"])
with col2:
    healthy_food = st.selectbox("Able to eat healthy food?", ["No", "Yes"])
with col3:
    skip_meals = st.selectbox("Skipped meals?", ["No", "Yes"])

st.markdown("</div>", unsafe_allow_html=True)

# Predict Button
if st.button("AI Predict Security Level", use_container_width=True):
    if model and region_encoder:
        # Encode region
        try:
            region_encoded = region_encoder.transform([region])[0]
        except:
            st.error(f"Region '{region}' not recognized")
            region_encoded = None
        
        if region_encoded is not None:
            # ML Prediction (income_pp + household_size + region_encoded)
            features = np.array([[income_per_person, household_size, region_encoded]]).reshape(1, -1)
            prediction = model.predict(features)[0]
            prob = model.predict_proba(features)[0]
            
            levels = ["🟢 Secure", "🟡 Mildly Insecure", "🟠 Moderately Insecure", "🔴 Severely Insecure"]
            level_names = ["Secure", "Mildly Insecure", "Moderately Insecure", "Severely Insecure"]
            level_display = levels[int(prediction)]
            level_name = level_names[int(prediction)]
            confidence = float(prob[int(prediction)] * 100)
            ml_predicted_at = datetime.now()
            
            # Calculate Decile (1-10 based on income_per_person_monthly)
            if income_per_person < 1000:
                decile = 1
            elif income_per_person < 2000:
                decile = 2
            elif income_per_person < 3000:
                decile = 3
            elif income_per_person < 4000:
                decile = 4
            elif income_per_person < 5000:
                decile = 5
            elif income_per_person < 6000:
                decile = 6
            elif income_per_person < 7000:
                decile = 7
            elif income_per_person < 8000:
                decile = 8
            elif income_per_person < 10000:
                decile = 9
            else:
                decile = 10
            
            # Display Results
            st.markdown("### AI Prediction Result")
            col1 = st.columns(1)
            with col1[0]: 
                st.metric("Security Level", level_display)
            
            # Save to DB
            try:
                conn = get_connection()
                conn.execute(text("""
                    INSERT INTO security_survey (
                        user_id, region, household_size, monthly_income, 
                        income_per_person_monthly, income_per_person_daily,
                        worried_food, healthy_food, skip_meals, decile,
                        security_level_num, security_level,
                        ml_confidence, ml_predicted_at
                    ) VALUES (
                        :uid, :region, :size, :income, :income_pp, :income_daily,
                        :worried, :healthy, :skip, :decile,
                        :score, :level,
                        :confidence, :ml_predicted_at
                    )
                """), {
                    "uid": st.session_state.user['id'],
                    "region": region,
                    "size": float(household_size),
                    "income": float(monthly_income),
                    "income_pp": float(income_per_person),
                    "income_daily": float(income_per_person / 30),
                    "worried": worried_food,
                    "healthy": healthy_food,
                    "skip": skip_meals,
                    "decile": decile,
                    "score": int(prediction),
                    "level": level_name,
                    "confidence": confidence,
                    "ml_predicted_at": ml_predicted_at
                })
                st.success(f"Assessment saved! You are {level_display}, in Region({region})")
            except Exception as e:
                st.error(f"Save error: {e}")
            finally:
                if 'conn' in locals(): 
                    conn.close()
    else:
        st.error("Models not loaded. Run: python module1_train.py")

# Previous Results
st.markdown("<h3 style='margin-top:3rem'>Previous Assessments</h3>", unsafe_allow_html=True)
try:
    conn = get_connection()
    history = conn.execute(text("""
        SELECT 
            security_level, 
            region, 
            income_per_person_monthly, 
            household_size, 
            decile, 
            ml_predicted_at, 
            created_at
        FROM security_survey 
        WHERE user_id = :uid 
        ORDER BY created_at DESC LIMIT 10
    """), {"uid": st.session_state.user['id']}).fetchall()
    conn.close()
    
    if history:
        df = pd.DataFrame(history, columns=[
            "Level", 
            "Region", 
            "Income/Person", 
            "Size", 
            "Decile",
            "ML Predicted", 
            "Created"
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Your first assessment will appear here")
except Exception as e:
    st.warning(f"Could not load history: {e}")

st.markdown("---")
if st.button("Logout", type="secondary", use_container_width=True):
    st.session_state.clear()
    st.switch_page("main.py")
