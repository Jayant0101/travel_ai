from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid

# User Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: User

# Trip Models
class TripPreferences(BaseModel):
    adventure: bool = False
    family_friendly: bool = False
    vegetarian: bool = False
    budget_conscious: bool = False
    luxury: bool = False

class TripCreate(BaseModel):
    destination: str
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    budget: float
    travelers: int
    preferences: TripPreferences

class DayPlan(BaseModel):
    day: int
    date: str
    title: str
    description: str
    activities: List[str]
    meals: List[Dict[str, str]]
    accommodation: Optional[Dict[str, Any]] = None

class Itinerary(BaseModel):
    destination: str
    duration_days: int
    daily_plans: List[DayPlan]
    estimated_cost: float
    hotels: List[Dict[str, Any]]
    flights: List[Dict[str, Any]]
    local_transport: List[Dict[str, Any]]
    tips: List[str]
    weather_info: Optional[str] = None
    packing_list: List[str]

class Trip(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    destination: str
    start_date: str
    end_date: str
    budget: float
    travelers: int
    preferences: TripPreferences
    itinerary: Optional[Itinerary] = None
    status: str = "draft"  # draft, confirmed, completed, cancelled
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Booking Models
class Booking(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trip_id: str
    user_id: str
    booking_type: str  # flight, hotel, train, bus, taxi
    provider: str
    booking_reference: str
    details: Dict[str, Any]
    status: str = "pending"  # pending, confirmed, cancelled
    amount: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BookingCreate(BaseModel):
    trip_id: str
    booking_type: str
    provider: str
    details: Dict[str, Any]
    amount: float

# Payment Models
class Payment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trip_id: str
    user_id: str
    amount: float
    currency: str = "INR"
    payment_method: str = "razorpay"
    payment_id: Optional[str] = None
    order_id: Optional[str] = None
    signature: Optional[str] = None
    status: str = "pending"  # pending, completed, failed, refunded
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PaymentCreate(BaseModel):
    trip_id: str
    amount: float

class PaymentVerify(BaseModel):
    payment_id: str
    order_id: str
    signature: str
    trip_id: str