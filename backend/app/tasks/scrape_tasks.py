def process_journey_sync(journey_id: int):
    """Process journey in background"""
    # Import here to avoid circular import
    from app.db.mysql import SessionLocal
    from app.api.v1.services.journey_service import JourneyService
    import time
    
    # Small delay to ensure journey is committed to database
    time.sleep(0.5)
    
    try:
        db = SessionLocal()
        try:
            print(f"Starting journey processing for journey {journey_id}...")
            journey_service = JourneyService()
            result = journey_service.process_journey_sync(db, journey_id)
            db.commit()  # Make sure to commit changes
            print(f"Journey {journey_id} processed: {result}")
        except Exception as e:
            db.rollback()
            print(f"Error processing journey {journey_id}: {e}")
            import traceback
            traceback.print_exc()
        finally:
            db.close()
    except Exception as e:
        print(f"Error processing journey {journey_id}: {e}")
        import traceback
        traceback.print_exc()

