# sigma_app/scripts/generate_seeding_csvs.py
"""
Generate CSV files for seeding Django with multiple sport preferences per user.
Source dataset: https://www.kaggle.com/datasets/andradaolteanu/socialmedia-profiles
"""

import os
import pandas as pd
import random
import secrets
from constants import CITY_CHOICES, SPORT_CHOICES, SKILL_CHOICES

# Set random seed for reproducibility
random.seed(42)

# Define output paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(DATA_DIR, exist_ok=True)

USERS_CSV_PATH = os.path.join(DATA_DIR, "users_seeding.csv")
SPORT_PREFS_CSV_PATH = os.path.join(DATA_DIR, "sport_preferences_seeding.csv")

# Read source CSV
SOURCE_PATH = os.path.join(DATA_DIR, "users.csv")
df_old = pd.read_csv(SOURCE_PATH)

# ========== GENERATE USERS CSV ==========
users_data = []

for _, row in df_old.iterrows():
    username = row["screen_name"]
    full_name = row["name"]

    email = f"{username}@example.com"
    password = secrets.token_urlsafe(10)  # Secure random password
    bio = f"Halo, saya {full_name}"
    city = random.choice(CITY_CHOICES)[0]
    profile_image_url = (
        "https://images.unsplash.com/photo-1759354001829-233b2025c6b2"
        "?q=80&w=687&auto=format&fit=crop"
    )
    total_points = 0
    total_events = 0

    users_data.append(
        {
            "username": username,
            "full_name": full_name,
            "email": email,
            "password": password,
            "bio": bio,
            "city": city,
            "profile_image_url": profile_image_url,
            "total_points": total_points,
            "total_events": total_events,
        }
    )

df_users = pd.DataFrame(users_data)
df_users.to_csv(USERS_CSV_PATH, index=False)
print(f"✓ Users CSV created: {USERS_CSV_PATH}")

# ========== GENERATE SPORT PREFERENCES CSV ==========
sport_preferences_data = []

for _, row in df_old.iterrows():
    username = row["screen_name"]

    # Each user has 1–3 unique sport preferences
    num_preferences = random.randint(1, 3)
    selected_sports = random.sample(SPORT_CHOICES, num_preferences)

    for sport_type, _ in selected_sports:  # Unpack (value, label)
        skill_level = random.choice(SKILL_CHOICES)[0]

        sport_preferences_data.append(
            {
                "username": username,
                "sport_type": sport_type,
                "skill_level": skill_level,
            }
        )

df_sport_prefs = pd.DataFrame(sport_preferences_data)
df_sport_prefs.to_csv(SPORT_PREFS_CSV_PATH, index=False)
print(f"✓ Sport preferences CSV created: {SPORT_PREFS_CSV_PATH}")

# ========== SUMMARY ==========
print("\n=== SUMMARY ===")
print(f"Total users: {len(df_users)}")
print(f"Total sport preferences: {len(df_sport_prefs)}")
print(f"Average preferences per user: {len(df_sport_prefs)/len(df_users):.2f}")