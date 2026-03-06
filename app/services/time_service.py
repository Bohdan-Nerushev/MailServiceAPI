import os
from datetime import datetime
from zoneinfo import ZoneInfo
import logging

logger = logging.getLogger(__name__)

class TimeService:
    def __init__(self):
        self._default_timezone = os.getenv("DISPLAY_TIMEZONE", "Europe/Berlin")
        try:
            self._tz = ZoneInfo(self._default_timezone)
        except Exception as e:
            logger.error(f"Invalid timezone configuration: {self._default_timezone}. Falling back to UTC. Error: {e}")
            self._tz = ZoneInfo("UTC")

    def now(self) -> datetime:
        """Returns current time in configured timezone."""
        return datetime.now(self._tz)

    def to_display_string(self, dt: datetime, format_str: str = "%d %b %Y, %H:%M") -> str:
        """Converts a datetime object to a formatted string in the configured timezone."""
        if dt is None:
            return "Unknown"
        
        try:
            # If datetime is naive, assume it's UTC or Local and convert
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=ZoneInfo("UTC"))
            
            display_dt = dt.astimezone(self._tz)
            return display_dt.strftime(format_str)
        except Exception as e:
            logger.error(f"Error formatting datetime: {e}")
            return str(dt)

time_service = TimeService()
