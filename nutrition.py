import pandas as pd
import streamlit as st

# Load datasets from Excel
@st.cache_data
def load_data():
    user_df = pd.read_csv("user_health_data.csv")
    food_df = pd.read_csv("food_data.csv")
    return user_df, food_df

user_df, food_df = load_data()

# --- Helper Functions ---
def calculate_bmr(weight, height, age, gender):
    if gender.lower() == 'male':
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161

def get_activity_multiplier(level):
    level = level.lower()
    if level == 'sedentary': return 1.2
    elif level == 'light': return 1.375
    elif level == 'moderate': return 1.55
    elif level == 'active': return 1.725
    elif level == 'very_active': return 1.9
    else: return 1.2

# --- Streamlit UI ---
st.title("AI-Powered Nutrition Recommender")
st.write("Get your daily calorie target and recommended foods based on your health profile.")

user_ids = user_df["user_id"].tolist()
selected_id = st.selectbox("Select your User ID", user_ids)

user = user_df[user_df["user_id"] == selected_id].iloc[0]

# Extract user info
age = int(user["age"])
height = float(user["height_cm"])
weight = float(user["weight_kg"])
gender = user["gender"]
activity = user["activity_level"]
diet_type = user["diet"]
goal = user["goal"]

# Calculate BMR and TDEE
bmr = calculate_bmr(weight, height, age, gender)
tdee = bmr * get_activity_multiplier(activity)

# Adjust TDEE based on goal
if goal == "weight_loss":
    target_calories = tdee - 300
elif goal == "muscle_gain":
    target_calories = tdee + 300
else:
    target_calories = tdee

st.subheader(" Your Daily Targets")
st.write(f"**Calories:** {int(target_calories)} kcal")
st.write(f"**Goal:** {goal.replace('_', ' ').title()}")

# Recommend foods
st.subheader(" Recommended Foods")
filtered_food = food_df[food_df["type"].str.lower().str.contains(diet_type.lower())]
recommended_foods = filtered_food[filtered_food["calories"] <= target_calories * 0.4]

if not recommended_foods.empty:
    st.dataframe(recommended_foods.reset_index(drop=True))
else:
    st.warning("No suitable foods found for your diet type and calorie target.")
