from firebase_functions import scheduler_fn, options
from firebase_admin import initialize_app, firestore
from datetime import date, datetime
import utils.constants as constants
from utils.message_utils import send_topic_notification
from utils.time_utils import compare_times_in_timezone as compare_times, process_time_string, subtract_minutes, convert_to_12_hour_format
from utils.db_utils import get_data_from_document as get_data, write_data_to_document as set_data, batch_write_month
from utils.adhan_api import PrayerTimesApi
from utils.scraper import scrape_magr
from utils.rng_utils import generate_daily_random_number
from zoneinfo import ZoneInfo

app = initialize_app()

# Deploy with `firebase deploy`
# Manually run the scheduled tasks here: https://console.cloud.google.com/cloudscheduler

@scheduler_fn.on_schedule(schedule="* * * * *", timeout_sec=30, memory=options.MemoryOption.MB_256)
def accountcleanup(event: scheduler_fn.ScheduledEvent) -> None:

    # Get the time that we want to update firebase
    update_time = get_data(constants.FIREBASE_FUNCTIONS_COLLECTION, constants.UPDATE_DOCUMENT)[constants.UPDATE_FIELD_2]

    # Check if it is time to update firebase
    if compare_times({constants.UPDATE_FIELD_2: update_time}):

        # Update the update_firebase document to write to it the last time it was updated
        update_dict = {constants.UPDATE_FIELD: firestore.SERVER_TIMESTAMP, constants.UPDATE_FIELD_2: update_time}
        set_data(constants.FIREBASE_FUNCTIONS_COLLECTION, constants.UPDATE_DOCUMENT, update_dict)

        today = date.today()
        month = today.month
        year = today.year

        adhan_api_parameters = PrayerTimesApi.Parameters(
            latitude=constants.LATITUDE,
            longitude=constants.LONGITUDE,
            method=PrayerTimesApi.Methods.ISLAMIC_SOCIETY_OF_NORTH_AMERICA,
            school=PrayerTimesApi.School.SHAFI
        )

        # Get the monthly and daily prayer times
        monthly_adhan_times = PrayerTimesApi.get_monthly_prayer_times(year, month, adhan_api_parameters)
        daily_adhan_times = PrayerTimesApi.get_daily_prayer_times(today, adhan_api_parameters)
        
        # Get Today's iqama times and announcements
        scraper_result = scrape_magr()
        daily_iqama_times = {prayer.name.lower(): prayer.time for prayer in scraper_result.prayer_times}  # Convert to dict
        announcements = scraper_result.announcements
        
        # Format the times
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
                prayer: subtract_minutes(time, 20)
                for prayer, time in prayer_times.items()
                if prayer.endswith("_iqama")  # Subtract 15 minutes from iqama times
            },
            'jumaa_khutba': subtract_minutes(prayer_times['jumaa_khutba'], 20),
            'jumaa_salah':  subtract_minutes(prayer_times['jumaa_salah'], 40),
            'membership_renewal': "8:00"
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

    # If there is a match to a time for a notification
    if notification_topic:

        # If the match is to a jumaa notification
        if notification_topic in constants.NOTIFICATION_TIMES_FIELD[10:12]:

            # Only Send the Notification if it is Friday
            if datetime.now().strftime('%A') == "Friday":
                send_topic_notification(notification_topic)
        

        # If the Match is For Membership Renewal
        elif notification_topic == constants.NOTIFICATION_TIMES_FIELD[13]:

            # Check if it is in the correct date range to send this notice
            if datetime(2025, 1, 1) <= datetime.now() <= datetime(2025, 1, 20):
                send_topic_notification(notification_topic)

        # If the Match is for a Normal Daily Prayer
        else:
            send_topic_notification(notification_topic)

    # Update the counter in the test document
    data = get_data(constants.FIREBASE_FUNCTIONS_COLLECTION, constants.INVOCATIONS_DOCUMENT)
    set_data(constants.FIREBASE_FUNCTIONS_COLLECTION, constants.INVOCATIONS_DOCUMENT, {
        constants.INVOCATIONS_FIELD_2: data[constants.INVOCATIONS_FIELD_2] + 1,
        constants.INVOCATIONS_FIELD: firestore.SERVER_TIMESTAMP
        })