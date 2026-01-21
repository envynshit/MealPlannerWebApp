import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

# Create models folder
os.makedirs("models", exist_ok=True)

print("="*60)
print("MODULE 1: FIES RandomForest Training (With Region)")
print("="*60)

# 1. Load ML features
print("\n📥 Loading data/fies_ml_features.csv...")
try:
    fies_ml = pd.read_csv("data/fies_ml_features.csv")
    print(f"✅ Loaded {len(fies_ml)} rows")
    print(f"Columns: {list(fies_ml.columns)}")
except FileNotFoundError:
    print("❌ File not found!")
    exit()

# 2. Encode region (convert text to numbers)
print("\n🔤 Encoding regions...")
le = LabelEncoder()
fies_ml['region_encoded'] = le.fit_transform(fies_ml['region'])
print(f"✅ Regions: {list(le.classes_)}")

# 3. Define features (X) and target (y)
print("\n📊 Preparing features...")
X = fies_ml[['income_per_person_monthly', 'household_size', 'region_encoded']]
y = fies_ml['security_level_num']  # 0=Secure, 1=Mildly, 2=Moderately, 3=Severely
print(f"✅ Features: {list(X.columns)}")
print(f"✅ Target: security_level_num (0-3)")
print(f"   Class distribution:\n{y.value_counts().sort_index()}")

# 4. Train-test split
print("\n🔀 Splitting data (80-20)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"✅ Train: {len(X_train)}, Test: {len(X_test)}")

# 5. Train RandomForest
print("\n🤖 Training RandomForest...")
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=6,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)
print("✅ Model trained!")

# 6. Evaluate
print("\n📈 Evaluating...")
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Accuracy: {acc:.4f} ({acc*100:.1f}%)")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, 
    target_names=["🟢 Secure", "🟡 Mildly", "🟠 Moderately", "🔴 Severely"]))

# 7. Save model
print("\n💾 Saving model...")
joblib.dump(model, "models/food_security_rf.pkl")
print("✅ Model saved: models/food_security_rf.pkl")

# 8. Save label encoder (for region encoding in Streamlit)
print("\n💾 Saving region encoder...")
joblib.dump(le, "models/region_encoder.pkl")
print("✅ Encoder saved: models/region_encoder.pkl")

# 9. Feature importance
print("\n📊 Feature Importance:")
for feat, imp in zip(X.columns, model.feature_importances_):
    print(f"  {feat}: {imp:.4f}")

print("\n" + "="*60)
print("✅ Module 1 Training Complete!")
print("="*60)
