import pytest
from app import create_app
from app.models import db, Provider, User
from app.services.review_service import ReviewService


@pytest.fixture
def client():
    app = create_app("testing")
    with app.app_context():
        db.create_all()

        # Seed test admin & test provider with reviews
        admin = User(name="Admin", email="admin@test.com", role="admin")
        admin.set_password("Admin@123")
        db.session.add(admin)

        p1 = Provider(
            name="Test Tiffin One",
            slug="test-tiffin-one",
            category="tiffin",
            food_type="veg",
            address="Street 1, Pune",
            locality="Viman Nagar",
            latitude=18.5679,
            longitude=73.9143,
            price_per_month=2400,
        )
        p2 = Provider(
            name="Test Mess Two",
            slug="test-mess-two",
            category="mess",
            food_type="both",
            address="Street 2, Pune",
            locality="Viman Nagar",
            latitude=18.5650,
            longitude=73.9120,
            price_per_month=2200,
        )
        db.session.add_all([p1, p2])
        db.session.commit()

        # Add reviews to p1
        ReviewService.add_review(
            provider_id=p1.id,
            rating=5.0,
            review_text="Amazing soft rotis and tasty dal. Hygienic packaging!",
            reviewer_name="Customer A",
        )
        ReviewService.add_review(
            provider_id=p1.id,
            rating=4.5,
            review_text="Good food quality, delivery is on time every single day.",
            reviewer_name="Customer B",
        )

        # Add reviews to p2
        ReviewService.add_review(
            provider_id=p2.id,
            rating=5.0,
            review_text="Best service call now 9890000000 for discount.",
            reviewer_name="Promo 1",
        )
        ReviewService.add_review(
            provider_id=p2.id,
            rating=5.0,
            review_text="Best service call now 9890000000 for discount.",
            reviewer_name="Promo 2",
        )

        with app.test_client() as test_client:
            yield test_client

        db.session.remove()
        db.drop_all()


def test_landing_page(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"Tifinify" in res.data
    assert b"Find food nearby" in res.data


def test_about_page(client):
    res = client.get("/about")
    assert res.status_code == 200
    assert b"Review Trust Analysis" in res.data


def test_discovery_page(client):
    res = client.get("/providers/discovery?location=Viman+Nagar&radius=5")
    assert res.status_code == 200
    assert b"Test Tiffin One" in res.data
    assert b"Test Mess Two" in res.data


def test_provider_details_page(client):
    res = client.get("/providers/1")
    assert res.status_code == 200
    assert b"Test Tiffin One" in res.data
    assert b"Review Trust" in res.data
    assert b"AI Review Intelligence" in res.data


def test_provider_comparison_page(client):
    res = client.get("/providers/compare?p1=1&p2=2")
    assert res.status_code == 200
    assert b"Test Tiffin One" in res.data
    assert b"Test Mess Two" in res.data
    assert b"Side-by-Side Provider Comparison" in res.data


def test_api_providers(client):
    res = client.get("/api/v1/providers?lat=18.5679&lng=73.9143&radius=5")
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["status"] == "success"
    assert json_data["count"] == 2


def test_auth_and_review_submission(client):
    # 1. Register new user
    reg_res = client.post("/auth/register", data={
        "name": "New Student",
        "email": "newstudent@test.com",
        "password": "Password@123",
        "dietary_preference": "veg",
    }, follow_redirects=True)
    assert reg_res.status_code == 200
    assert b"Welcome to Tifinify" in reg_res.data

    # 2. Submit a review for provider 1
    review_res = client.post("/reviews/1/new", data={
        "rating": "4.0",
        "review_text": "Clean homestyle food, generous quantity and warm delivery.",
        "reviewer_name": "New Student",
    }, follow_redirects=True)
    assert review_res.status_code == 200
    assert b"Your review has been submitted" in review_res.data
