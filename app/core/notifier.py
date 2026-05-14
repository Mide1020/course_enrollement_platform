import logging
from app.config import settings

logger = logging.getLogger("app")

async def send_enrollment_notification(user_email: str, course_title: str):
    """
    Mock email notification service. 
    In production, this would use an SMTP server or an API like SendGrid/SES.
    """
    message = f"NOTIFICATION: Enrollment successful! User {user_email} has enrolled in '{course_title}'."
    
    if settings.MOCK_EMAIL:
        # Simulate some processing delay
        import asyncio
        await asyncio.sleep(1)
        logger.info(message)
    else:
        # Actual email logic would go here
        pass

async def send_waitlist_notification(user_email: str, course_title: str):
    """
    Mock waitlist notification service.
    """
    message = f"NOTIFICATION: Waitlist joined! User {user_email} is now on the waitlist for '{course_title}'."
    
    if settings.MOCK_EMAIL:
        import asyncio
        await asyncio.sleep(1)
        logger.info(message)
    else:
        pass

async def send_waitlist_promotion_notification(user_email: str, course_title: str):
    """
    Mock waitlist promotion notification service.
    Called when a student is automatically enrolled from the waitlist.
    """
    message = f"NOTIFICATION: Waitlist Promotion! User {user_email} has been automatically enrolled in '{course_title}' from the waitlist."
    
    if settings.MOCK_EMAIL:
        import asyncio
        await asyncio.sleep(1)
        logger.info(message)
    else:
        pass

async def send_welcome_email(user_email: str, user_name: str):
    """
    Mock welcome email service.
    """
    message = f"NOTIFICATION: Welcome to LMS Pro, {user_name}! We're excited to have you on board."
    
    if settings.MOCK_EMAIL:
        import asyncio
        await asyncio.sleep(1)
        logger.info(message)
    else:
        pass

async def send_login_notification(user_email: str, ip_address: str):
    """
    Mock login security alert.
    """
    message = f"NOTIFICATION: New login detected for {user_email} from IP: {ip_address}."
    
    if settings.MOCK_EMAIL:
        import asyncio
        await asyncio.sleep(1)
        logger.info(message)
    else:
        pass
