from typing import Dict, Any, Optional
from pywebpush import webpush, WebPushException
import json
from app.config import settings
from app.api.v1.dao.push_dao import PushDAO


class PushService:
    """Service for sending push notifications"""
    
    def __init__(self):
        self.push_dao = PushDAO()
    
    def subscribe_user(
        self,
        user_id: int,
        subscription: Dict[str, Any]
    ) -> bool:
        """Subscribe a user to push notifications"""
        try:
            self.push_dao.save_subscription(user_id, subscription)
            return True
        except Exception as e:
            print(f"Error subscribing user {user_id}: {e}")
            return False
    
    def unsubscribe_user(self, user_id: int) -> bool:
        """Unsubscribe a user from push notifications"""
        try:
            self.push_dao.delete_subscription(user_id)
            return True
        except Exception as e:
            print(f"Error unsubscribing user {user_id}: {e}")
            return False
    
    def send_notification(
        self,
        user_id: int,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send a push notification to a user"""
        if not settings.VAPID_PRIVATE_KEY or not settings.VAPID_PUBLIC_KEY:
            print("VAPID keys not configured, skipping push notification")
            return False
        
        subscription = self.push_dao.get_subscription(user_id)
        if not subscription:
            print(f"No push subscription found for user {user_id}")
            return False
        
        try:
            # Prepare notification payload
            payload = {
                "title": title,
                "body": body,
                "icon": "/upskill-logo.svg",
                "badge": "/upskill-logo.svg",
                "tag": data.get("tag", "notification") if data else "notification",
                "data": data or {}
            }
            
            # Format VAPID private key if needed
            from app.utils.vapid import format_vapid_private_key
            try:
                vapid_key = format_vapid_private_key(settings.VAPID_PRIVATE_KEY)
                # Verify the key format
                if not vapid_key or (not vapid_key.startswith('-----BEGIN') and len(vapid_key) < 32):
                    print(f"Warning: VAPID key format may be incorrect. Key length: {len(vapid_key) if vapid_key else 0}")
            except Exception as e:
                print(f"Error formatting VAPID key: {e}")
                import traceback
                traceback.print_exc()
                return False
            
            # Send push notification
            webpush(
                subscription_info=subscription,
                data=json.dumps(payload),
                vapid_private_key=vapid_key,
                vapid_claims={
                    "sub": settings.VAPID_CONTACT_EMAIL or "mailto:team@inurek.com"
                }
            )
            print(f"✓ Push notification sent successfully to user {user_id}")
            return True
        except WebPushException as e:
            print(f"WebPush error for user {user_id}: {e}")
            # If subscription is invalid, remove it
            if e.response and e.response.status_code in [410, 404]:
                print(f"Removing invalid subscription for user {user_id}")
                self.push_dao.delete_subscription(user_id)
            return False
        except Exception as e:
            print(f"Error sending push notification to user {user_id}: {e}")
            return False
    
    def send_journey_ready_notification(
        self,
        user_id: int,
        journey_id: int,
        topic: str
    ) -> bool:
        """Send notification when a journey is ready"""
        return self.send_notification(
            user_id=user_id,
            title="Journey Ready! 🎉",
            body=f"Your learning journey for '{topic}' is ready to start!",
            data={
                "type": "journey_ready",
                "journeyId": journey_id,
                "url": f"/journey/{journey_id}"
            }
        )

