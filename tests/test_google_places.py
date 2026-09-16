import pytest
from app import create_app
from app.models import db, Provider, Review, ProviderSource
from app.integrations.google_places import GooglePlacesAdapter


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


def test_google_places_adapter_verified_places(app):
    with app.app_context():
        adapter = GooglePlacesAdapter(api_key="")
        assert adapter.is_configured() is False

        # Should retrieve verified real places from catalog around Viman Nagar, Pune
        places = adapter.search_nearby(18.5679, 73.9143, radius_meters=5000)
        assert len(places) > 0
        first = places[0]
        assert "external_id" in first
        assert "reviews" in first
        assert len(first["reviews"]) > 0

        # Ingest to database
        provider = adapter.ingest_to_database(first)
        assert provider is not None
        assert provider.id is not None
        assert provider.is_demo is False
        assert provider.review_trust_score > 0

        # ProviderSource created
        ps = ProviderSource.query.filter_by(provider_id=provider.id).first()
        assert ps is not None
        assert ps.source_type == "google_places"

        # Reviews added and analyzed
        reviews = Review.query.filter_by(provider_id=provider.id).all()
        assert len(reviews) == len(first["reviews"])


def test_google_places_sync_api(client, app):
    # Test sync endpoint
    res = client.post(
        "/api/v1/sync/google-places",
        json={"lat": 18.5679, "lng": 73.9143, "query": "Viman Nagar, Pune"},
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["count"] > 0
    assert len(data["data"]) > 0


def test_google_maps_key_config_api(client, app):
    # GET key status
    res = client.get("/api/v1/config/google-maps-key")
    assert res.status_code == 200
    data = res.get_json()
    assert "configured" in data

    # POST new key
    res = client.post(
        "/api/v1/config/google-maps-key",
        json={"api_key": "AIzaSyFakeTestKeyForTifinify1234567890"},
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["configured"] is True

    # Reset environment variable so it doesn't pollute subsequent test runs
    import os
    os.environ["GOOGLE_MAPS_API_KEY"] = ""
