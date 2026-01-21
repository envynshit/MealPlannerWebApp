"""
test_meal_planner.py
Quick test of PHASE 3 meal planner engine (UPDATED - SMART COST MIXING)
"""

from models.meal_planner_engine import MealPlannerEngine


# Test 1: Initialize engine
print("=" * 60)
print("TEST 1: Initialize Meal Planner Engine")
print("=" * 60)
planner = MealPlannerEngine()


if planner.recipes_df is not None:
    print(f"✅ Recipes loaded: {len(planner.recipes_df)} recipes")
else:
    print("❌ Failed to load recipes")
    exit()


# Test 2: Generate meal plan (no allergies)
print("\n" + "=" * 60)
print("TEST 2: Generate 7-Day Meal Plan (No Allergies)")
print("=" * 60)

daily_budget = 88.50
weekly_budget = daily_budget * 7

meal_plan, total_cost, status = planner.generate_7day_meal_plan(
    daily_budget_per_person=daily_budget,
    allergies=[],
    household_size=4
)


print(status)
if meal_plan is not None:
    print(f"✅ Total weekly cost per person: ₱{total_cost:,.2f}")
    print(f"✅ Days generated: {len(meal_plan)}")
    print(f"✅ Budget utilization: {(total_cost/weekly_budget)*100:.1f}%")
    
    # Show sample day with detailed breakdown
    first_day = list(meal_plan.values())[0]
    print(f"\nSample - {list(meal_plan.keys())[0]}:")
    day_total = 0.0
    for meal_type, meal_info in first_day['meals'].items():
        cost = meal_info['cost_per_person']
        print(f"  {meal_type}: {meal_info['recipe']} (₱{cost:.2f})")
        day_total += cost
    print(f"  Day Total: ₱{day_total:.2f}")
else:
    print(f"❌ Error: {total_cost}")


# Test 3: Generate with allergies
print("\n" + "=" * 60)
print("TEST 3: Generate with Pork & Seafood Allergies")
print("=" * 60)


meal_plan, total_cost, status = planner.generate_7day_meal_plan(
    daily_budget_per_person=daily_budget,
    allergies=['Pork', 'Seafood'],
    household_size=4
)


print(status)
if meal_plan is not None:
    print(f"✅ Total weekly cost per person: ₱{total_cost:,.2f}")
    print(f"✅ Days generated: {len(meal_plan)}")
    print(f"✅ Budget utilization: {(total_cost/weekly_budget)*100:.1f}%")
    
    # Show sample day
    first_day = list(meal_plan.values())[0]
    print(f"\nSample - {list(meal_plan.keys())[0]}:")
    for meal_type, meal_info in first_day['meals'].items():
        print(f"  {meal_type}: {meal_info['recipe']} (₱{meal_info['cost_per_person']:.2f})")
else:
    print(f"❌ Error: {total_cost}")


# Test 4: Calculate stats
print("\n" + "=" * 60)
print("TEST 4: Budget Statistics")
print("=" * 60)


stats = planner.calculate_budget_stats(
    total_weekly_cost_per_person=total_cost,
    weekly_budget=weekly_budget,
    household_size=4
)


print(f"Total Cost/Person: ₱{stats['total_cost_per_person']:,.2f}")
print(f"Total Cost/Family: ₱{stats['total_cost_household']:,.2f}")
print(f"Weekly Budget: ₱{stats['weekly_budget']:,.2f}")
print(f"Budget Used: {stats['budget_used_percent']:.1f}%")
print(f"Savings: ₱{stats['savings_per_person']:,.2f}")
print(f"Total Meals: {stats['total_meals']}")


# Test 5: Compare before and after
print("\n" + "=" * 60)
print("TEST 5: Algorithm Comparison (Old vs New)")
print("=" * 60)
print("OLD Algorithm:")
print("  - Budget Utilization: 15.1%")
print("  - Daily Cost: ₱58.69")
print("  - Result: TOO CHEAP ❌")
print("\nNEW Algorithm (Smart Cost Mixing):")
print(f"  - Budget Utilization: {stats['budget_used_percent']:.1f}%")
print(f"  - Daily Cost: ₱{total_cost/7:.2f}")
print(f"  - Result: REALISTIC ✅" if 70 <= stats['budget_used_percent'] <= 85 else f"  - Result: ACCEPTABLE")


print("\n" + "=" * 60)
print("✅ ALL TESTS COMPLETED!")
print("=" * 60)
