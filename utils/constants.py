# Database names
NOTIFICATION_TIMES_COLLECTION = "notification_times"
NOTIFICATION_TIMES_DOCUMENT = "today"
NOTIFICATION_TIMES_FIELD = [
    'fajr_adhan',
    'fajr_iqama',
    'dhuhr_adhan',
    'dhuhr_iqama',
    'asr_adhan',
    'asr_iqama',
    'maghrib_adhan',
    'maghrib_iqama',
    'isha_adhan',
    'isha_iqama',
]

TODAY_COLLECTION = "todays_prayer_times"
TODAY_DOCUMENT = "daily_prayer_times"
TODAY_FIELD = [
    'fajr_adhan',
    'fajr_iqama',
    'dhuhr_adhan',
    'dhuhr_iqama',
    'asr_adhan',
    'asr_iqama',
    'maghrib_adhan',
    'maghrib_iqama',
    'isha_adhan',
    'isha_iqama',
    'jumaa_salah',
    'jumaa_khutba'
]

MONTH_COLLECTION = "monthly_adhan_times"

ANNOUNCEMENT_COLLECTION = "announcements"
ANNOUNCEMENT_DOCUMENT = "announcements"
ANNOUNCEMENT_FIELD = "urls"

HADITH_COLLECTION = "hadiths"
HADITH_DOCUMENT = "hadith"
HADITH_FIELD = "number"

TEST_COLLECTION = "z_functions_tests"
TEST_1_DOCUMENT = "every_minute_test"
FIELD1 = "counter"
FIELD2 = "time"
TEST_2_DOCUMENT = "scrape_test"
FIELD3 = "time"
# Adhan API
API_URL = 'https://api.aladhan.com'
PRAYER_TIMES_ENDPOINT = '/v1/timings'
MONTHLY_PRAYER_TIMES_ENDPOINT = '/v1/calendar/{year}/{month}'

# MAGR
FRONT_PAGE_URL = 'https://magr.org/wp-json/wp/v2/pages/2429?_fields=content'
LATITUDE = '42.235857'
LONGITUDE = '-89.000643'
PRAYER_NAMES = ['Fajr', 'Zuhr', 'Asr', 'Maghrib', 'Isha', 'Friday Khutbah', 'Friday Salat']