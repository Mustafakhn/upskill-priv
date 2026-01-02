from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db.mysql import init_db
from app.api.v1.routers import chat_router, journey_router, resource_router, user_router, companion_router, admin_router, quiz_router, push_router
from app.db.base import Journey, JourneyStatus

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-Powered Learning Platform API"
)

# CORS middleware
cors_origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup and resume incomplete journeys"""
    try:
        print("Initializing database...")
        init_db()
        print("✓ Database initialized successfully!")
        
        # Resume incomplete journeys
        print("Checking for incomplete journeys...")
        from app.db.mysql import SessionLocal
        from app.tasks.scrape_tasks import process_journey_sync
        from app.db.base import Journey, JourneyStatus
        import threading
        
        db = SessionLocal()
        try:
            # Find all journeys that are PENDING, SCRAPING, or CURATING
            incomplete_statuses = [JourneyStatus.PENDING, JourneyStatus.SCRAPING, JourneyStatus.CURATING]
            incomplete_journeys = db.query(Journey).filter(
                Journey.status.in_(incomplete_statuses)
            ).all()
            
            if incomplete_journeys:
                print(f"Found {len(incomplete_journeys)} incomplete journey(s), resuming processing...")
                for journey in incomplete_journeys:
                    print(f"  - Resuming journey {journey.id}: {journey.topic} (status: {journey.status.value})")
                    # Start background thread to process each journey
                    thread = threading.Thread(target=process_journey_sync, args=(journey.id,))
                    thread.daemon = True
                    thread.start()
                print(f"✓ Started processing for {len(incomplete_journeys)} journey(s)")
            else:
                print("✓ No incomplete journeys found")
        except Exception as e:
            print(f"⚠ Error resuming journeys: {e}")
            import traceback
            traceback.print_exc()
        finally:
            db.close()
    except Exception as e:
        print(f"⚠ Database initialization warning: {e}")
        print("Attempting to continue...")


# Include routers
app.include_router(user_router.router, prefix=settings.API_V1_PREFIX)
app.include_router(chat_router.router, prefix=settings.API_V1_PREFIX)
app.include_router(journey_router.router, prefix=settings.API_V1_PREFIX)
app.include_router(resource_router.router, prefix=settings.API_V1_PREFIX)
app.include_router(companion_router.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin_router.router, prefix=settings.API_V1_PREFIX)
app.include_router(quiz_router.router, prefix=settings.API_V1_PREFIX)
app.include_router(push_router.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    return {
        "message": "AI Learning Platform API",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

