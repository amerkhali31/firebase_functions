from datetime import datetime, timedelta
from zoneinfo import ZoneInfo  # Built-in in Python 3.9+
import re

def compare_times_in_timezone(fields: dict, timezone: str = "US/Central") -> str:
    """
    Compares the current time in a specific timezone to the times in the input dictionary.

    Args:
        fields (dict): A dictionary where keys are field names and values are times as strings
                       in the format "h:mm AM/PM" (e.g., {"fajr_adhan": "2:52 PM"}).
        timezone (str): The timezone to use for the current time (e.g., "US/Central").

    Returns:
        str: A message indicating which time matches, if any.
    """
    try:
        # Step 1: Get the current time in the specified timezone
        now = datetime.now(ZoneInfo(timezone)).replace(second=0, microsecond=0)
        current_time_formatted = now.strftime("%-I:%M %p")  # e.g., "2:52 PM"

        # Step 2: Compare the current time to each entry in the dictionary
        for field_name, field_time in fields.items():
            try:
                # Parse the input time string
                field_time_obj = datetime.strptime(field_time, "%I:%M %p").replace(
                    year=now.year, month=now.month, day=now.day
                )

                # Compare formatted times
                if current_time_formatted == field_time:
                    
                    print(f"The current time matches the {field_name} time: {field_time}")
                    return field_name
                
            except ValueError as e:
                print(f"Invalid time format for {field_name}: {field_time} ({e})")
                return

        return
    except Exception as e:
        print("Error processing timezone or times:", e)
        return
    
def strip_timezone(time) -> str:
    return re.sub(r' \(.*\)$', '', time)

# Function to process the iqama time string
def process_time_string(base_time, time_string):
    # Check if the time string is an offset from the base time
    offset_match = re.match(r"(\d+)\s+minutes\s+after\s+prayer\s+time", time_string, re.IGNORECASE)
    if offset_match:
        # Calculate the offset time
        offset_minutes = int(offset_match.group(1))
        base_time_obj = datetime.strptime(base_time, "%H:%M")
        new_time_obj = base_time_obj + timedelta(minutes=offset_minutes)
        return new_time_obj.strftime("%H:%M")
    else:
        # Convert 12-hour time to 24-hour time
        time_obj = datetime.strptime(time_string, "%I:%M %p")
        return time_obj.strftime("%H:%M")

# Function to subtract 15 minutes from a time string
def subtract_15_minutes(time_string):
    time_obj = datetime.strptime(time_string, "%H:%M")
    new_time_obj = time_obj - timedelta(minutes=15)
    return new_time_obj.strftime("%H:%M")

def convert_to_12_hour_format(time_string):
    """Convert a 24-hour time string (HH:MM) to 12-hour format with AM/PM."""
    time_obj = datetime.strptime(time_string, "%H:%M")
    return time_obj.strftime("%I:%M %p")

