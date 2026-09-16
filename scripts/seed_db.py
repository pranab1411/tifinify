import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Ensure project root is in Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app import create_app
from app.models import db, User, Provider, ProviderSource, Review
from app.services.review_service import ReviewService


def seed_database():
    """Populate database with realistic demo providers and controlled review patterns."""
    app = create_app()
    with app.app_context():
        print("Creating all database tables...")
        db.create_all()

        # Check if already seeded
        if Provider.query.first():
            print("Database already contains provider records. Skipping seed.")
            return

        print("Seeding initial users...")
        # 1. Admin & Test User
        admin = User(name="Tifinify Administrator", email="admin@tifinify.com", role="admin")
        admin.set_password("Admin@123")
        db.session.add(admin)

        student = User(
            name="Rahul Sharma",
            email="rahul@tifinify.com",
            role="user",
            dietary_preference="veg",
            default_radius_km=5.0
        )
        student.set_password("Student@123")
        db.session.add(student)
        db.session.commit()

        print("Seeding demo providers...")
        # Coordinates centered around a student educational hub (e.g. Viman Nagar, Pune: 18.5679° N, 73.9143° E)
        center_lat = 18.5679
        center_lon = 73.9143

        providers_data = [
            {
                "name": "Annapurna Homely Tiffin Service",
                "slug": "annapurna-homely-tiffin",
                "category": "tiffin",
                "food_type": "veg",
                "meal_types": "lunch,dinner",
                "address": "Row House 4, Sakore Nagar, Viman Nagar, Pune",
                "locality": "Viman Nagar",
                "latitude": center_lat + 0.0035,
                "longitude": center_lon + 0.0020,
                "phone": "+91 98231 44510",
                "website": "https://annapurnatiffins.example.com",
                "opening_hours": "11:30 AM - 3:00 PM, 7:00 PM - 10:30 PM",
                "price_per_month": 2600,
                "price_per_meal": 90,
                "delivery_available": True,
                "pickup_available": True,
                "description": "Authentic North & South Indian pure vegetarian home-cooked meals. Freshly made rotis, dal, seasonal sabzi, and steamed rice.",
                "reviews": [
                    ("Amit Verma", 5.0, "The food tastes just like home. Roti is extremely soft and dal is flavorful without excess oil.", -20),
                    ("Pooja Nair", 4.5, "Very consistent hygiene and good portion quantity. Monthly subscription is worth every rupee.", -15),
                    ("Rohan Kulkarni", 4.0, "Great taste and healthy preparations. Delivery is usually on time, maybe 10 mins late on rainy days.", -10),
                    ("Sneha Joshi", 5.0, "Clean packaging and delicious homestyle taste. Truly dependable mess for college students.", -5),
                    ("Vikas Gupta", 4.5, "Best tiffin service in Viman Nagar. The food quality and hygiene have remained consistent for 6 months.", -2),
                ]
            },
            {
                "name": "Royal Star Mess & Catering",
                "slug": "royal-star-mess-catering",
                "category": "mess",
                "food_type": "both",
                "meal_types": "lunch,dinner",
                "address": "Shop 12, Dutta Mandir Chowk, Viman Nagar, Pune",
                "locality": "Viman Nagar",
                "latitude": center_lat - 0.0050,
                "longitude": center_lon + 0.0040,
                "phone": "+91 98900 11223",
                "website": None,
                "opening_hours": "12:00 PM - 3:30 PM, 7:30 PM - 11:00 PM",
                "price_per_month": 2200,
                "price_per_meal": 80,
                "delivery_available": True,
                "pickup_available": True,
                "description": "Budget-friendly student mess serving vegetarian and egg/chicken thalis.",
                # Controlled anomaly: Near-duplicate phrasing and marketing jargon
                "reviews": [
                    ("User101", 5.0, "Best tiffin service in Pune call now for guaranteed discounts. Royal Star mess is the ultimate best service in town guaranteed!", -1),
                    ("User102", 5.0, "Best tiffin service in Pune call now for guaranteed discounts. Royal Star mess is the ultimate best food in town guaranteed!", -1),
                    ("Rajesh M", 1.0, "Food was completely cold and found a hair in the dal. Worst unhygienic experience.", -12),
                    ("User103", 5.0, "Best tiffin service in town call now for guaranteed discount. Royal Star mess has super quality!", -1),
                    ("Deepak S", 1.0, "Extremely disappointed. Extremely delayed delivery and stale sabzi. Disgusting smell.", -8),
                ]
            },
            {
                "name": "Maa Ki Rasoi Pure Veg Mess",
                "slug": "maa-ki-rasoi-mess",
                "category": "both",
                "food_type": "jain_available",
                "meal_types": "lunch,dinner",
                "address": "Near Symbiosis College, Lane 3, Viman Nagar, Pune",
                "locality": "Viman Nagar",
                "latitude": center_lat + 0.0080,
                "longitude": center_lon - 0.0060,
                "phone": "+91 98505 67890",
                "website": "https://maakirasoi.example.com",
                "opening_hours": "11:00 AM - 3:00 PM, 6:30 PM - 10:00 PM",
                "price_per_month": 3000,
                "price_per_meal": 110,
                "delivery_available": True,
                "pickup_available": True,
                "description": "Pure vegetarian satvik food with separate Jain meals available upon request. High hygiene standards and eco-friendly steel tiffin delivery.",
                "reviews": [
                    ("Tanvi Deshmukh", 5.0, "Spotless hygiene and wholesome taste. The Jain meal option is authentic without onion or garlic.", -25),
                    ("Kunal Saxena", 4.0, "Price is slightly on the higher side, but the food quality and cleanliness justify the cost.", -18),
                    ("Aarav Mehta", 4.5, "Generous quantity and tasty homestyle sabzis. Packaging is very neat in insulated bags.", -11),
                    ("Simran Kaur", 5.0, "Excellent taste and very polite delivery rider. Food arrives piping hot every day.", -4),
                ]
            },
            {
                "name": "Bawarchi Tiffin Express",
                "slug": "bawarchi-tiffin-express",
                "category": "tiffin",
                "food_type": "both",
                "meal_types": "both",
                "address": "Kalyani Nagar Main Road, Pune",
                "locality": "Kalyani Nagar",
                "latitude": center_lat - 0.0150,
                "longitude": center_lon - 0.0120,
                "phone": "+91 97654 32100",
                "website": None,
                "opening_hours": "12:00 PM - 3:00 PM, 7:00 PM - 11:00 PM",
                "price_per_month": 2500,
                "price_per_meal": 95,
                "delivery_available": True,
                "pickup_available": False,
                "description": "Daily doorstep tiffin delivery catering to software professionals and college students in Kalyani Nagar & Viman Nagar.",
                "reviews": [
                    ("Gaurav Patil", 4.0, "Good value for money. Chicken thali on Wednesdays and Sundays is delicious.", -14),
                    ("Priya Menon", 2.0, "Delivery timing is unpredictable. Food is often late by 45 minutes on weekends.", -9),
                    ("Aniket Shinde", 4.5, "Decent quantity and flavorful taste. Pocket friendly monthly rates.", -3),
                ]
            },
            {
                "name": "Shree Ganesh Bhojanalay",
                "slug": "shree-ganesh-bhojanalay",
                "category": "mess",
                "food_type": "veg",
                "meal_types": "lunch,dinner",
                "address": "Behind Phoenix Mall, Clover Park, Viman Nagar, Pune",
                "locality": "Viman Nagar",
                "latitude": center_lat + 0.0120,
                "longitude": center_lon + 0.0150,
                "phone": "+91 98222 99881",
                "website": None,
                "opening_hours": "11:30 AM - 4:00 PM, 7:00 PM - 10:30 PM",
                "price_per_month": 2100,
                "price_per_meal": 75,
                "delivery_available": False,
                "pickup_available": True,
                "description": "Traditional unlimited Maharashtrian & North Indian thali dining hall with take-away dabba service.",
                "reviews": [
                    ("Sachin Kadam", 4.5, "Unlimited thali with hot bhakri and pitla. Authentic taste and very affordable price.", -30),
                    ("Neha Bansal", 4.0, "Simple and hearty food. Always crowded during lunch hours so arrive early.", -16),
                    ("Harish Rao", 4.0, "Great quantity for the price. Hygiene is decent for a traditional bhojanalay.", -7),
                ]
            }
        ]

        for p_info in providers_data:
            reviews = p_info.pop("reviews")
            provider = Provider(
                **p_info,
                is_demo=True,
                is_active=True,
            )
            db.session.add(provider)
            db.session.commit()

            # Record ProviderSource
            ps = ProviderSource(
                provider_id=provider.id,
                source_type="seed_demo",
                external_id=f"demo_{provider.slug}",
            )
            db.session.add(ps)
            db.session.commit()

            # Add reviews with specified relative dates
            now = datetime.utcnow()
            for r_name, r_rating, r_text, days_offset in reviews:
                r_date = now + timedelta(days=days_offset)
                ReviewService.add_review(
                    provider_id=provider.id,
                    rating=r_rating,
                    review_text=r_text,
                    reviewer_name=r_name,
                    source="demo",
                    review_date=r_date,
                )

        print("Database seeded successfully with 5 providers and realistic review profiles!")


if __name__ == "__main__":
    seed_database()
