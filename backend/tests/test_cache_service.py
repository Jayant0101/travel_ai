import asyncio

from cache_service import CacheService


def test_make_itinerary_key_is_deterministic_for_equivalent_inputs():
    key_a = CacheService.make_itinerary_key(
        destination="  Goa ",
        days=4,
        budget=52000.0,
        preferences={"family_friendly": True, "vegetarian": False, "adventure": True},
    )
    key_b = CacheService.make_itinerary_key(
        destination="goa",
        days=4,
        budget=54999.0,
        preferences={"adventure": True, "family_friendly": True, "vegetarian": False},
    )

    assert key_a == key_b
    assert key_a.startswith("itinerary:")


def test_disconnected_cache_gracefully_returns_defaults():
    cache = CacheService()

    assert cache.is_connected is False
    assert asyncio.run(cache.get("missing")) is None
    assert asyncio.run(cache.increment("rate-limit")) == 0
    assert asyncio.run(cache.health()) == {"status": "disconnected", "backend": "none"}
