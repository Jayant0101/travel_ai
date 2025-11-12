from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List
from datetime import datetime

# Import models and services
from models import (
    User, UserCreate, UserLogin, UserInDB, Token,
    Trip, TripCreate,
    Booking, BookingCreate,
    Payment, PaymentCreate, PaymentVerify
)
from auth import (
    get_password_hash, verify_password, create_access_token, 
    create_refresh_token, get_current_user
)
from itinerary_service import ItineraryService

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="AI Travel Booking Agent")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize services
itinerary_service = ItineraryService()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============= AUTHENTICATION ENDPOINTS =============

@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    """Register a new user"""
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        phone=user_data.phone
    )
    
    user_in_db = UserInDB(
        **user.model_dump(),
        hashed_password=get_password_hash(user_data.password)
    )
    
    # Save to database
    doc = user_in_db.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.users.insert_one(doc)
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id, "email": user.email})
    refresh_token = create_refresh_token(data={"sub": user.id, "email": user.email})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user
    )

@api_router.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login user"""
    # Find user
    user_doc = await db.users.find_one({"email": credentials.email})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user_doc['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create user object
    user = User(
        id=user_doc['id'],
        email=user_doc['email'],
        full_name=user_doc['full_name'],
        phone=user_doc.get('phone')
    )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id, "email": user.email})
    refresh_token = create_refresh_token(data={"sub": user.id, "email": user.email})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user
    )

@api_router.get("/auth/me", response_model=User)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    user_doc = await db.users.find_one({"id": current_user['user_id']})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return User(
        id=user_doc['id'],
        email=user_doc['email'],
        full_name=user_doc['full_name'],
        phone=user_doc.get('phone')
    )

# ============= TRIP ENDPOINTS =============

@api_router.post("/trips/generate", response_model=Trip)
async def generate_trip(trip_data: TripCreate, current_user: dict = Depends(get_current_user)):
    """Generate a new trip itinerary using AI"""
    try:
        logger.info(f"Generating itinerary for {trip_data.destination}")
        
        # Generate itinerary using Gemini
        itinerary = await itinerary_service.generate_itinerary(trip_data)
        
        # Create trip object
        trip = Trip(
            user_id=current_user['user_id'],
            destination=trip_data.destination,
            start_date=trip_data.start_date,
            end_date=trip_data.end_date,
            budget=trip_data.budget,
            travelers=trip_data.travelers,
            preferences=trip_data.preferences,
            itinerary=itinerary,
            status="draft"
        )
        
        # Save to database
        doc = trip.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.trips.insert_one(doc)
        
        logger.info(f"Trip created successfully: {trip.id}")
        return trip
        
    except Exception as e:
        logger.error(f"Error generating trip: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate itinerary: {str(e)}"
        )

@api_router.get("/trips", response_model=List[Trip])
async def get_trips(current_user: dict = Depends(get_current_user)):
    """Get all trips for current user"""
    trips = await db.trips.find({"user_id": current_user['user_id']}, {"_id": 0}).to_list(100)
    
    # Convert ISO strings back to datetime
    for trip in trips:
        if isinstance(trip.get('created_at'), str):
            trip['created_at'] = datetime.fromisoformat(trip['created_at'])
        if isinstance(trip.get('updated_at'), str):
            trip['updated_at'] = datetime.fromisoformat(trip['updated_at'])
    
    return trips

@api_router.get("/trips/{trip_id}", response_model=Trip)
async def get_trip(trip_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific trip"""
    trip = await db.trips.find_one({"id": trip_id, "user_id": current_user['user_id']}, {"_id": 0})
    
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    
    # Convert ISO strings back to datetime
    if isinstance(trip.get('created_at'), str):
        trip['created_at'] = datetime.fromisoformat(trip['created_at'])
    if isinstance(trip.get('updated_at'), str):
        trip['updated_at'] = datetime.fromisoformat(trip['updated_at'])
    
    return trip

@api_router.put("/trips/{trip_id}/confirm")
async def confirm_trip(trip_id: str, current_user: dict = Depends(get_current_user)):
    """Confirm a trip and update status"""
    result = await db.trips.update_one(
        {"id": trip_id, "user_id": current_user['user_id']},
        {"$set": {"status": "confirmed", "updated_at": datetime.utcnow().isoformat()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    
    return {"message": "Trip confirmed successfully"}

# ============= BOOKING ENDPOINTS =============

@api_router.post("/bookings", response_model=Booking)
async def create_booking(booking_data: BookingCreate, current_user: dict = Depends(get_current_user)):
    """Create a new booking"""
    # Verify trip belongs to user
    trip = await db.trips.find_one({"id": booking_data.trip_id, "user_id": current_user['user_id']})
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    
    # Create booking
    booking = Booking(
        trip_id=booking_data.trip_id,
        user_id=current_user['user_id'],
        booking_type=booking_data.booking_type,
        provider=booking_data.provider,
        booking_reference=f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}",
        details=booking_data.details,
        amount=booking_data.amount,
        status="confirmed"
    )
    
    # Save to database
    doc = booking.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.bookings.insert_one(doc)
    
    return booking

@api_router.get("/bookings/trip/{trip_id}", response_model=List[Booking])
async def get_trip_bookings(trip_id: str, current_user: dict = Depends(get_current_user)):
    """Get all bookings for a trip"""
    bookings = await db.bookings.find(
        {"trip_id": trip_id, "user_id": current_user['user_id']},
        {"_id": 0}
    ).to_list(100)
    
    # Convert ISO strings
    for booking in bookings:
        if isinstance(booking.get('created_at'), str):
            booking['created_at'] = datetime.fromisoformat(booking['created_at'])
    
    return bookings

# ============= PAYMENT ENDPOINTS =============

@api_router.post("/payments/create")
async def create_payment_order(payment_data: PaymentCreate, current_user: dict = Depends(get_current_user)):
    """Create a payment order (mock for now)"""
    # Verify trip
    trip = await db.trips.find_one({"id": payment_data.trip_id, "user_id": current_user['user_id']})
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    
    # Create payment record
    payment = Payment(
        trip_id=payment_data.trip_id,
        user_id=current_user['user_id'],
        amount=payment_data.amount,
        order_id=f"order_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        status="pending"
    )
    
    doc = payment.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.payments.insert_one(doc)
    
    # Return mock Razorpay-like response
    return {
        "order_id": payment.order_id,
        "amount": payment.amount,
        "currency": payment.currency,
        "status": "created"
    }

@api_router.post("/payments/verify")
async def verify_payment(payment_data: PaymentVerify, current_user: dict = Depends(get_current_user)):
    """Verify payment (mock for now)"""
    # Update payment status
    result = await db.payments.update_one(
        {"order_id": payment_data.order_id, "user_id": current_user['user_id']},
        {"$set": {
            "payment_id": payment_data.payment_id,
            "signature": payment_data.signature,
            "status": "completed"
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment order not found"
        )
    
    # Update trip status to confirmed
    await db.trips.update_one(
        {"id": payment_data.trip_id, "user_id": current_user['user_id']},
        {"$set": {"status": "confirmed"}}
    )
    
    return {"message": "Payment verified successfully", "status": "completed"}

@api_router.get("/payments/trip/{trip_id}")
async def get_trip_payments(trip_id: str, current_user: dict = Depends(get_current_user)):
    """Get all payments for a trip"""
    payments = await db.payments.find(
        {"trip_id": trip_id, "user_id": current_user['user_id']},
        {"_id": 0}
    ).to_list(100)
    
    # Convert ISO strings
    for payment in payments:
        if isinstance(payment.get('created_at'), str):
            payment['created_at'] = datetime.fromisoformat(payment['created_at'])
    
    return payments

# ============= HEALTH CHECK =============

@api_router.get("/")
async def root():
    return {
        "message": "AI Travel Booking Agent API",
        "version": "1.0.0",
        "status": "running"
    }

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

# Include the router in the main app
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()