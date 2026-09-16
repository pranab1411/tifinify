import pytest
from app import create_app
from app.models import db, Provider
from app.services.provider_service import ProviderService


@pytest.fixture
def app_instance():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        # Add two test providers
        p1 = Provider(
            name="Alpha Tiffin",
            slug="alpha-tiffin",
            category="tiffin",
            food_type="veg",
            address="Viman Nagar, Pune",
            locality="Viman Nagar",
            latitude=18.5679,
            longitude=73.9143,
            source_rating=4.5,
            review_trust_score=92,
            trust_badge="likely_authentic",
            price_per_month=2500,
        )
        p2 = Provider(
            name="Beta Mess",
            slug="beta-mess",
            category="mess",
            food_type="both",
            address="Kalyani Nagar, Pune",
            locality="Kalyani Nagar",
            latitude=18.5500,
            longitude=73.9000,
            source_rating=3.8,
            review_trust_score=65,
            trust_badge="potentially_suspicious",
            price_per_month=2200,
        )
        db.session.add_all([p1, p2])
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


def test_provider_search_and_filters(app_instance):
    with app_instance.app_context():
        # Search all
        results = ProviderService.search_providers()
        assert len(results) == 2

        # Search category tiffin
        tiffin_results = ProviderService.search_providers(category="tiffin")
        assert len(tiffin_results) == 1
        assert tiffin_results[0]["name"] == "Alpha Tiffin"

        # Search veg food
        veg_results = ProviderService.search_providers(food_type="veg")
        assert len(veg_results) == 1
        assert veg_results[0]["name"] == "Alpha Tiffin"

        # Search with min trust score 80
        high_trust = ProviderService.search_providers(min_trust_score=80)
        assert len(high_trust) == 1
        assert high_trust[0]["name"] == "Alpha Tiffin"


def test_provider_comparison(app_instance):
    with app_instance.app_context():
        p1 = Provider.query.filter_by(slug="alpha-tiffin").first()
        p2 = Provider.query.filter_by(slug="beta-mess").first()

        comp = ProviderService.compare_providers(p1.id, p2.id, user_lat=18.5679, user_lon=73.9143)
        assert "provider1" in comp
        assert "provider2" in comp
        assert comp["provider1"]["name"] == "Alpha Tiffin"
        assert comp["provider2"]["name"] == "Beta Mess"
        assert len(comp["aspect_comparison"]) == 6
