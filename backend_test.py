#!/usr/bin/env python3
"""
Comprehensive Backend Testing for AI Travel Booking Agent
Tests all backend APIs according to the test plan in test_result.md
"""

import requests
import json
import sys
import os
from datetime import datetime, timedelta

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except FileNotFoundError:
        pass
    return "http://localhost:8001"

BASE_URL = get_backend_url() + "/api"
print(f"Testing backend at: {BASE_URL}")

class BackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.trip_id = None
        self.order_id = None
        
        # Test data
        self.test_user = {
            "email": "test@example.com",
            "password": "Test123!",
            "full_name": "Test User",
            "phone": "+91-9876543210"
        }
        
        self.test_trip = {
            "destination": "Shimla",
            "start_date": "2025-12-20",
            "end_date": "2025-12-25",
            "budget": 75000,
            "travelers": 3,
            "preferences": {
                "adventure": True,
                "family_friendly": True,
                "vegetarian": True,
                "budget_conscious": False,
                "luxury": False
            }
        }
        
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        status_symbol = "✅" if status == "PASS" else "❌"
        print(f"{status_symbol} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        print()
        
    def make_request(self, method, endpoint, data=None, headers=None):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        # Add auth header if token exists
        if self.auth_token and headers is None:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
        elif self.auth_token and headers:
            headers["Authorization"] = f"Bearer {self.auth_token}"
            
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            return None
    
    def test_health_check(self):
        """Test basic health endpoints"""
        print("=== HEALTH CHECK TESTS ===")
        
        # Test root endpoint
        response = self.make_request("GET", "/")
        if response and response.status_code == 200:
            data = response.json()
            if "message" in data and "AI Travel Booking Agent" in data["message"]:
                self.log_test("Root endpoint", "PASS", f"Response: {data}")
            else:
                self.log_test("Root endpoint", "FAIL", f"Unexpected response: {data}")
        else:
            self.log_test("Root endpoint", "FAIL", f"Status: {response.status_code if response else 'No response'}")
        
        # Test health endpoint
        response = self.make_request("GET", "/health")
        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                self.log_test("Health endpoint", "PASS", f"Response: {data}")
            else:
                self.log_test("Health endpoint", "FAIL", f"Unhealthy status: {data}")
        else:
            self.log_test("Health endpoint", "FAIL", f"Status: {response.status_code if response else 'No response'}")
    
    def test_user_registration(self):
        """Test user registration"""
        print("=== USER REGISTRATION TEST ===")
        
        response = self.make_request("POST", "/auth/register", self.test_user)
        
        if response and response.status_code == 200:
            data = response.json()
            
            # Check required fields
            required_fields = ["access_token", "refresh_token", "user"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                self.auth_token = data["access_token"]
                self.user_id = data["user"]["id"]
                
                # Validate user data
                user_data = data["user"]
                if (user_data["email"] == self.test_user["email"] and 
                    user_data["full_name"] == self.test_user["full_name"]):
                    self.log_test("User Registration", "PASS", 
                                f"User created with ID: {self.user_id}")
                else:
                    self.log_test("User Registration", "FAIL", 
                                "User data mismatch in response")
            else:
                self.log_test("User Registration", "FAIL", 
                            f"Missing fields: {missing_fields}")
        else:
            status_code = response.status_code if response else "No response"
            error_detail = response.json().get("detail", "Unknown error") if response else "Connection failed"
            self.log_test("User Registration", "FAIL", 
                        f"Status: {status_code}, Error: {error_detail}")
    
    def test_user_login(self):
        """Test user login"""
        print("=== USER LOGIN TEST ===")
        
        login_data = {
            "email": self.test_user["email"],
            "password": self.test_user["password"]
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        
        if response and response.status_code == 200:
            data = response.json()
            
            if "access_token" in data and "user" in data:
                # Update token (in case we're testing login separately)
                self.auth_token = data["access_token"]
                self.log_test("User Login", "PASS", 
                            f"Login successful, token received")
            else:
                self.log_test("User Login", "FAIL", 
                            "Missing token or user data in response")
        else:
            status_code = response.status_code if response else "No response"
            error_detail = response.json().get("detail", "Unknown error") if response else "Connection failed"
            self.log_test("User Login", "FAIL", 
                        f"Status: {status_code}, Error: {error_detail}")
    
    def test_auth_me(self):
        """Test /auth/me endpoint"""
        print("=== AUTH ME TEST ===")
        
        if not self.auth_token:
            self.log_test("Auth Me", "FAIL", "No auth token available")
            return
            
        response = self.make_request("GET", "/auth/me")
        
        if response and response.status_code == 200:
            data = response.json()
            
            if (data.get("email") == self.test_user["email"] and 
                data.get("full_name") == self.test_user["full_name"]):
                self.log_test("Auth Me", "PASS", 
                            f"User info retrieved correctly")
            else:
                self.log_test("Auth Me", "FAIL", 
                            f"User data mismatch: {data}")
        else:
            status_code = response.status_code if response else "No response"
            error_detail = response.json().get("detail", "Unknown error") if response else "Connection failed"
            self.log_test("Auth Me", "FAIL", 
                        f"Status: {status_code}, Error: {error_detail}")
    
    def test_trip_generation(self):
        """Test AI trip generation"""
        print("=== AI TRIP GENERATION TEST ===")
        
        if not self.auth_token:
            self.log_test("Trip Generation", "FAIL", "No auth token available")
            return
            
        response = self.make_request("POST", "/trips/generate", self.test_trip)
        
        if response and response.status_code == 200:
            data = response.json()
            
            # Check required trip fields
            required_fields = ["id", "destination", "itinerary", "status"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                self.trip_id = data["id"]
                
                # Validate itinerary structure
                itinerary = data.get("itinerary", {})
                itinerary_fields = ["daily_plans", "hotels", "flights", "tips", "packing_list", "estimated_cost"]
                missing_itinerary = [field for field in itinerary_fields if field not in itinerary]
                
                if not missing_itinerary:
                    # Check if daily plans exist and have proper structure
                    daily_plans = itinerary.get("daily_plans", [])
                    if daily_plans and len(daily_plans) > 0:
                        # Check estimated cost is within budget
                        estimated_cost = itinerary.get("estimated_cost", 0)
                        if estimated_cost <= self.test_trip["budget"]:
                            self.log_test("Trip Generation", "PASS", 
                                        f"Trip created with ID: {self.trip_id}, "
                                        f"Cost: ₹{estimated_cost:,.0f}, "
                                        f"Days: {len(daily_plans)}")
                        else:
                            self.log_test("Trip Generation", "FAIL", 
                                        f"Estimated cost (₹{estimated_cost:,.0f}) exceeds budget (₹{self.test_trip['budget']:,.0f})")
                    else:
                        self.log_test("Trip Generation", "FAIL", 
                                    "No daily plans generated")
                else:
                    self.log_test("Trip Generation", "FAIL", 
                                f"Missing itinerary fields: {missing_itinerary}")
            else:
                self.log_test("Trip Generation", "FAIL", 
                            f"Missing trip fields: {missing_fields}")
        else:
            status_code = response.status_code if response else "No response"
            error_detail = response.json().get("detail", "Unknown error") if response else "Connection failed"
            self.log_test("Trip Generation", "FAIL", 
                        f"Status: {status_code}, Error: {error_detail}")
    
    def test_get_trips(self):
        """Test getting all user trips"""
        print("=== GET TRIPS TEST ===")
        
        if not self.auth_token:
            self.log_test("Get Trips", "FAIL", "No auth token available")
            return
            
        response = self.make_request("GET", "/trips")
        
        if response and response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list):
                if len(data) > 0:
                    # Check if our created trip is in the list
                    trip_found = any(trip.get("id") == self.trip_id for trip in data)
                    if trip_found:
                        self.log_test("Get Trips", "PASS", 
                                    f"Retrieved {len(data)} trips, including our test trip")
                    else:
                        self.log_test("Get Trips", "FAIL", 
                                    f"Test trip not found in {len(data)} trips")
                else:
                    self.log_test("Get Trips", "PASS", "No trips found (empty list)")
            else:
                self.log_test("Get Trips", "FAIL", 
                            f"Expected list, got: {type(data)}")
        else:
            status_code = response.status_code if response else "No response"
            error_detail = response.json().get("detail", "Unknown error") if response else "Connection failed"
            self.log_test("Get Trips", "FAIL", 
                        f"Status: {status_code}, Error: {error_detail}")
    
    def test_get_specific_trip(self):
        """Test getting specific trip by ID"""
        print("=== GET SPECIFIC TRIP TEST ===")
        
        if not self.auth_token or not self.trip_id:
            self.log_test("Get Specific Trip", "FAIL", "No auth token or trip ID available")
            return
            
        response = self.make_request("GET", f"/trips/{self.trip_id}")
        
        if response and response.status_code == 200:
            data = response.json()
            
            if data.get("id") == self.trip_id and data.get("destination") == self.test_trip["destination"]:
                self.log_test("Get Specific Trip", "PASS", 
                            f"Retrieved trip: {data.get('destination')}")
            else:
                self.log_test("Get Specific Trip", "FAIL", 
                            "Trip data mismatch")
        else:
            status_code = response.status_code if response else "No response"
            error_detail = response.json().get("detail", "Unknown error") if response else "Connection failed"
            self.log_test("Get Specific Trip", "FAIL", 
                        f"Status: {status_code}, Error: {error_detail}")
    
    def test_confirm_trip(self):
        """Test trip confirmation"""
        print("=== TRIP CONFIRMATION TEST ===")
        
        if not self.auth_token or not self.trip_id:
            self.log_test("Trip Confirmation", "FAIL", "No auth token or trip ID available")
            return
            
        response = self.make_request("PUT", f"/trips/{self.trip_id}/confirm")
        
        if response and response.status_code == 200:
            data = response.json()
            
            if "message" in data and "confirmed" in data["message"]:
                # Verify trip status changed
                verify_response = self.make_request("GET", f"/trips/{self.trip_id}")
                if verify_response and verify_response.status_code == 200:
                    trip_data = verify_response.json()
                    if trip_data.get("status") == "confirmed":
                        self.log_test("Trip Confirmation", "PASS", 
                                    "Trip status updated to confirmed")
                    else:
                        self.log_test("Trip Confirmation", "FAIL", 
                                    f"Status not updated, current: {trip_data.get('status')}")
                else:
                    self.log_test("Trip Confirmation", "FAIL", 
                                "Could not verify status change")
            else:
                self.log_test("Trip Confirmation", "FAIL", 
                            f"Unexpected response: {data}")
        else:
            status_code = response.status_code if response else "No response"
            error_detail = response.json().get("detail", "Unknown error") if response else "Connection failed"
            self.log_test("Trip Confirmation", "FAIL", 
                        f"Status: {status_code}, Error: {error_detail}")
    
    def test_payment_creation(self):
        """Test payment order creation"""
        print("=== PAYMENT ORDER CREATION TEST ===")
        
        if not self.auth_token or not self.trip_id:
            self.log_test("Payment Creation", "FAIL", "No auth token or trip ID available")
            return
            
        payment_data = {
            "trip_id": self.trip_id,
            "amount": 50000.0
        }
        
        response = self.make_request("POST", "/payments/create", payment_data)
        
        if response and response.status_code == 200:
            data = response.json()
            
            required_fields = ["order_id", "amount", "currency", "status"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                self.order_id = data["order_id"]
                if data["status"] == "created" and data["amount"] == payment_data["amount"]:
                    self.log_test("Payment Creation", "PASS", 
                                f"Payment order created: {self.order_id}")
                else:
                    self.log_test("Payment Creation", "FAIL", 
                                f"Invalid payment data: {data}")
            else:
                self.log_test("Payment Creation", "FAIL", 
                            f"Missing fields: {missing_fields}")
        else:
            status_code = response.status_code if response else "No response"
            error_detail = response.json().get("detail", "Unknown error") if response else "Connection failed"
            self.log_test("Payment Creation", "FAIL", 
                        f"Status: {status_code}, Error: {error_detail}")
    
    def test_payment_verification(self):
        """Test payment verification"""
        print("=== PAYMENT VERIFICATION TEST ===")
        
        if not self.auth_token or not self.order_id or not self.trip_id:
            self.log_test("Payment Verification", "FAIL", "Missing required data")
            return
            
        # Mock payment verification data
        verify_data = {
            "payment_id": f"pay_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "order_id": self.order_id,
            "signature": "mock_signature_12345",
            "trip_id": self.trip_id
        }
        
        response = self.make_request("POST", "/payments/verify", verify_data)
        
        if response and response.status_code == 200:
            data = response.json()
            
            if data.get("status") == "completed":
                # Verify trip status changed to confirmed
                verify_response = self.make_request("GET", f"/trips/{self.trip_id}")
                if verify_response and verify_response.status_code == 200:
                    trip_data = verify_response.json()
                    if trip_data.get("status") == "confirmed":
                        self.log_test("Payment Verification", "PASS", 
                                    "Payment verified and trip confirmed")
                    else:
                        self.log_test("Payment Verification", "FAIL", 
                                    f"Trip status not updated: {trip_data.get('status')}")
                else:
                    self.log_test("Payment Verification", "FAIL", 
                                "Could not verify trip status")
            else:
                self.log_test("Payment Verification", "FAIL", 
                            f"Payment not completed: {data}")
        else:
            status_code = response.status_code if response else "No response"
            error_detail = response.json().get("detail", "Unknown error") if response else "Connection failed"
            self.log_test("Payment Verification", "FAIL", 
                        f"Status: {status_code}, Error: {error_detail}")
    
    def test_data_persistence(self):
        """Test data persistence by retrieving data again"""
        print("=== DATA PERSISTENCE TEST ===")
        
        if not self.auth_token:
            self.log_test("Data Persistence", "FAIL", "No auth token available")
            return
            
        # Test user data persistence
        user_response = self.make_request("GET", "/auth/me")
        user_ok = (user_response and user_response.status_code == 200 and 
                  user_response.json().get("email") == self.test_user["email"])
        
        # Test trip data persistence
        trips_response = self.make_request("GET", "/trips")
        trips_ok = (trips_response and trips_response.status_code == 200 and 
                   len(trips_response.json()) > 0)
        
        # Test specific trip persistence
        if self.trip_id:
            trip_response = self.make_request("GET", f"/trips/{self.trip_id}")
            trip_ok = (trip_response and trip_response.status_code == 200 and 
                      trip_response.json().get("user_id") == self.user_id)
        else:
            trip_ok = False
            
        if user_ok and trips_ok and trip_ok:
            self.log_test("Data Persistence", "PASS", 
                        "All data persisted correctly in MongoDB")
        else:
            issues = []
            if not user_ok: issues.append("user data")
            if not trips_ok: issues.append("trips data")
            if not trip_ok: issues.append("specific trip data")
            self.log_test("Data Persistence", "FAIL", 
                        f"Issues with: {', '.join(issues)}")
    
    def run_all_tests(self):
        """Run all backend tests in sequence"""
        print("🚀 Starting AI Travel Booking Agent Backend Tests")
        print("=" * 60)
        
        # Health checks first
        self.test_health_check()
        
        # Authentication flow
        self.test_user_registration()
        self.test_user_login()
        self.test_auth_me()
        
        # Trip management flow
        self.test_trip_generation()
        self.test_get_trips()
        self.test_get_specific_trip()
        self.test_confirm_trip()
        
        # Payment flow
        self.test_payment_creation()
        self.test_payment_verification()
        
        # Data persistence
        self.test_data_persistence()
        
        print("=" * 60)
        print("🏁 Backend Testing Complete")

if __name__ == "__main__":
    tester = BackendTester()
    tester.run_all_tests()