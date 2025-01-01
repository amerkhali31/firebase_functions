# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`
# Manually run the scheduled tasks here: https://console.cloud.google.com/cloudscheduler

from firebase_functions import scheduler_fn, options
from firebase_admin import initialize_app, firestore
import utils.constants as constants
from utils.message_utils import send_topic_notification
from utils.time_utils import compare_times_in_timezone as compare_times
from utils.db_utils import get_data_from_document as get_data, write_data_to_document as set_data

app = initialize_app()


# Run once a day at midnight, to clean up inactive users.
@scheduler_fn.on_schedule(schedule="* * * * *", timeout_sec=30, memory=options.MemoryOption.MB_256)
def accountcleanup(event: scheduler_fn.ScheduledEvent) -> None:

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
    