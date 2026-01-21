"""
modules/meal_planner_engine.py
PHASE 3: Meal Planner Algorithm (UPDATED - SMART COST MIXING)
Core engine for generating personalized meal plans
"""

import pandas as pd
import random
from db import get_connection


class MealPlannerEngine:
    """
    Smart meal planner that generates 7-day meal plans based on:
    - User budget constraints
    - Allergy restrictions
    - Available recipes from database
    - Household size
    - SMART COST DISTRIBUTION (70-85% budget utilization)
    """
    
    def __init__(self):
        """Initialize the meal planner engine"""
        self.recipes_df = None
        self.load_recipes()
    
    # ========================================================================
    # PHASE 3.1: LOAD RECIPES FROM DATABASE
    # ========================================================================
    
    def load_recipes(self):
        """Load all recipes from PostgreSQL database"""
        try:
            conn = get_connection()
            query = """
                SELECT id, recipe, meal_name, total_cost, cost_per_person, 
                       servings, ingredients_used, ingredients, data_source
                FROM recipes
                ORDER BY cost_per_person ASC
            """
            self.recipes_df = pd.read_sql_query(query, conn)
            conn.close()
            print(f"✅ Loaded {len(self.recipes_df)} recipes from database")
        except Exception as e:
            print(f"❌ Error loading recipes: {str(e)}")
            self.recipes_df = None
    
    # ========================================================================
    # PHASE 3.2: FILTER RECIPES BY ALLERGIES
    # ========================================================================
    
    def filter_by_allergies(self, allergies):
        """
        Filter recipes to exclude allergic ingredients
        
        Args:
            allergies (list): List of allergens to exclude
            
        Returns:
            pd.DataFrame: Filtered recipes without allergens
        """
        if self.recipes_df is None or len(self.recipes_df) == 0:
            return None
        
        filtered = self.recipes_df.copy()
        
        # If no allergies, return all recipes
        if not allergies or len(allergies) == 0:
            return filtered
        
        # Remove recipes containing any allergen
        for allergy in allergies:
            allergy_lower = allergy.lower()
            # Filter out recipes containing this ingredient
            filtered = filtered[
                ~filtered['ingredients'].str.contains(allergy_lower, case=False, na=False)
            ]
        
        return filtered
    
    # ========================================================================
    # PHASE 3.3: FILTER RECIPES BY BUDGET
    # ========================================================================
    
    def filter_by_budget(self, recipes, daily_budget_per_person):
        """
        Filter recipes to only affordable ones
        
        Args:
            recipes (pd.DataFrame): Recipes to filter
            daily_budget_per_person (float): Daily budget per person (₱)
            
        Returns:
            pd.DataFrame: Recipes within budget (with 50% buffer for variety)
        """
        if recipes is None or len(recipes) == 0:
            return None
        
        # Allow 50% buffer for variety (can pick more expensive meals)
        # This ensures we have enough variety in price ranges
        max_cost = daily_budget_per_person * 1.5
        
        affordable = recipes[recipes['cost_per_person'] <= max_cost].copy()
        
        return affordable if len(affordable) > 0 else recipes.nsmallest(10, 'cost_per_person')
    
    # ========================================================================
    # PHASE 3.4: SELECT MEAL FOR ONE MEAL TIME (IMPROVED - SMART COST MIX)
    # ========================================================================
    
    def select_meal_for_mealtime(self, available_recipes, daily_budget_per_person, meal_type=None):
        """
        Select ONE meal (breakfast, lunch, or dinner) with SMART COST MIXING
        
        Strategy:
        - Breakfast: Usually cheap (₱15-25) - 20-25% of daily budget
        - Lunch: Medium-priced (₱25-40) - 30-40% of daily budget
        - Dinner: Better quality (₱35-50) - 40-45% of daily budget
        
        This ensures realistic meal plans that use 70-85% of budget
        
        Args:
            available_recipes (pd.DataFrame): Available recipes after filtering
            daily_budget_per_person (float): Daily budget per person
            meal_type (str): 'Breakfast', 'Lunch', or 'Dinner'
            
        Returns:
            pd.Series: Selected recipe details
        """
        if available_recipes is None or len(available_recipes) == 0:
            return None
        
        # SMART COST DISTRIBUTION
        # Total daily: target 75-90 pesos per person (vs unlimited budget)
        # Breakfast: 20% (cheap start)
        # Lunch: 35-40% (main meal)
        # Dinner: 40-45% (better quality)
        
        if meal_type == 'Breakfast':
            # Cheap breakfast (20-25% of daily budget)
            min_cost = 0
            max_cost = daily_budget_per_person * 0.28
        elif meal_type == 'Lunch':
            # Medium lunch (30-40% of daily budget)
            min_cost = daily_budget_per_person * 0.20
            max_cost = daily_budget_per_person * 0.45
        elif meal_type == 'Dinner':
            # Better dinner (40-50% of daily budget)
            min_cost = daily_budget_per_person * 0.30
            max_cost = daily_budget_per_person * 0.55
        else:
            # Default: balanced approach
            max_cost = daily_budget_per_person * 0.45
            min_cost = 0
        
        # Find recipes within this meal budget range
        suitable = available_recipes[
            (available_recipes['cost_per_person'] >= min_cost) &
            (available_recipes['cost_per_person'] <= max_cost)
        ]
        
        # If not enough options in ideal range, expand slightly
        if len(suitable) < 5:
            suitable = available_recipes[
                (available_recipes['cost_per_person'] >= min_cost) &
                (available_recipes['cost_per_person'] <= max_cost * 1.15)
            ]
        
        # If still not enough, expand more
        if len(suitable) < 3:
            suitable = available_recipes[
                available_recipes['cost_per_person'] <= max_cost * 1.3
            ]
        
        # Last resort: take cheapest options
        if len(suitable) == 0:
            suitable = available_recipes.nsmallest(10, 'cost_per_person')
        
        # Randomly select one recipe for variety (not always the cheapest)
        if len(suitable) > 0:
            selected = suitable.sample(n=1, random_state=None).iloc[0]
            return selected
        
        return None
    
    # ========================================================================
    # PHASE 3.5: VALIDATE BUDGET FEASIBILITY
    # ========================================================================
    
    def validate_budget_feasibility(self, available_recipes, daily_budget_per_person):
        """
        Check if budget is realistic for meal generation
        
        Args:
            available_recipes (pd.DataFrame): Available recipes
            daily_budget_per_person (float): Daily budget per person
            
        Returns:
            tuple: (is_feasible, message)
        """
        if available_recipes is None or len(available_recipes) == 0:
            return False, "❌ No recipes available after filtering. Try removing allergies or increasing budget."
        
        if len(available_recipes) < 15:
            return False, f"❌ Only {len(available_recipes)} recipes available. Need at least 15 for variety. Try removing allergies or increasing budget."
        
        # Check if cheapest recipes can fit in 3 meals
        cheapest_3 = available_recipes['cost_per_person'].nsmallest(3).sum()
        if cheapest_3 > daily_budget_per_person:
            return False, f"❌ Budget too low. Minimum needed: ₱{cheapest_3:.2f}/day. Try increasing budget."
        
        return True, "✅ Budget is feasible"
    
    # ========================================================================
    # PHASE 3.6: GENERATE 7-DAY MEAL PLAN (IMPROVED)
    # ========================================================================
    
    def generate_7day_meal_plan(self, daily_budget_per_person, allergies, household_size):
        """
        Generate complete 7-day meal plan with SMART COST DISTRIBUTION
        
        Args:
            daily_budget_per_person (float): Budget per person per day (₱)
            allergies (list): List of allergen restrictions
            household_size (int): Number of people in household
            
        Returns:
            tuple: (meal_plan_dict, total_weekly_cost_per_person, feasibility_status)
        """
        
        # Step 1: Filter recipes by allergies
        available = self.filter_by_allergies(allergies)
        if available is None:
            return None, 0.0, "❌ Database error: No recipes loaded"
        
        # Step 2: Filter recipes by budget
        available = self.filter_by_budget(available, daily_budget_per_person)
        
        # Step 3: Validate feasibility
        is_feasible, message = self.validate_budget_feasibility(available, daily_budget_per_person)
        if not is_feasible:
            return None, 0.0, message
        
        # Step 4: Generate 7 days with SMART cost distribution
        meal_plan = {}
        total_weekly_cost_per_person = 0.0
        
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        meal_types = ['Breakfast', 'Lunch', 'Dinner']
        
        for day_num in range(1, 8):
            day_name = days_of_week[day_num - 1]
            day_key = f"Day {day_num} ({day_name})"
            
            meals_for_day = {}
            day_total_per_person = 0.0
            
            # Select 3 meals for this day (with smart cost distribution)
            for meal_type in meal_types:
                selected_recipe = self.select_meal_for_mealtime(
                    available, 
                    daily_budget_per_person,
                    meal_type=meal_type
                )
                
                if selected_recipe is not None:
                    cost_per_person = float(selected_recipe['cost_per_person'])
                    total_for_household = cost_per_person * household_size
                    
                    meals_for_day[meal_type] = {
                        'recipe': str(selected_recipe['recipe']),
                        'meal_name': str(selected_recipe['meal_name']),
                        'cost_per_person': cost_per_person,
                        'total_cost_household': total_for_household,
                        'servings': int(selected_recipe['servings']),
                        'ingredients': str(selected_recipe['ingredients']),
                        'recipe_id': int(selected_recipe['id'])
                    }
                    day_total_per_person += cost_per_person
            
            meal_plan[day_key] = {
                'day_number': day_num,
                'day_name': day_name,
                'meals': meals_for_day,
                'day_total_per_person': day_total_per_person,
                'day_total_household': day_total_per_person * household_size
            }
            
            total_weekly_cost_per_person += day_total_per_person
        
        return meal_plan, total_weekly_cost_per_person, "✅ Meal plan generated successfully"
    
    # ========================================================================
    # PHASE 3.7: CALCULATE BUDGET STATS
    # ========================================================================
    
    def calculate_budget_stats(self, total_weekly_cost_per_person, weekly_budget, household_size):
        """
        Calculate budget utilization statistics
        
        Args:
            total_weekly_cost_per_person (float): Total weekly cost per person
            weekly_budget (float): Total weekly budget allocated
            household_size (int): Number of people in household
            
        Returns:
            dict: Budget statistics
        """
        total_cost_household = total_weekly_cost_per_person * household_size
        budget_used_percent = (total_weekly_cost_per_person / weekly_budget) * 100
        savings = weekly_budget - total_weekly_cost_per_person
        
        return {
            'total_cost_per_person': total_weekly_cost_per_person,
            'total_cost_household': total_cost_household,
            'weekly_budget': weekly_budget,
            'budget_used_percent': budget_used_percent,
            'savings_per_person': max(0, savings),
            'total_meals': 21  # 7 days × 3 meals
        }


# ========================================================================
# HELPER FUNCTION FOR STREAMLIT
# ========================================================================

def get_meal_planner():
    """Factory function to get meal planner instance (for Streamlit caching)"""
    return MealPlannerEngine()
