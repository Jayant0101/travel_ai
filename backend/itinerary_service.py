import os
import json
import logging
from typing import Dict, Any
from models import TripCreate, Itinerary

logger = logging.getLogger(__name__)

class ItineraryService:
    def __init__(self):
        self.api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
    
    async def generate_itinerary(self, trip_data: TripCreate) -> Itinerary:
        """Generate travel itinerary using Gemini AI"""
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            
            # Create system message for travel planning
            system_message = """You are an expert travel planner AI. Generate detailed, personalized travel itineraries based on user preferences. 
            Always respond with valid JSON in the exact format specified. Include realistic prices, activities, and recommendations."""
            
            # Create chat instance with Gemini
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"trip_{trip_data.destination}",
                system_message=system_message
            ).with_model("gemini", "gemini-2.5-flash")
            
            # Build the prompt
            prompt = self._build_prompt(trip_data)
            
            # Send message to Gemini
            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            logger.info(f"Gemini response received: {response[:200]}...")
            
            # Parse response
            itinerary_data = self._parse_response(response, trip_data)
            
            return Itinerary(**itinerary_data)
            
        except Exception as e:
            logger.error(f"Error generating itinerary: {str(e)}")
            # Return a fallback itinerary
            return self._create_fallback_itinerary(trip_data)
    
    def _build_prompt(self, trip_data: TripCreate) -> str:
        """Build detailed prompt for Gemini"""
        prefs = []
        if trip_data.preferences.adventure:
            prefs.append("adventure activities")
        if trip_data.preferences.family_friendly:
            prefs.append("family-friendly")
        if trip_data.preferences.vegetarian:
            prefs.append("vegetarian food options")
        if trip_data.preferences.budget_conscious:
            prefs.append("budget-conscious")
        if trip_data.preferences.luxury:
            prefs.append("luxury experiences")
        
        preferences_text = ", ".join(prefs) if prefs else "general tourist activities"
        
        prompt = f"""Create a detailed {(datetime.strptime(trip_data.end_date, '%Y-%m-%d') - datetime.strptime(trip_data.start_date, '%Y-%m-%d')).days}-day travel itinerary for {trip_data.destination}.

Trip Details:
- Destination: {trip_data.destination}
- Dates: {trip_data.start_date} to {trip_data.end_date}
- Number of travelers: {trip_data.travelers}
- Total budget: ₹{trip_data.budget:,.0f}
- Preferences: {preferences_text}

Provide a comprehensive JSON response with the following structure:
{{
  "destination": "{trip_data.destination}",
  "duration_days": {(datetime.strptime(trip_data.end_date, '%Y-%m-%d') - datetime.strptime(trip_data.start_date, '%Y-%m-%d')).days},
  "daily_plans": [
    {{
      "day": 1,
      "date": "{trip_data.start_date}",
      "title": "Day title",
      "description": "What to expect this day",
      "activities": ["Activity 1", "Activity 2", "Activity 3"],
      "meals": [
        {{"type": "breakfast", "suggestion": "Restaurant name and dish", "cost": "₹500"}},
        {{"type": "lunch", "suggestion": "Restaurant name", "cost": "₹800"}},
        {{"type": "dinner", "suggestion": "Restaurant name", "cost": "₹1000"}}
      ],
      "accommodation": {{"name": "Hotel name", "type": "Hotel", "cost": "₹3000"}}
    }}
  ],
  "estimated_cost": 50000,
  "hotels": [
    {{"name": "Hotel Luxury", "rating": 4.5, "price_per_night": 5000, "amenities": ["Pool", "Spa"], "location": "City Center"}},
    {{"name": "Budget Inn", "rating": 3.5, "price_per_night": 2000, "amenities": ["WiFi"], "location": "Near Station"}},
    {{"name": "Mid-Range Hotel", "rating": 4.0, "price_per_night": 3500, "amenities": ["Restaurant", "WiFi"], "location": "Tourist Area"}}
  ],
  "flights": [
    {{"airline": "IndiGo", "route": "Delhi to Nearest Airport", "price": 4500, "duration": "2h", "departure": "08:00", "arrival": "10:00"}}
  ],
  "local_transport": [
    {{"type": "Taxi", "description": "Airport to Hotel", "cost": 1200}},
    {{"type": "Rental Car", "description": "Daily rental", "cost": 2000}}
  ],
  "tips": ["Tip 1", "Tip 2", "Tip 3", "Tip 4", "Tip 5"],
  "weather_info": "Expected weather during travel dates",
  "packing_list": ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]
}}

IMPORTANT: Respond ONLY with valid JSON. No markdown, no code blocks, just pure JSON."""
        
        return prompt
    
    def _parse_response(self, response: str, trip_data: TripCreate) -> Dict[str, Any]:
        """Parse Gemini response and extract JSON"""
        try:
            # Try to parse as direct JSON
            response = response.strip()
            
            # Remove markdown code blocks if present
            if response.startswith("```json"):
                response = response[7:]
            elif response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            response = response.strip()
            
            # Parse JSON
            data = json.loads(response)
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(f"Response was: {response[:500]}")
            # Return fallback
            return self._create_fallback_itinerary(trip_data).model_dump()
    
    def _create_fallback_itinerary(self, trip_data: TripCreate) -> Itinerary:
        """Create a basic fallback itinerary if AI fails"""
        from datetime import datetime, timedelta
        
        start = datetime.strptime(trip_data.start_date, "%Y-%m-%d")
        end = datetime.strptime(trip_data.end_date, "%Y-%m-%d")
        days = (end - start).days
        
        daily_plans = []
        for i in range(days):
            current_date = start + timedelta(days=i)
            daily_plans.append({
                "day": i + 1,
                "date": current_date.strftime("%Y-%m-%d"),
                "title": f"Day {i + 1} - Explore {trip_data.destination}",
                "description": f"Discover the highlights of {trip_data.destination}",
                "activities": [
                    "Visit local attractions",
                    "Try local cuisine",
                    "Explore markets and shopping areas"
                ],
                "meals": [
                    {"type": "breakfast", "suggestion": "Hotel breakfast", "cost": "₹500"},
                    {"type": "lunch", "suggestion": "Local restaurant", "cost": "₹800"},
                    {"type": "dinner", "suggestion": "Popular dining spot", "cost": "₹1200"}
                ],
                "accommodation": {"name": "Recommended Hotel", "type": "Hotel", "cost": "₹3000"}
            })
        
        return Itinerary(
            destination=trip_data.destination,
            duration_days=days,
            daily_plans=daily_plans,
            estimated_cost=trip_data.budget * 0.9,
            hotels=[
                {"name": "Luxury Stay", "rating": 4.5, "price_per_night": 5000, "amenities": ["Pool", "Spa", "Restaurant"], "location": "City Center"},
                {"name": "Mid-Range Hotel", "rating": 4.0, "price_per_night": 3000, "amenities": ["WiFi", "Restaurant"], "location": "Tourist Area"},
                {"name": "Budget Inn", "rating": 3.5, "price_per_night": 1500, "amenities": ["WiFi"], "location": "Near Station"}
            ],
            flights=[
                {"airline": "IndiGo", "route": f"Delhi to {trip_data.destination}", "price": 4500, "duration": "2-3h", "departure": "08:00", "arrival": "10:30"}
            ],
            local_transport=[
                {"type": "Taxi", "description": "Airport transfers", "cost": 1200},
                {"type": "Local transport", "description": "Daily commute", "cost": 500}
            ],
            tips=[
                f"Best time to visit {trip_data.destination}",
                "Carry cash for small purchases",
                "Book attractions in advance",
                "Try local specialties",
                "Respect local customs"
            ],
            weather_info=f"Pleasant weather expected in {trip_data.destination}",
            packing_list=["Comfortable shoes", "Light clothing", "Sunscreen", "Camera", "Power bank", "Travel adapter", "Medications", "Toiletries"]
        )

from datetime import datetime