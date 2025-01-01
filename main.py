from firebase_functions import scheduler_fn, options
from firebase_admin import initialize_app, firestore
from datetime import date
import utils.constants as constants
from utils.message_utils import send_topic_notification
from utils.time_utils import compare_times_in_timezone as compare_times, process_time_string, subtract_15_minutes, convert_to_12_hour_format
from utils.db_utils import get_data_from_document as get_data, write_data_to_document as set_data, batch_write_month
from utils.adhan_api import PrayerTimesApi
from utils.scraper import scrape_magr
from utils.rng_utils import generate_daily_random_number

app = initialize_app()

# Deploy with `firebase deploy`
# Manually run the scheduled tasks here: https://console.cloud.google.com/cloudscheduler

@scheduler_fn.on_schedule(schedule="* * * * *", timeout_sec=30, memory=options.MemoryOption.MB_256)
def accountcleanup(event: scheduler_fn.ScheduledEvent) -> None:

    # Update Firebase if it is midnight
    update_time = get_data(constants.TEST_COLLECTION, constants.TEST_2_DOCUMENT)
    if compare_times(update_time):
        set_data(constants.TEST_COLLECTION, "scrape_update_test", {"counter": 1})

        today = date.today()
        month = today.month
        year = today.year

        adhan_api_parameters = PrayerTimesApi.Parameters(
            latitude=constants.LATITUDE,
            longitude=constants.LONGITUDE,
            method=PrayerTimesApi.Methods.ISLAMIC_SOCIETY_OF_NORTH_AMERICA,
            school=PrayerTimesApi.School.SHAFI
        )

        monthly_adhan_times = PrayerTimesApi.get_monthly_prayer_times(year, month, adhan_api_parameters)
        daily_adhan_times = PrayerTimesApi.get_daily_prayer_times(today, adhan_api_parameters)
        
        # Get Today's iqama times and announcements
        scraper_result = scrape_magr()
        daily_iqama_times = {prayer.name.lower(): prayer.time for prayer in scraper_result.prayer_times}  # Convert to dict
        announcements = scraper_result.announcements
        
        prayer_times = {
            'jumaa_khutba': process_time_string('', daily_iqama_times["friday khutbah"]),
            'jumaa_salah': process_time_string('', daily_iqama_times["friday salat"]),
            **{
                f"{prayer.lower()}_adhan": getattr(daily_adhan_times, prayer.lower())
                for prayer in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
            },
            **{
                f"{prayer.lower()}_iqama": process_time_string(
                    getattr(daily_adhan_times, prayer.lower()),  # Base adhan time
                    daily_iqama_times.get(prayer.lower(), "")  # Iqama time string
                )
                for prayer in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
                if prayer.lower() in daily_iqama_times
            }
        }

        adjusted_notification_times = {
            **{
                prayer: time
                for prayer, time in prayer_times.items()
                if prayer.endswith("_adhan")  # Keep adhan times as is
            },
            **{
                prayer: subtract_15_minutes(time)
                for prayer, time in prayer_times.items()
                if prayer.endswith("_iqama")  # Subtract 15 minutes from iqama times
            }
        }

        # announcements
        set_data(constants.ANNOUNCEMENT_COLLECTION, constants.ANNOUNCEMENT_DOCUMENT, {constants.ANNOUNCEMENT_FIELD: [announcement.url for announcement in announcements]})

        # today times
        formatted_times = {key: convert_to_12_hour_format(value).lstrip('0') for key, value in prayer_times.items()}
        set_data(constants.TODAY_COLLECTION, constants.TODAY_DOCUMENT, formatted_times)

        # random number
        set_data(constants.HADITH_COLLECTION, constants.HADITH_DOCUMENT, {constants.HADITH_FIELD: generate_daily_random_number(today)})

        # notification times
        formatted_times = {key: convert_to_12_hour_format(value).lstrip('0') for key, value in adjusted_notification_times.items()}
        set_data(constants.NOTIFICATION_TIMES_COLLECTION, constants.NOTIFICATION_TIMES_DOCUMENT, formatted_times)

        # monthly times        
        batch_write_month(constants.MONTH_COLLECTION, monthly_adhan_times)

    # Get the notification times
    notification_times = get_data(constants.NOTIFICATION_TIMES_COLLECTION, constants.NOTIFICATION_TIMES_DOCUMENT)

    # Compare the current time to the notification times
    notification_topic = compare_times(notification_times)

    # Send a notification if a match is found
    if notification_topic:
        send_topic_notification(notification_topic)

    # Update the counter in the test document
    data = get_data(constants.TEST_COLLECTION, constants.TEST_1_DOCUMENT)
    set_data(constants.TEST_COLLECTION, constants.TEST_1_DOCUMENT, {
        constants.FIELD1: data[constants.FIELD1] + 1,
        constants.FIELD2: firestore.SERVER_TIMESTAMP
        })