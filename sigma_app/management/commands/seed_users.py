# sigma_app/management/commands/seed_users.py

import os
import pandas as pd
from django.conf import settings
from django.db import transaction
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from authentication.models import UserProfile, SportPreference


class Command(BaseCommand):
    help = "Seed users, profiles, and sport preferences from generated CSV files"

    def handle(self, *args, **kwargs):
        users_path = os.path.join(settings.BASE_DIR, "sigma_app", "data", "users_seeding.csv")
        sports_path = os.path.join(settings.BASE_DIR, "sigma_app", "data", "sport_preferences_seeding.csv")

        users_df = pd.read_csv(users_path)
        sports_df = pd.read_csv(sports_path)

        self.stdout.write(self.style.SUCCESS("Seeding users..."))

        with transaction.atomic():
            for _, row in users_df.iterrows():
                if pd.isna(row["username"]) or pd.isna(row["email"]):
                    self.stdout.write(self.style.WARNING(f"⚠️ Skipping invalid row: {row}"))
                    continue

                user, created = User.objects.get_or_create(
                    username=row["username"],
                    defaults={
                        "email": row["email"],
                        "first_name": row["full_name"].split()[0],
                        "last_name": " ".join(row["full_name"].split()[1:]),
                    },
                )

                if created:
                    user.set_password(row["password"])
                    user.save()

                    profile, _ = UserProfile.objects.get_or_create(user=user)
                    profile.full_name = row["full_name"]
                    profile.bio = row["bio"]
                    profile.city = row["city"]
                    profile.profile_image_url = row.get("profile_image_url", "")
                    profile.total_points = int(row["total_points"])
                    profile.total_events = int(row["total_events"])
                    profile.save()

                    self.stdout.write(f"Created: {row['username']}")
                else:
                    self.stdout.write(f"Skipped existing user: {row['username']}")

            self.stdout.write(self.style.SUCCESS("\nSeeding sport preferences..."))

            for _, row in sports_df.iterrows():
                user = User.objects.filter(username=row["username"]).first()
                if not user:
                    self.stdout.write(self.style.WARNING(f"User {row['username']} not found, skipping."))
                    continue

                SportPreference.objects.get_or_create(
                    user=user,
                    sport_type=row["sport_type"],
                    defaults={"skill_level": row["skill_level"]},
                )

        self.stdout.write(self.style.SUCCESS("✅ Done seeding all users and sport preferences."))