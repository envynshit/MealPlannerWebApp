# module2_train_FIXED.py
# Complete training script with region mapping for Module 2

import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import numpy as np

# ============================================================================
# STEP 1: REGION MAPPING DICTIONARY (FIES → Recipe Regions)
# ============================================================================

REGION_MAP_FIES_TO_RECIPE = {
    # National level - fallback
    "PHILIPPINES": "National Capital region",
    
    # NCR (National Capital Region) - All variants
    "NCR": "National Capital region",
    "NCR I": "National Capital region",
    "NCR II": "National Capital region",
    "NCR III": "National Capital region",
    "NCR IV": "National Capital region",
    
    # NCR Cities - All map to National Capital region
    "City of Mandaluyong": "National Capital region",
    "City of San Juan": "National Capital region",
    "Quezon City": "National Capital region",
    "City of Marikina": "National Capital region",
    "City of Caloocan": "National Capital region",
    "City of Malabon": "National Capital region",
    "City of Navotas": "National Capital region",
    "City of Las Piñas": "National Capital region",
    "City of Muntinlupa": "National Capital region",
    "City of Parañaque": "National Capital region",
    "Pasay City": "National Capital region",
    "City of Makati": "National Capital region",
    "Pateros": "National Capital region",
    
    # CAR - CORDILLERA ADMINISTRATIVE REGION → Region I
    "CAR - CORDILLERA ADMINISTRATIVE REGION": "Region I",
    "Abra": "Region I",
    "Benguet (Excluding City of Baguio)": "Region I",
    "City of Baguio": "Region I",
    "Ifugao": "Region I",
    "Kalinga": "Region I",
    "Mountain Province": "Region I",
    "Apayao": "Region I",
    
    # Ilocos Region → Region I
    "Ilocos Norte": "Region I",
    "Ilocos Sur": "Region I",
    "La Union": "Region I",
    "Pangasinan": "Region I",
    
    # Central Luzon → Region III
    "Tarlac": "Region III",
    "Nueva Ecija": "Region III",
    "Zambales": "Region III",
    "Bulacan": "Region III",
    "Nueva Vizcaya": "Region III",
    "Quirino": "Region III",
    "Aurora": "Region III",
    
    # CALABARZON → Region IV-A
    "Batangas": "Region IV-A",
    "Cavite": "Region IV-A",
    "Laguna": "Region IV-A",
    "Quezon": "Region IV-A",
    "Rizal": "Region IV-A",
    "Marinduque": "Region IV-A",
    "Romblon": "Region IV-A",
    "Palawan": "Region IV-A",
    
    # Bicol Region → Region V
    "Albay": "Region V",
    "Camarines Norte": "Region V",
    "Camarines Sur": "Region V",
    "Catanduanes": "Region V",
    "Sorsogon": "Region V",
    "Masbate": "Region V",
    
    # Western Visayas → Region VI
    "Aklan": "Region VI",
    "Antique": "Region VI",
    "Capiz": "Region VI",
    "Guimaras": "Region VI",
    "Iloilo": "Region VI",
    "Negros Occidental": "Region VI",
    
    # Central Visayas → Region VII
    "Bohol": "Region VII",
    "Cebu": "Region VII",
    "Negros Oriental": "Region VII",
    "Siquijor": "Region VII",
    
    # Eastern Visayas → Region VIII
    "Biliran": "Region VII",  # Fallback to VII (no VIII in recipes)
    "Eastern Samar": "Region VII",
    "Leyte": "Region VII",
    "Northern Samar": "Region VII",
    "Samar": "Region VII",
    "Southern Leyte": "Region VII",
    
    # Zamboanga Peninsula → Region IX (fallback to VII)
    "Zamboanga del Norte": "Region VII",
    "Zamboanga del Sur": "Region VII",
    "Zamboanga Sibugay": "Region VII",
    "City of Isabela": "Region VII",
    
    # Northern Mindanao → Region X (fallback to VII)
    "Bukidnon": "Region VII",
    "Camiguin": "Region VII",
    "Lanao del Norte": "Region VII",
    "Misamis Occidental": "Region VII",
    "Misamis Oriental": "Region VII",
    
    # Davao Region → Region XI (fallback to VII)
    "Davao del Norte": "Region VII",
    "Davao del Sur": "Region VII",
    "Davao Oriental": "Region VII",
    "Davao de Oro": "Region VII",
    "Davao Occidental": "Region VII",
    "City of Davao": "Region VII",
    
    # Soccsksargen Region → Region XII (fallback to VII)
    "Cotabato (North Cotabato)": "Region VII",
    "South Cotabato (Excluding City of General Santos)": "Region VII",
    "City of General Santos (Dadiangas)": "Region VII",
    "Sultan Kudarat": "Region VII",
    "Sarangani": "Region VII",
    "Cotabato City": "Region VII",
    
    # Caraga Region → Region XIII (fallback to VII)
    "Agusan del Norte": "Region VII",
    "City of Butuan": "Region VII",
    "Agusan del Sur": "Region VII",
    "Surigao del Norte": "Region VII",
    "Surigao del Sur": "Region VII",
    "Dinagat Islands": "Region VII",
    
    # Bangsamoro Region (ARMM) → Region (fallback)
    "Basilan": "Region VII",
    "Lanao del Sur": "Region VII",
    "Maguindanao": "Region VII",
    "Maguindanao del Norte": "Region VII",
    "Maguindanao del Sur": "Region VII",
    "Sulu": "Region VII",
}

# ============================================================================
# STEP 2: LOAD & PROCESS DATA
# ============================================================================

print("📊 Loading datasets...")

# Load recipe costs dataset
recipe_df = pd.read_csv('data/module2_recipe_costs_by_region.csv')
print(f"✅ Recipe dataset loaded: {recipe_df.shape[0]} rows, {recipe_df.shape[1]} columns")
print(f"   Regions in recipe data: {recipe_df['region'].unique().tolist()}")

# Display dataset preview
print("\n📋 Recipe Dataset Preview:")
print(recipe_df.head())

# ============================================================================
# STEP 3: PREPARE FEATURES & TARGETS
# ============================================================================

print("\n🔧 Preparing features and targets...")

# Drop unnecessary columns
X = recipe_df[['region', 'category', 'type', 'serves']].copy()
y = recipe_df['cost_per_person'].copy()

print(f"Features shape: {X.shape}")
print(f"Target shape: {y.shape}")

# Encode categorical variables
print("\n🔐 Encoding categorical variables...")

le_region = LabelEncoder()
le_category = LabelEncoder()
le_type = LabelEncoder()

X['region'] = le_region.fit_transform(X['region'])
X['category'] = le_category.fit_transform(X['category'])
X['type'] = le_type.fit_transform(X['type'])

print(f"✅ Region classes: {le_region.classes_.tolist()}")
print(f"✅ Category classes: {le_category.classes_.tolist()}")
print(f"✅ Type classes: {le_type.classes_.tolist()}")

# ============================================================================
# STEP 4: TRAIN RANDOM FOREST MODEL
# ============================================================================

print("\n🤖 Training Random Forest model...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestRegressor(
    n_estimators=100,
    max_depth=15,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# ============================================================================
# STEP 5: EVALUATE MODEL
# ============================================================================

print("\n📈 Model Evaluation:")

y_pred = model.predict(X_test)
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print(f"✅ R² Score: {r2:.4f}")
print(f"✅ MAE: ₱{mae:.2f}")
print(f"✅ RMSE: ₱{rmse:.2f}")

# Feature importance
feature_names = ['region', 'category', 'type', 'serves']
feature_importance = pd.DataFrame({
    'feature': feature_names,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("\n📊 Feature Importance:")
print(feature_importance)

# ============================================================================
# STEP 6: SAVE ARTIFACTS & MAPPING
# ============================================================================

print("\n💾 Saving artifacts...")

# Save model
joblib.dump(model, 'recipe_cost_model.pkl')
print("✅ Model saved: recipe_cost_model.pkl")

# Save encoders
encoders = {
    'region': le_region,
    'category': le_category,
    'type': le_type,
    'map_fies_to_recipe': REGION_MAP_FIES_TO_RECIPE
}
joblib.dump(encoders, 'encoders_mapping.pkl')
print("✅ Encoders saved: encoders_mapping.pkl")

# Save region mapping as JSON for reference
import json
with open('region_mapping.json', 'w') as f:
    json.dump(REGION_MAP_FIES_TO_RECIPE, f, indent=2)
print("✅ Region mapping saved: region_mapping.json")

# ============================================================================
# STEP 7: TEST PREDICTIONS
# ============================================================================

print("\n🧪 Testing predictions with various FIES regions...")

test_recipes = [
    ("Quezon City", "chicken", "dinner", 6),          # NCR city
    ("PHILIPPINES", "beef", "lunch", 8),              # National
    ("Tarlac", "pork", "breakfast", 4),              # Region III
    ("Cebu", "fish", "dinner", 6),                   # Region VII
    ("Albay", "gulay", "lunch", 6),                  # Region V
]

for fies_region, category, meal_type, serves in test_recipes:
    # Map FIES region to recipe region
    mapped_region = REGION_MAP_FIES_TO_RECIPE.get(fies_region, "National Capital region")
    
    # Encode
    region_enc = le_region.transform([mapped_region])[0]
    category_enc = le_category.transform([category])[0]
    type_enc = le_type.transform([meal_type])[0]
    
    # Predict
    prediction = model.predict([[region_enc, category_enc, type_enc, serves]])[0]
    
    print(f"\n📌 Input: {fies_region} ({category}, {meal_type}, serves {serves})")
    print(f"   → Mapped to: {mapped_region}")
    print(f"   → Predicted cost: ₱{prediction:.2f}/person")

print("\n" + "="*70)
print("✨ TRAINING COMPLETE! Module 2 is ready.")
print("="*70)
print("\n📝 Summary:")
print(f"   • Model: Random Forest (100 estimators)")
print(f"   • Performance: R² = {r2:.4f}, MAE = ₱{mae:.2f}")
print(f"   • Region mapping: {len(REGION_MAP_FIES_TO_RECIPE)} FIES→Recipe mappings")
print(f"   • Saved files:")
print(f"     - recipe_cost_model.pkl")
print(f"     - encoders_mapping.pkl")
print(f"     - region_mapping.json")
print("\n✅ Ready for Streamlit integration!")