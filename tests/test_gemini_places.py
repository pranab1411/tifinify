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
