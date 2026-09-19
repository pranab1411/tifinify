import pytest
from app import create_app
from app.models import db, Provider, Review, ProviderSource
from app.integrations.gemini_places import GeminiPlacesAdapter


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_gemini_places_adapter_discovery_and_ingestion(app):
    with app.app_context():
        adapter = GeminiPlacesAdapter(api_key="")
        
        # Discover places around Koramangala, Bengaluru
        places = adapter.discover_places(
            location_name="Koramangala, Bengaluru",
            lat=12.9352,
            lng=77.6245,
            count=3
        )

        assert len(places) > 0
        first = places[0]
        assert "name" in first
        assert "latitude" in first
        assert "longitude" in first
        assert "reviews" in first
        assert len(first["reviews"]) > 0

        # Ingest to database
        provider = adapter.ingest_to_database(first)
        assert provider is not None
        assert provider.id is not None
        assert provider.review_trust_score > 0
        assert provider.trust_badge in ("likely_authentic", "potentially_suspicious", "highly_suspicious")

        # ProviderSource created
        ps = ProviderSource.query.filter_by(provider_id=provider.id).first()
        assert ps is not None
        assert ps.source_type == "gemini_discovery"

        # Reviews added and analyzed
        reviews = Review.query.filter_by(provider_id=provider.id).all()
        assert len(reviews) == len(first["reviews"])


def test_gemini_places_sync_api(client, app):
    # Test POST /api/v1/sync/gemini-places
    res = client.post(
        "/api/v1/sync/gemini-places",
        json={
            "lat": 18.5204,
            "lng": 73.8567,
            "location_name": "Shivaji Nagar, Pune",
            "count": 3,
        },
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["count"] > 0
    assert len(data["data"]) > 0
    assert "name" in data["data"][0]


def test_gemini_places_sync_missing_params(client, app):
    # Test POST without lat/lng
    res = client.post("/api/v1/sync/gemini-places", json={})
    assert res.status_code == 400
    data = res.get_json()
    assert data["status"] == "error"


def test_web_search_places_adapter_and_sync(client, app):
    from app.integrations.web_search_places import WebSearchPlacesAdapter
    with app.app_context():
        adapter = WebSearchPlacesAdapter()
        sample_place = {
            "name": "Shree Ram Mess & Tiffin Service",
            "category": "mess",
            "food_type": "veg",
            "address": "Opposite Engineering College, Ranjhi",
            "locality": "Ranjhi",
            "city": "Jabalpur",
            "latitude": 23.1815,
            "longitude": 79.9864,
            "phone": "+91 98260 11223",
            "price_per_month": 2400,
            "price_per_meal": 80,
            "reviews": [
                {
                    "reviewer_name": "Rohan Patel",
                    "rating": 4.5,
                    "text": "Tasty hot rotis and very hygienic packaging. Great for students.",
                },
                {
                    "reviewer_name": "Pooja Verma",
                    "rating": 5.0,
                    "text": "Affordable monthly mess service with authentic home taste.",
                },
            ],
        }
        
        provider = adapter.ingest_to_database(sample_place)
        assert provider is not None
        assert provider.id is not None
        assert provider.review_trust_score > 0
        assert provider.name == "Shree Ram Mess & Tiffin Service"

    # Test POST /api/v1/sync/real-places
    res = client.post(
        "/api/v1/sync/real-places",
        json={
            "lat": 23.1815,
            "lng": 79.9864,
            "location_name": "JEC Ranjhi, Jabalpur",
            "mode": "google_web",
            "count": 2,
        },
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "count" in data


def test_gemini_key_config_api(client, app):
    # GET key config
    res_get = client.get("/api/v1/config/gemini-key")
    assert res_get.status_code == 200
    data_get = res_get.get_json()
    assert data_get["status"] == "success"
    assert "configured" in data_get

    # POST invalid short key (< 10 chars) returns 400
    res_short = client.post("/api/v1/config/gemini-key", json={"api_key": "short"})
    assert res_short.status_code == 400
    assert res_short.get_json()["status"] == "error"

    # POST clearing key ("") returns 200 with configured: False
    res_clear = client.post("/api/v1/config/gemini-key", json={"api_key": ""})
    assert res_clear.status_code == 200
    assert res_clear.get_json()["configured"] is False


