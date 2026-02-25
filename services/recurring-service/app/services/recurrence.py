"""
Recurrence calculation service.

Handles iCal RRule parsing and next occurrence calculation
using the rrule library.
"""

from datetime import datetime, timedelta
from typing import Optional, List
import logging
from dateutil import rrule
from dateutil.tz import tzutc, gettz

from app.models.events import RecurrencePattern
from app.config import settings

logger = logging.getLogger(settings.SERVICE_NAME)


class RecurrenceCalculator:
    """Calculate next occurrence for recurring tasks."""
    
    @staticmethod
    def parse_rrule(rrule_str: str, start_date: datetime, timezone: str = "UTC") -> rrule.rrule:
        """
        Parse iCal RRule string into rrule object.
        
        Args:
            rrule_str: iCal RRule format (e.g., "FREQ=DAILY;INTERVAL=1")
            start_date: Start date for recurrence
            timezone: Timezone for calculation
            
        Returns:
            rrule.rrule object
        """
        try:
            tz = gettz(timezone) if timezone != "UTC" else tzutc()
            
            # Parse RRule string
            rule = rrule.rrulestr(
                rrule_str,
                dtstart=start_date.replace(tzinfo=tz)
            )
            
            logger.debug(f"Parsed RRule: {rrule_str}")
            return rule
            
        except Exception as e:
            logger.error(f"Failed to parse RRule '{rrule_str}': {e}")
            raise ValueError(f"Invalid RRule format: {e}")
    
    @staticmethod
    def calculate_next_occurrence(
        recurrence_rule: str,
        start_date: datetime,
        last_occurrence: Optional[datetime] = None,
        timezone: str = "UTC"
    ) -> datetime:
        """
        Calculate the next occurrence date.
        
        Args:
            recurrence_rule: iCal RRule string
            start_date: Original start date
            last_occurrence: Last occurrence date (if any)
            timezone: Timezone for calculation
            
        Returns:
            Next occurrence datetime
        """
        try:
            rule = RecurrenceCalculator.parse_rrule(
                recurrence_rule, 
                start_date, 
                timezone
            )
            
            # If we have a last occurrence, find the next one after it
            if last_occurrence:
                next_date = rule.after(last_occurrence, inc=False)
            else:
                # First occurrence - use start date
                next_date = start_date
            
            if next_date is None:
                raise ValueError("No more occurrences available")
            
            logger.info(f"Calculated next occurrence: {next_date}")
            return next_date
            
        except Exception as e:
            logger.error(f"Failed to calculate next occurrence: {e}")
            raise
    
    @staticmethod
    def calculate_occurrences(
        recurrence_rule: str,
        start_date: datetime,
        count: int,
        timezone: str = "UTC"
    ) -> List[datetime]:
        """
        Calculate multiple future occurrences.
        
        Args:
            recurrence_rule: iCal RRule string
            start_date: Original start date
            count: Number of occurrences to calculate
            timezone: Timezone for calculation
            
        Returns:
            List of occurrence datetimes
        """
        try:
            rule = RecurrenceCalculator.parse_rrule(
                recurrence_rule,
                start_date,
                timezone
            )
            
            occurrences = list(rule[:count])
            logger.debug(f"Calculated {len(occurrences)} occurrences")
            return occurrences
            
        except Exception as e:
            logger.error(f"Failed to calculate occurrences: {e}")
            raise
    
    @staticmethod
    def get_recurrence_info(recurrence_rule: str) -> RecurrencePattern:
        """
        Extract recurrence pattern information from RRule.
        
        Args:
            recurrence_rule: iCal RRule string
            
        Returns:
            RecurrencePattern object
        """
        try:
            # Parse the RRule string manually to extract components
            parts = recurrence_rule.split(";")
            pattern_dict = {}
            
            for part in parts:
                if "=" in part:
                    key, value = part.split("=", 1)
                    pattern_dict[key] = value
            
            return RecurrencePattern(
                frequency=pattern_dict.get("FREQ", "DAILY"),
                interval=int(pattern_dict.get("INTERVAL", "1")),
                byWeekday=pattern_dict.get("BYDAY", "").split(",") if pattern_dict.get("BYDAY") else None,
                byMonthday=[int(x) for x in pattern_dict.get("BYMONTHDAY", "").split(",")] if pattern_dict.get("BYMONTHDAY") else None,
                count=int(pattern_dict["COUNT"]) if pattern_dict.get("COUNT") else None,
                until=datetime.fromisoformat(pattern_dict["UNTIL"]) if pattern_dict.get("UNTIL") else None
            )
            
        except Exception as e:
            logger.error(f"Failed to extract recurrence info: {e}")
            raise
    
    @staticmethod
    def is_occurrence_due(
        recurrence_rule: str,
        start_date: datetime,
        last_occurrence: Optional[datetime],
        timezone: str = "UTC"
    ) -> bool:
        """
        Check if a new occurrence is due.
        
        Args:
            recurrence_rule: iCal RRule string
            start_date: Original start date
            last_occurrence: Last occurrence date
            timezone: Timezone for calculation
            
        Returns:
            True if new occurrence is due
        """
        try:
            next_occurrence = RecurrenceCalculator.calculate_next_occurrence(
                recurrence_rule,
                start_date,
                last_occurrence,
                timezone
            )
            
            now = datetime.now(tz=gettz(timezone) if timezone != "UTC" else tzutc())
            is_due = next_occurrence <= now
            
            if is_due:
                logger.info(f"Occurrence is due (scheduled: {next_occurrence}, now: {now})")
            
            return is_due
            
        except Exception as e:
            logger.error(f"Failed to check if occurrence is due: {e}")
            return False
