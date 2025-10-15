import logging
from django.conf import settings
from django.core.cache import cache
import os

logger = logging.getLogger(__name__)

def is_master_otp(otp: str, phone: str) -> bool:
    """Check if the provided OTP is the master OTP"""
    # master_otp = getattr(settings, 'MASTER_OTP', None)
    master_otp = os.getenv('MASTER_OTP', '986257') 
    
    # Rate limiting
    cache_key = f"master_otp_attempts:{phone}"
    attempts = cache.get(cache_key, 0)
    
    if attempts >= 3:  # Limit to 3 attempts per hour
        logger.warning(f"Too many master OTP attempts for {phone}")
        return False
        
    is_master = master_otp and otp == master_otp
    
    if is_master:
        logger.warning(f"Master OTP used for {phone}")
    else:
        cache.set(cache_key, attempts + 1, 3600)  # 1 hour timeout
        
    return is_master