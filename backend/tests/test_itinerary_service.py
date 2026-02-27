from itinerary_service import ItineraryService
from models import TripCreate, TripPreferences


def _sample_trip() -> TripCreate:
    return TripCreate(
        destination="Goa",
        start_date="2026-03-10",
        end_date="2026-03-13",
        budget=45000,
        travelers=2,
        preferences=TripPreferences(adventure=True, vegetarian=True),
    )


def test_parse_response_supports_markdown_json_block():
    service = object.__new__(ItineraryService)
    trip = _sample_trip()
    response = '{"destination":"Goa","duration_days":3,"daily_plans":[],"estimated_cost":40000,"hotels":[],"flights":[],"local_transport":[],"tips":[],"weather_info":"Clear","packing_list":[]}'

    parsed = service._parse_response(f"```json\n{response}\n```", trip)

    assert parsed["destination"] == "Goa"
    assert parsed["duration_days"] == 3


def test_parse_response_invalid_json_returns_fallback_data():
    service = object.__new__(ItineraryService)
    trip = _sample_trip()

    parsed = service._parse_response("not-json", trip)

    assert parsed["destination"] == "Goa"
    assert parsed["duration_days"] == 3
    assert len(parsed["daily_plans"]) == 3


def test_create_fallback_itinerary_builds_expected_day_count():
    service = object.__new__(ItineraryService)
    trip = _sample_trip()

    itinerary = service._create_fallback_itinerary(trip)

    assert itinerary.destination == "Goa"
    assert itinerary.duration_days == 3
    assert len(itinerary.daily_plans) == 3
