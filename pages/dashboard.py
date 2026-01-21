import streamlit as st
from sqlalchemy import text
from db import get_connection
import pandas as pd
import altair as alt


if "logged_in" not in st.session_state:
    st.switch_page("main.py")


st.set_page_config(page_title="NutriScopePH", layout="wide")


# Header
st.markdown("""
<div style='text-align:center; padding:2rem; background:linear-gradient(135deg,#4a90e2,#50c878)'>
    <h1 style='color:white; margin:0'>Food Security Overview</h1>
    <p style='color:#f0f8ff'>Your Food Security Overview</p>
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

colss = st.columns(1)
with colss[0]:
    st.markdown(f"""
    <div style='padding:1rem'>
        <h2> Hi {st.session_state.user['username']}</h2>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")



# Create Tabs
tab1, tab2, tab3 = st.tabs(["Your Stats", "🇵🇭 National Poverty", "Food Prices"])


# ==================== TAB 1: YOUR STATS ====================
with tab1:
    st.markdown("<h3>Your Personal Statistics</h3>", unsafe_allow_html=True)
    
    try:
        conn = get_connection()
        stats = conn.execute(text("""
            SELECT 
                COUNT(*) as total_assessments,
                COUNT(CASE WHEN security_level = 'Secure' THEN 1 END)::float / NULLIF(COUNT(*), 0) * 100 as secure_pct,
                AVG(income_per_person_monthly) as avg_income
            FROM security_survey WHERE user_id = :uid
        """), {"uid": st.session_state.user['id']}).fetchone()
        conn.close()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Assessments", stats.total_assessments or 0)
        with col2:
            st.metric("Secure %", f"{stats.secure_pct:.0f}%" if stats.total_assessments else "0%")
        with col3:
            st.metric("Avg Income/Person", f"₱{stats.avg_income:,.0f}" if stats.avg_income else "N/A")
    except:
        st.info("Complete assessments to see personalized stats")


    # Your regional results
    st.markdown("<h4>Your Assessment Results by Region</h4>", unsafe_allow_html=True)
    try:
        conn = get_connection()
        user_regions = conn.execute(text("""
            SELECT 
                region, 
                COUNT(*) as count,
                ROUND(AVG(income_per_person_monthly)::numeric, 2) as avg_income,
                security_level
            FROM security_survey 
            WHERE user_id = :uid
            GROUP BY region, security_level
            ORDER BY count DESC
        """), {"uid": st.session_state.user['id']}).fetchall()
        conn.close()
        
        if user_regions:
            df_user = pd.DataFrame(user_regions, columns=["Region", "Count", "Avg Income", "Level"])
            st.dataframe(df_user, use_container_width=True, hide_index=True)
        else:
            st.info("No assessments yet - Go to Assessment to create one!")
    except:
        st.info("Could not load assessment results")


# ==================== TAB 2: NATIONAL POVERTY ====================
with tab2:
    st.markdown("<h3>🇵🇭 Regional Poverty Rates</h3>", unsafe_allow_html=True)
    
    # Explanation
    st.markdown("""
    **What is this?**  
    This chart shows the percentage of poor households in each Philippine region based on official government data.
    Regions with higher poverty rates typically face greater food security challenges.
    
    **Data Source**: Philippine Statistics Authority (PSA) FIES 2023, World Food Programme (WFP)
    """)
    
    try:
        # Load regional context data
        regional_data = pd.read_csv("data/module1_regional_context.csv")
        
        # Sort by poverty DESCENDING (highest first)
        regional_sorted = regional_data.sort_values('poverty_pct', ascending=False)
        
        # Create horizontal bar chart
        chart = alt.Chart(regional_sorted).mark_bar().encode(
            y=alt.Y('region:N', title='Region', sort='-x'),
            x=alt.X('poverty_pct:Q', title='Poverty Rate (%)'),
            color=alt.Color('poverty_pct:Q', 
                           scale=alt.Scale(scheme='reds'),
                           title='Poverty %'),
            tooltip=['region:N', alt.Tooltip('poverty_pct:Q', format='.1f')]
        ).properties(
            height=500,
            width=800
        )
        
        st.altair_chart(chart, use_container_width=True)
        
        # Key Insights
        st.markdown("### Key Insights")
        col1, col2, col3 = st.columns(3)
        
        top_5_poverty = regional_sorted.head(5)['poverty_pct'].sum()
        
        with col1:
            st.metric(
                " Highest Poverty", 
                f"{regional_sorted.iloc[0]['region']}",
                f"{regional_sorted.iloc[0]['poverty_pct']:.1f}%"
            )
        with col2:
            st.metric(
                " Lowest Poverty", 
                f"{regional_sorted.iloc[-1]['region']}",
                f"{regional_sorted.iloc[-1]['poverty_pct']:.1f}%"
            )
        with col3:
            st.metric(
                "National Average", 
                f"Across all regions",
                f"{regional_data['poverty_pct'].mean():.1f}%"
            )
        
        # Detailed insights
        st.info(f"""
        ** Understanding the Data:**
        - **Top 5 Most Vulnerable Regions** account for **{top_5_poverty:.1f}%** of total poverty burden
        - Regions like **{regional_sorted.iloc[0]['region']}** (highest poverty) and **{regional_sorted.iloc[1]['region']}** (2nd highest) require targeted food security interventions
        - **{regional_sorted.iloc[-1]['region']}** has the lowest poverty, making food security more stable
        """)
        
        # Detailed Table
        st.markdown("###  Complete Data")
        display_df = regional_data.sort_values('poverty_pct', ascending=False)[['region', 'poverty_pct']]
        display_df.columns = ['Region', 'Poverty Rate (%)']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
    except FileNotFoundError:
        st.error(" Regional data file not found: data/module1_regional_context.csv")


# ==================== TAB 3: FOOD PRICES ====================
with tab3:
    st.markdown("<h3> Food Price Index by Region</h3>", unsafe_allow_html=True)
    
    # Explanation
    st.markdown("""
    **What is this?**  
    This chart displays the Consumer Price Index (CPI) for food in each region.
    A higher index means food is more expensive relative to the national baseline.
    Expensive food + high poverty = severe food insecurity risk.
    
    **Data Source**: Philippine Statistics Authority (PSA) Consumer Price Index, WFP Food Security Data
    """)
    
    try:
        # Load regional context data
        regional_data = pd.read_csv("data/module1_regional_context.csv")
        
        # Sort by CPI DESCENDING (highest first)
        regional_sorted = regional_data.sort_values('food_cpi_ave', ascending=False)
        
        # Create horizontal bar chart
        chart = alt.Chart(regional_sorted).mark_bar().encode(
            y=alt.Y('region:N', title='Region', sort='-x'),
            x=alt.X('food_cpi_ave:Q', title='Food Price Index (CPI)'),
            color=alt.Color('food_cpi_ave:Q', 
                           scale=alt.Scale(scheme='oranges'),
                           title='CPI'),
            tooltip=['region:N', alt.Tooltip('food_cpi_ave:Q', format='.1f')]
        ).properties(
            height=500,
            width=800
        )
        
        st.altair_chart(chart, use_container_width=True)
        
        # Key Insights
        st.markdown("###  Key Insights")
        col1, col2, col3 = st.columns(3)
        
        expensive_regions = regional_sorted.head(3)
        price_range = regional_sorted.iloc[0]['food_cpi_ave'] - regional_sorted.iloc[-1]['food_cpi_ave']
        
        with col1:
            st.metric(
                " Most Expensive", 
                f"{regional_sorted.iloc[0]['region']}",
                f"{regional_sorted.iloc[0]['food_cpi_ave']:.1f}"
            )
        with col2:
            st.metric(
                " Most Affordable", 
                f"{regional_sorted.iloc[-1]['region']}",
                f"{regional_sorted.iloc[-1]['food_cpi_ave']:.1f}"
            )
        with col3:
            st.metric(
                "Price Difference", 
                "Between extremes",
                f"{price_range:.1f} points"
            )
        
        # Detailed insights
        st.info(f"""
        ** Understanding the Data:**
        - **Top 3 Most Expensive Regions**: {', '.join(expensive_regions['region'].tolist())}
        - **Price Range**: From {regional_sorted.iloc[-1]['food_cpi_ave']:.1f} to {regional_sorted.iloc[0]['food_cpi_ave']:.1f} CPI points
        - Higher CPI = Food less affordable for low-income households
        - When combined with high poverty rates, this creates critical food insecurity risk
        """)
        
        # Detailed Table
        st.markdown("### Complete Data")
        display_df = regional_data.sort_values('food_cpi_ave', ascending=False)[['region', 'food_cpi_ave']]
        display_df.columns = ['Region', 'Food CPI']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
    except FileNotFoundError:
        st.error(" Regional data file not found: data/module1_regional_context.csv")


st.markdown("---")
st.markdown("""
<p style='text-align:center; color:#666; font-size:0.9rem'>
 <strong>Data Sources</strong>: Philippine Statistics Authority (PSA) FIES 2023 | World Food Programme (WFP) | Consumer Price Index<br>
ℹ Charts updated based on latest official government datasets
</p>
""", unsafe_allow_html=True)

# Logout
st.markdown("---")
if st.button("Logout", type="secondary", use_container_width=True):
    st.session_state.clear()
    st.switch_page("main.py")