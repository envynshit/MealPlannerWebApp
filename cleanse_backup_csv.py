#!/usr/bin/env python3

"""
DATA CLEANSING: Filter Backup CSV for AUTHENTIC FILIPINO FOODS ONLY

Purpose: Remove non-Filipino/fusion dishes and keep only traditional Filipino recipes
Output: REAL_RECIPE_COSTS_FILIPINOFOOD_ONLY_2026.csv
"""

import pandas as pd
import os

print("="*70)
print("CLEANSING: AUTHENTIC FILIPINO FOODS ONLY")
print("="*70)

# STEP 1: LOAD THE BACKUP CSV
print("\n📥 Loading backup CSV...")
df = pd.read_csv('REAL_RECIPE_COSTS_REALISTIC_2026-BACKUP.csv')
print(f"✅ Loaded {len(df)} recipes")

# STEP 2: AUTHENTIC FILIPINO RECIPES (Keep these!)
authentic_filipino_recipes = {
    # BREAKFAST
    'Arroz Caldo': 'Breakfast',
    'Lugaw': 'Breakfast',
    'Tapa': 'Breakfast',
    'Longganisa': 'Breakfast',
    'Pandesal': 'Breakfast',
    'Tocino': 'Breakfast',
    'Cornmeal Porridge': 'Breakfast',
    'Champorado': 'Breakfast',
    'Tuyo': 'Breakfast',
    'Goto': 'Breakfast',
    'Corned Beef': 'Breakfast',
    'Fried Rice': 'Breakfast',
    'Garlic Fried Rice': 'Breakfast',
    'Sinangag': 'Breakfast',
    'Taho': 'Breakfast',
    
    # LUNCH/MAIN DISHES - PORK
    'Adobo': 'Lunch',
    'Adobo sa Gata': 'Lunch',
    'Pork Guisado': 'Lunch',
    'Pork Afritada': 'Lunch',
    'Afritada': 'Lunch',
    'Pork Tinola': 'Lunch',
    'Pork Nilaga': 'Lunch',
    'Pork Estofado': 'Lunch',
    'Pork Mechado': 'Lunch',
    'Pork Embutido': 'Lunch',
    'Sinigang': 'Lunch',
    'Lechon Kawali': 'Lunch',
    'Inihawin': 'Lunch',
    'Inihaw na Liempo': 'Lunch',
    'Pork Inihaw': 'Lunch',
    'Tokwa\'t Baboy': 'Lunch',
    'Sisig': 'Lunch',
    'Dinuguan': 'Lunch',
    'Kulampot': 'Lunch',
    
    # LUNCH/MAIN DISHES - BEEF
    'Beef Adobo': 'Lunch',
    'Beef Caldereta': 'Lunch',
    'Beef Nilaga': 'Lunch',
    'Beef Bulalo': 'Lunch',
    'Beef Guisado': 'Lunch',
    'Beef Mechado': 'Lunch',
    'Beef Morcon': 'Lunch',
    'Beef Embutido': 'Lunch',
    'Bulalo': 'Lunch',
    
    # LUNCH/MAIN DISHES - CHICKEN
    'Chicken Adobo': 'Lunch',
    'Chicken Afritada': 'Lunch',
    'Tinola': 'Lunch',
    'Chicken Sopas': 'Lunch',
    'Inahos na Manok': 'Lunch',
    
    # LUNCH/MAIN DISHES - FISH/SEAFOOD
    'Grilled Fish': 'Lunch',
    'Fried Fish': 'Lunch',
    'Steamed Fish': 'Lunch',
    'Fish Tinola': 'Lunch',
    'Pesang Isda': 'Lunch',
    'Inihaw na Isda': 'Lunch',
    'Kinilaw': 'Lunch',
    'Ginataan na Isda': 'Lunch',
    'Lapu-Lapu sa Alsa': 'Lunch',
    'Sinigang na Hipon': 'Lunch',
    'Hilabos': 'Lunch',
    'Guisadong Hipon': 'Lunch',
    'Hawang Alaskan': 'Lunch',
    'Ginataang Hipon': 'Lunch',
    
    # LUNCH/MAIN DISHES - VEGETABLES
    'Pinakbet': 'Lunch',
    'Lapu-Lapu': 'Lunch',
    'Bicol Express': 'Lunch',
    'Kare-Kare': 'Lunch',
    'Sauteed Kangkong': 'Lunch',
    'Mixed Vegetables': 'Lunch',
    'Ginisang Ampalaya': 'Lunch',
    'Tortang Talong': 'Lunch',
    'Bistek Tagalog': 'Lunch',
    
    # LUNCH/MAIN DISHES - NOODLES/RICE
    'Pancit': 'Lunch',
    'Lumpia': 'Lunch',
    'Lumpia Shanghai': 'Lunch',
    'Lumpia Primavera': 'Lunch',
    
    # DESSERTS
    'Leche Flan': 'Dessert',
    'Ube': 'Dessert',
    'Halo-Halo': 'Dessert',
    'Bibingka': 'Dessert',
    'Puto': 'Dessert',
    'Suman': 'Dessert',
    'Turon': 'Dessert',
    'Buko Pie': 'Dessert',
}

# STEP 3: FILTER THE DATAFRAME
print("\n🔍 Filtering for authentic Filipino recipes...")
print(f"\nAuthentic Filipino recipes to keep: {len(authentic_filipino_recipes)}")

# Check which recipes are in the data
df['recipe_match'] = df['recipe'].apply(
    lambda x: any(auth in x for auth in authentic_filipino_recipes.keys())
)

filtered_df = df[df['recipe_match']].copy()
print(f"✅ Found {len(filtered_df)} authentic Filipino recipes in the data")

# Show recipes found
print("\n✅ Recipes found:")
for idx, row in filtered_df.iterrows():
    print(f"  • {row['recipe']} (₱{row['cost_per_person']:.2f}/person)")

# Show recipes NOT found
print("\n❌ Authentic recipes NOT in dataset:")
found_recipes = set()
for recipe in filtered_df['recipe']:
    for auth in authentic_filipino_recipes.keys():
        if auth in recipe:
            found_recipes.add(auth)

not_found = set(authentic_filipino_recipes.keys()) - found_recipes
if not_found:
    for recipe in sorted(not_found):
        print(f"  • {recipe}")
else:
    print("  (All or most recipes found!)")

# STEP 4: SAVE CLEANED CSV
print(f"\n💾 Saving cleaned CSV...")
output_file = 'REAL_RECIPE_COSTS_FILIPINOFOOD_ONLY_2026.csv'

# Reset columns and save
cleaned_df = filtered_df.drop('recipe_match', axis=1).reset_index(drop=True)
cleaned_df.to_csv(output_file, index=False)

print(f"✅ Saved: {output_file}")
print(f"✅ Recipes saved: {len(cleaned_df)}")

# STEP 5: SUMMARY STATISTICS
print("\n" + "="*70)
print("📊 DATASET SUMMARY:")
print("="*70)
print(f"\n✅ Total recipes: {len(cleaned_df)}")
print(f"✅ Price per person range: ₱{cleaned_df['cost_per_person'].min():.2f} - ₱{cleaned_df['cost_per_person'].max():.2f}")
print(f"✅ Mean price: ₱{cleaned_df['cost_per_person'].mean():.2f}")
print(f"✅ Median price: ₱{cleaned_df['cost_per_person'].median():.2f}")
print(f"✅ Standard deviation: ₱{cleaned_df['cost_per_person'].std():.2f}")

# Price distribution
print(f"\n📈 Price Distribution:")
print(f"  Budget (₱8-30):      {len(cleaned_df[cleaned_df['cost_per_person'] <= 30])} recipes")
print(f"  Medium (₱30-60):     {len(cleaned_df[(cleaned_df['cost_per_person'] > 30) & (cleaned_df['cost_per_person'] <= 60)])} recipes")
print(f"  Premium (₱60-100):   {len(cleaned_df[(cleaned_df['cost_per_person'] > 60) & (cleaned_df['cost_per_person'] <= 100)])} recipes")
print(f"  Luxury (₱100+):      {len(cleaned_df[cleaned_df['cost_per_person'] > 100])} recipes")

print(f"\n✨ CLEANSING COMPLETE!")
print("="*70)
print("\n🇵🇭 Ready for ML training with authentic Filipino food only! 🍽️")
