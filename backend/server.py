"""
Travel AI — Backend Server (Production-Grade)
===============================================
Distributed systems safeguards:
  1. Proper lifecycle management (lifespan, not deprecated on_event)
  2. MongoDB connection pooling with explicit limits
  3. Circuit breaker integration on health checks
  4. Redis cache-backed AI itinerary generation
  5. Request timeout middleware (kills slow requests)
  6. Concurrency limiter on expensive AI endpoints
  7. Structured JSON logging for observability
  8. Graceful shutdown with connection cleanup
"""

from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
import os
import json
import asyncio
import logging
import time
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
from cache_service import cache_service
from circuit_breaker import ai_circuit_breaker, db_circuit_breaker

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, os.environ.get("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════
# LIFECYCLE MANAGEMENT (replaces deprecated on_event)
# ═══════════════════════════════════════════════

# Module-level references (set during lifespan)
mongo_client = None
db = None
itinerary_service = None

# Concurrency semaphore: limits simultaneous AI generation requests
# This is the BACKPRESSURE mechanism — prevents Gemini API from being overwhelmed
AI_CONCURRENCY_LIMIT = int(os.environ.get("AI_CONCURRENCY_LIMIT", "10"))
ai_semaphore = asyncio.Semaphore(AI_CONCURRENCY_LIMIT)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown lifecycle.
    Ref: https://fastapi.tiangolo.com/advanced/events/
    """
    global mongo_client, db, itinerary_service

    # ── STARTUP ──
    logger.info("Starting Travel AI Backend...")

    # 1. MongoDB connection with explicit pool limits
    mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    max_pool = int(os.environ.get("MONGO_MAX_POOL_SIZE", "50"))
    min_pool = int(os.environ.get("MONGO_MIN_POOL_SIZE", "5"))

    mongo_client = AsyncIOMotorClient(
        mongo_url,
        maxPoolSize=max_pool,
        minPoolSize=min_pool,
        serverSelectionTimeoutMS=5000,     # Fail fast if Mongo is unreachable
        connectTimeoutMS=5000,
        socketTimeoutMS=10000,
        retryWrites=True,
        retryReads=True,
    )
    db_name = os.environ.get("DB_NAME", "travel_agent_db")
    db = mongo_client[db_name]

    # Test MongoDB connection at startup
    try:
        await db.command("ping")
        logger.info(f"MongoDB connected: {mongo_url} (pool: {min_pool}-{max_pool})")
    except Exception as e:
        logger.error(f"MongoDB connection failed at startup: {e}")
        # Don't crash — K8s readiness probe will mark pod as not ready

    # 2. Redis cache
    await cache_service.connect()

    # 3. Initialize services
    itinerary_service = ItineraryService()

    # 4. Create MongoDB indexes for performance at scale
    try:
        await db.users.create_index("email", unique=True)
        await db.users.create_index("id", unique=True)
        await db.trips.create_index([("user_id", 1), ("created_at", -1)])
        await db.trips.create_index("id", unique=True)
        await db.bookings.create_index([("trip_id", 1), ("user_id", 1)])
        await db.payments.create_index([("order_id", 1), ("user_id", 1)])
        logger.info("MongoDB indexes created/verified.")
    except Exception as e:
        logger.warning(f"Index creation failed (non-fatal): {e}")

    logger.info(f"Travel AI Backend ready. AI concurrency limit: {AI_CONCURRENCY_LIMIT}")

    yield  # ── APP IS RUNNING ──

    # ── SHUTDOWN ──
    logger.info("Shutting down Travel AI Backend...")
    await cache_service.disconnect()
    if mongo_client:
        mongo_client.close()
    logger.info("Cleanup complete. Goodbye.")


# ═══════════════════════════════════════════════
# APP INITIALIZATION
# ═══════════════════════════════════════════════

app = FastAPI(
    title="AI Travel Booking Agent",
    version="2.0.0",
    lifespan=lifespan,
)

api_router = APIRouter(prefix="/api")


# ═══════════════════════════════════════════════
# MIDDLEWARE — Traffic Spike Safeguards
# ═══════════════════════════════════════════════

@app.middleware("http")
async def request_timeout_middleware(request: Request, call_next):
    """
    Global request timeout: kills any request that takes longer than 120 seconds.
    This prevents slow connections from consuming worker threads during traffic spikes.
    """
    try:
        response = await asyncio.wait_for(call_next(request), timeout=120.0)
        return response
    except asyncio.TimeoutError:
        logger.error(f"Request timeout: {request.method} {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={"detail": "Request timed out. Please try again."}
        )


@app.middleware("http")
async def request_metrics_middleware(request: Request, call_next):
    """
    Track request timing for observability.
    In production, this would push to Prometheus/Datadog.
    """
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    # Log slow requests (> 5 seconds)
    if duration > 5.0:
        logger.warning(f"SLOW REQUEST: {request.method} {request.url.path} took {duration:.2f}s")

    response.headers["X-Response-Time"] = f"{duration:.3f}s"
    return response


# ═══════════════════════════════════════════════
# AUTHENTICATION ENDPOINTS
# ═══════════════════════════════════════════════

@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    """Register a new user"""
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        phone=user_data.phone
    )

    user_in_db = UserInDB(
        **user.model_dump(),
        hashed_password=get_password_hash(user_data.password)
    )

    doc = user_in_db.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.users.insert_one(doc)

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
    user_doc = await db.users.find_one({"email": credentials.email})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(credentials.password, user_doc['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    user = User(
        id=user_doc['id'],
        email=user_doc['email'],
        full_name=user_doc['full_name'],
        phone=user_doc.get('phone')
    )

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


# ═══════════════════════════════════════════════
# TRIP ENDPOINTS (with circuit breaker + cache + backpressure)
# ═══════════════════════════════════════════════

@api_router.post("/trips/generate", response_model=Trip)
async def generate_trip(trip_data: TripCreate, current_user: dict = Depends(get_current_user)):
    """
    Generate a new trip itinerary using AI.

    Distributed systems safeguards:
      1. Cache check — return cached itinerary for similar searches
      2. Semaphore — limit concurrent AI calls (backpressure)
      3. Circuit breaker — stop calling AI if it's failing repeatedly
      4. Fallback — return pre-generated itinerary if everything fails
    """
    # ── Step 1: Check cache ──
    from datetime import datetime as dt
    days = (dt.strptime(trip_data.end_date, '%Y-%m-%d') - dt.strptime(trip_data.start_date, '%Y-%m-%d')).days
    cache_key = cache_service.make_itinerary_key(
        trip_data.destination, days, trip_data.budget, trip_data.preferences.model_dump()
    )

    cached = await cache_service.get(cache_key)
    if cached:
        logger.info(f"Cache HIT for itinerary: {cache_key}")
        try:
            from models import Itinerary
            itinerary = Itinerary(**json.loads(cached))
        except Exception:
            itinerary = None

        if itinerary:
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
            doc = trip.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            doc['updated_at'] = doc['updated_at'].isoformat()
            await db.trips.insert_one(doc)
            return trip

    # ── Step 2: Backpressure — limit concurrent AI calls ──
    try:
        await asyncio.wait_for(ai_semaphore.acquire(), timeout=10.0)
    except asyncio.TimeoutError:
        logger.warning("AI semaphore full — too many concurrent generation requests")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Server is busy generating itineraries. Please try again in a few seconds.",
            headers={"Retry-After": "10"}
        )

    try:
        # ── Step 3: Circuit breaker check ──
        if not ai_circuit_breaker.can_execute():
            logger.warning(f"AI circuit breaker is OPEN. Serving fallback itinerary.")
            itinerary = itinerary_service._create_fallback_itinerary(trip_data)
        else:
            try:
                logger.info(f"Generating AI itinerary for {trip_data.destination}")
                itinerary = await itinerary_service.generate_itinerary(trip_data)
                ai_circuit_breaker.record_success()

                # Cache the result for future similar searches
                await cache_service.set(
                    cache_key,
                    json.dumps(itinerary.model_dump(), default=str),
                    ttl=3600  # 1 hour cache
                )
            except Exception as e:
                logger.error(f"AI generation failed: {e}")
                ai_circuit_breaker.record_failure()
                itinerary = itinerary_service._create_fallback_itinerary(trip_data)

        # ── Step 4: Save to database ──
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

        doc = trip.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.trips.insert_one(doc)

        logger.info(f"Trip created: {trip.id}")
        return trip

    finally:
        ai_semaphore.release()


@api_router.get("/trips", response_model=List[Trip])
async def get_trips(current_user: dict = Depends(get_current_user)):
    """Get all trips for current user"""
    trips = await db.trips.find({"user_id": current_user['user_id']}, {"_id": 0}).to_list(100)

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


# ═══════════════════════════════════════════════
# BOOKING ENDPOINTS
# ═══════════════════════════════════════════════

@api_router.post("/bookings", response_model=Booking)
async def create_booking(booking_data: BookingCreate, current_user: dict = Depends(get_current_user)):
    """Create a new booking"""
    trip = await db.trips.find_one({"id": booking_data.trip_id, "user_id": current_user['user_id']})
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )

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

    for booking in bookings:
        if isinstance(booking.get('created_at'), str):
            booking['created_at'] = datetime.fromisoformat(booking['created_at'])

    return bookings


# ═══════════════════════════════════════════════
# PAYMENT ENDPOINTS
# ═══════════════════════════════════════════════

@api_router.post("/payments/create")
async def create_payment_order(payment_data: PaymentCreate, current_user: dict = Depends(get_current_user)):
    """Create a payment order (mock for now)"""
    trip = await db.trips.find_one({"id": payment_data.trip_id, "user_id": current_user['user_id']})
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )

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

    return {
        "order_id": payment.order_id,
        "amount": payment.amount,
        "currency": payment.currency,
        "status": "created"
    }


@api_router.post("/payments/verify")
async def verify_payment(payment_data: PaymentVerify, current_user: dict = Depends(get_current_user)):
    """Verify payment (mock for now)"""
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

    for payment in payments:
        if isinstance(payment.get('created_at'), str):
            payment['created_at'] = datetime.fromisoformat(payment['created_at'])

    return payments


# ═══════════════════════════════════════════════
# HEALTH & DIAGNOSTICS ENDPOINTS
# ═══════════════════════════════════════════════

@api_router.get("/")
async def root():
    return {
        "message": "AI Travel Booking Agent API",
        "version": "2.0.0",
        "status": "running"
    }


@api_router.get("/health")
async def health_check():
    """
    Health check endpoint for Kubernetes liveness/readiness probes.
    Returns 200 if the service can reach MongoDB.
    Returns 503 if critical dependencies are down.
    """
    health = {"status": "healthy", "components": {}}

    # Check MongoDB
    try:
        await db.command("ping")
        health["components"]["mongodb"] = "connected"
        db_circuit_breaker.record_success()
    except Exception as e:
        logger.error(f"Health check: MongoDB failed: {e}")
        db_circuit_breaker.record_failure()
        health["components"]["mongodb"] = "disconnected"
        health["status"] = "degraded"

    # Check Redis cache
    cache_health = await cache_service.health()
    health["components"]["redis"] = cache_health["status"]

    # Circuit breaker statuses
    health["circuit_breakers"] = {
        "ai_provider": ai_circuit_breaker.get_stats(),
        "mongodb": db_circuit_breaker.get_stats(),
    }

    # AI concurrency status
    health["ai_concurrency"] = {
        "limit": AI_CONCURRENCY_LIMIT,
        "available": ai_semaphore._value,
    }

    if health["status"] != "healthy":
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=health)

    return health


# ═══════════════════════════════════════════════
# APP ASSEMBLY
# ═══════════════════════════════════════════════

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)