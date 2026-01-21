"""
modules/meal_planner_engine.py
PHASE 3: Meal Planner Algorithm (OPTION C - FLEXIBLE WITH WARNINGS)
Core engine for generating personalized meal plans with proper meal categorization
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
    - MEAL TYPE VALIDATION (prevents desserts as main meals)
    
    OPTION C FEATURES:
    - Flexible validation (allows some budget overshoot with warnings)
    - Helpful warnings for edge cases
    - More realistic planning for restrictive diets
    """
    
    def __init__(self):
        """Initialize the meal planner engine"""
        self.recipes_df = None
        self.load_recipes()
    
    # ========================================================================
    # PHASE 3.1: LOAD RECIPES FROM DATABASE (WITH CATEGORIZATION)
    # ========================================================================
    
    def load_recipes(self):
        """Load all recipes from PostgreSQL database with meal categorization"""
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
            
            # Add meal_category based on meal_name (for better filtering)
            self.recipes_df['meal_category'] = self.recipes_df['meal_name'].str.lower().apply(self._categorize_meal)
            
            print(f"✅ Loaded {len(self.recipes_df)} recipes from database")
        except Exception as e:
            print(f"❌ Error loading recipes: {str(e)}")
            self.recipes_df = None
    
    def _categorize_meal(self, meal_name):
        """
        Categorize meal based on name to prevent desserts as main meals
        
        Returns:
        - 'main': Suitable for lunch/dinner (adobo, mechado, etc)
        - 'side': Light sides (salad, rice, etc)
        - 'dessert': Desserts/snacks (halo-halo, leche flan, etc)
        """
        meal_lower = str(meal_name).lower()
        
        # Desserts/Snacks/Beverages (NOT suitable as main meals)
        desserts = ['halo', 'leche', 'flan', 'taho', 'sago', 'halohalo', 'ice cream', 
                   'dessert', 'cake', 'pudding', 'jelly', 'mousse', 'candy', 'juice',
                   'smoothie', 'beverage', 'drinks', 'coffee', 'tea', 'shake', 'malt']
        
        # Main dishes (suitable for lunch/dinner)
        mains = ['adobo', 'mechado', 'guisado', 'nilaga', 'bulalo', 'sinigang',
                'tinola', 'curry', 'stew', 'roast', 'fried', 'grilled', 'inihaw',
                'lechon', 'embutido', 'morcon', 'relleno', 'caldereta', 'menudo',
                'afritada', 'picadillo', 'bistec', 'beef', 'chicken', 'fish', 'pork',
                'meat', 'pinakbet', 'gising', 'laing', 'sopas']
        
        if any(keyword in meal_lower for keyword in desserts):
            return 'dessert'
        elif any(keyword in meal_lower for keyword in mains):
            return 'main'
        else:
            return 'main'  # Default to main for unknown
    
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
        max_cost = daily_budget_per_person * 1.5
        
        affordable = recipes[recipes['cost_per_person'] <= max_cost].copy()
        
        return affordable if len(affordable) > 0 else recipes.nsmallest(10, 'cost_per_person')
    
    # ========================================================================
    # PHASE 3.4: SELECT MEAL FOR ONE MEAL TIME (WITH VALIDATION)
    # ========================================================================
    
    def select_meal_for_mealtime(self, available_recipes, daily_budget_per_person, meal_type=None):
        """
        Select ONE meal (breakfast, lunch, or dinner) with SMART COST MIXING
        
        Strategy:
        - Breakfast: Can be light/simple (₱15-25)
        - Lunch: Must be substantial main dish (₱25-40)
        - Dinner: Must be substantial main dish (₱35-50)
        
        VALIDATION: Prevents desserts/light items from being selected as main meals
        
        Args:
            available_recipes (pd.DataFrame): Available recipes after filtering
            daily_budget_per_person (float): Daily budget per person
            meal_type (str): 'Breakfast', 'Lunch', or 'Dinner'
            
        Returns:
            pd.Series: Selected recipe details
        """
        if available_recipes is None or len(available_recipes) == 0:
            return None
        
        # SMART COST DISTRIBUTION WITH MEAL VALIDATION
        if meal_type == 'Breakfast':
            # Breakfast can be simple (20-25% of daily budget)
            min_cost = 0
            max_cost = daily_budget_per_person * 0.28
            # Accept all categories for breakfast
            allowed_categories = ['main', 'side', 'dessert']
        
        elif meal_type == 'Lunch':
            # Lunch must be substantial (30-40% of daily budget)
            min_cost = daily_budget_per_person * 0.20
            max_cost = daily_budget_per_person * 0.45
            # ONLY accept main dishes, NOT desserts
            allowed_categories = ['main']
        
        elif meal_type == 'Dinner':
            # Dinner must be substantial (40-50% of daily budget)
            min_cost = daily_budget_per_person * 0.30
            max_cost = daily_budget_per_person * 0.55
            # ONLY accept main dishes, NOT desserts
            allowed_categories = ['main']
        
        else:
            # Default: balanced approach
            max_cost = daily_budget_per_person * 0.45
            min_cost = 0
            allowed_categories = ['main', 'side']
        
        # Find recipes within this meal budget range AND correct meal type
        suitable = available_recipes[
            (available_recipes['cost_per_person'] >= min_cost) &
            (available_recipes['cost_per_person'] <= max_cost) &
            (available_recipes['meal_category'].isin(allowed_categories))
        ]
        
        # If not enough options in ideal range, expand slightly (but keep category restriction)
        if len(suitable) < 5:
            suitable = available_recipes[
                (available_recipes['cost_per_person'] >= min_cost) &
                (available_recipes['cost_per_person'] <= max_cost * 1.15) &
                (available_recipes['meal_category'].isin(allowed_categories))
            ]
        
        # If still not enough, expand more (but keep category restriction)
        if len(suitable) < 3:
            suitable = available_recipes[
                (available_recipes['cost_per_person'] <= max_cost * 1.3) &
                (available_recipes['meal_category'].isin(allowed_categories))
            ]
        
        # Last resort: take any recipe of correct category (no cost restriction)
        if len(suitable) == 0:
            suitable = available_recipes[
                available_recipes['meal_category'].isin(allowed_categories)
            ]
        
        # Absolute last resort: take cheapest regardless (should rarely happen)
        if len(suitable) == 0:
            suitable = available_recipes.nsmallest(10, 'cost_per_person')
        
        # Randomly select one recipe for variety
        if len(suitable) > 0:
            selected = suitable.sample(n=1, random_state=None).iloc[0]
            return selected
        
        return None
    
    # ========================================================================
    # PHASE 3.5: VALIDATE BUDGET FEASIBILITY (OPTION C - FLEXIBLE)
    # ========================================================================
    
    def validate_budget_feasibility(self, available_recipes, daily_budget_per_person):
        """
        Check if budget is realistic for meal generation
        (OPTION C: More flexible with helpful warnings)
        
        Features:
        1. Reduced minimum main dishes (10 → 5) for more flexibility
        2. Allow budget overshoot with 10% tolerance
        3. Warn about restrictive allergies and limited variety
        
        Args:
            available_recipes (pd.DataFrame): Available recipes
            daily_budget_per_person (float): Daily budget per person
            
        Returns:
            tuple: (is_feasible, warnings_message)
        """
        if available_recipes is None or len(available_recipes) == 0:
            return False, "❌ No recipes available after filtering. Try removing allergies or increasing budget."
        
        warnings = []
        
        # ====================================================================
        # CHANGE 1: Reduce minimum main dishes requirement (10 → 5)
        # ====================================================================
        main_dishes = available_recipes[available_recipes['meal_category'] == 'main']
        if len(main_dishes) < 5:
            return False, f"❌ Only {len(main_dishes)} main dishes available. Budget constraints too tight. Try removing more allergies or increasing budget."
        elif len(main_dishes) < 10:
            # WARNING: Limited variety but still acceptable
            warnings.append(f"⚠️ Limited main dish variety ({len(main_dishes)} available). Plan may have repeated meals.")
        
        # Check minimum recipe variety (need at least 10 for acceptable plan)
        if len(available_recipes) < 10:
            return False, f"❌ Only {len(available_recipes)} recipes available. Need at least 10 for variety. Try removing allergies or increasing budget."
        elif len(available_recipes) < 15:
            # WARNING: Low variety
            warnings.append(f"⚠️ Limited recipe variety ({len(available_recipes)} available). You may see repeated meals in your plan.")
        
        # ====================================================================
        # CHANGE 2: Allow budget overshoot with 10% tolerance
        # ====================================================================
        cheapest_3 = available_recipes['cost_per_person'].nsmallest(3).sum()
        if cheapest_3 > daily_budget_per_person * 1.1:  # 10% buffer for flexibility
            return False, f"❌ Budget too low. Minimum needed: ₱{cheapest_3:.2f}/day. Try increasing budget by at least ₱{cheapest_3 - daily_budget_per_person:.2f}."
        elif cheapest_3 > daily_budget_per_person:
            # WARNING: Will slightly exceed budget (within tolerance)
            overshoot = cheapest_3 - daily_budget_per_person
            warnings.append(f"⚠️ Budget may exceed by ₱{overshoot:.2f}/day ({(overshoot/daily_budget_per_person)*100:.1f}%). Consider increasing budget if possible.")
        
        # ====================================================================
        # CHANGE 3: Check if allergies are very restrictive
        # ====================================================================
        if self.recipes_df is not None and len(self.recipes_df) > 0:
            total_original = len(self.recipes_df)
            recipes_remaining = len(available_recipes)
            restriction_percent = ((total_original - recipes_remaining) / total_original) * 100
            
            if restriction_percent > 70:
                # WARNING: Very restrictive allergies
                warnings.append(f"⚠️ Allergies removed {restriction_percent:.0f}% of recipes. Limited variety and higher costs expected.")
        
        # ====================================================================
        # Return combined message with all warnings
        # ====================================================================
        if warnings:
            warning_msg = "✅ Meal plan feasible with notes:\n" + "\n".join(warnings)
            return True, warning_msg
        else:
            return True, "✅ Meal plan is feasible"
    
    # ========================================================================
    # PHASE 3.6: GENERATE 7-DAY MEAL PLAN (IMPROVED WITH VALIDATION)
    # ========================================================================
    
    def generate_7day_meal_plan(self, daily_budget_per_person, allergies, household_size):
        """
        Generate complete 7-day meal plan with SMART COST DISTRIBUTION
        and MEAL TYPE VALIDATION
        
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
        
        # Step 3: Validate feasibility (OPTION C - includes warnings)
        is_feasible, message = self.validate_budget_feasibility(available, daily_budget_per_person)
        if not is_feasible:
            return None, 0.0, message
        
        # Step 4: Generate 7 days with SMART cost distribution and validation
        meal_plan = {}
        total_weekly_cost_per_person = 0.0
        
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        meal_types = ['Breakfast', 'Lunch', 'Dinner']
        
        for day_num in range(1, 8):
            day_name = days_of_week[day_num - 1]
            day_key = f"Day {day_num} ({day_name})"
            
            meals_for_day = {}
            day_total_per_person = 0.0
            
            # Select 3 meals for this day (with smart cost distribution and validation)
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
                        'recipe_id': int(selected_recipe['id']),
                        'meal_category': str(selected_recipe['meal_category'])
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
        
        return meal_plan, total_weekly_cost_per_person, message  # Return message (which may include warnings)
    
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
