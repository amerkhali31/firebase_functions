import requests
import constants
from typing import Any
from typing import Optional
from datetime import datetime
from models import DailyPrayerTimes
from time_utils import strip_timezone

class PrayerTimesApi():

    class Parameters():
        LATITUDE = 'latitude'
        LONGITUDE = 'longitude'
        METHOD = 'method'
        SHAFAQ = 'shafaq'
        TUNE = 'tune'
        SCHOOL = 'school'
        MIDNIGHT_MODE = 'midnightMode'
        TIMEZONE_STRING = 'timezonestring'
        LATITUDE_ADJUSTMENT_METHOD = 'latitudeAdjustmentMethod'
        ADJUSTMENT = 'adjustment'
        ISO8601 = 'iso8601'

        def __init__(
                self,
                latitude: str,
                longitude: str,
                method: Optional[str] = None,
                shafaq: Optional[str] = None,
                tune: Optional[str] = None,
                school: Optional[int] = None,
                midnightMode: Optional[int] = None,
                timezonestring: Optional[str] = None,
                latitudeAdjustmentMethod: Optional[int] = None,
                adjustment: Optional[int] = None,
                iso8601: Optional[str] = None
            ):
            self.latitude = latitude
            self.longitude = longitude
            self.method = method
            self.shafaq = shafaq
            self.tune = tune
            self.school = school
            self.midnightMode = midnightMode
            self.timezonestring = timezonestring
            self.latitudeAdjustmentMethod = latitudeAdjustmentMethod
            self.adjustment = adjustment
            self.iso8601 = iso8601

    class LatitudeAdjustmentMethod():
        MIDDLE_OF_THE_NIGHT = 1
        ONE_SEVENTH = 2
        ANGLE_BASED = 3

    class Shafaq():
        GENERAL = 'general'
        AHMER = 'ahmer'
        ABYAD = 'abyad'

    class School():
        SHAFI = 0
        HANAFI = 1
    
    class Methods():
        DEFAULT = 0
        JAFARI = 0
        SHIA_ITHNA_ASHARI = 0
        UNIVERSITY_OF_ISLAMIC_SCIENCES = 1
        ISLAMIC_SOCIETY_OF_NORTH_AMERICA = 2
        MUSLIM_WORLD_LEAGUE = 3
        UMM_ALQURA_UNIVERSITY = 4
        EGYPTIAN_GENERAL_AUTHORITY_OF_SURVEY = 5
        INSTITUTE_OF_GEOPHYSICS_UNIVERSITY_OF_TEHRAN = 6
        GULF_REGION = 8
        KUWAIT = 9
        QATAR = 10
        MAJLIS_UGAMA_ISLAM_SIGNAPURA_SINGAPORE = 12
        UNION_ORGANIZATION_ISLAMIC_DE_FRANCE = 12
        DIYANET_ISLERI_BASKANLIGI_TURKEY = 13
        SPIRITUAL_ADMINISTRATION_OF_MUSLIMS_OF_RUSSIA = 14
        MOONSIGHTING_COMMITTEE_WORLDWIDE = 15 # Requires shafaq parameter
        DUBAI = 16 # Experimental
        JABATAN_KEMAJUAN_ISLAM_MALAYSIA = 17 # JAKIM
        TUNISIA = 18
        ALGERIA = 19
        KEMENAG = 20 # Kementerian Agama Republik Indonesia
        MOROCCO = 21
        COMUNIDADE_ISLAMICA_DE_LISBOA = 22
        MINISTRY_OF_AWQAF_JORDAN = 23 # Islamic Affairs and Holy Places
        CUSTOM = 99 # See https://aladhan.com/calculation-methods

    @classmethod
    def get_daily_prayer_times(
            api,
            date: str,
            parameters: Parameters
        ) -> DailyPrayerTimes:

        #print(f'Getting prayer times for {date} at {parameters.latitude},{parameters.longitude} using {parameters.method} method')
        url = f'{constants.ALADHAN_API.API_URL}{constants.ALADHAN_API.PRAYER_TIMES_ENDPOINT}/{date}'
        response = requests.get(url, parameters.__dict__)

        # Raise an exception for HTTP errors
        response.raise_for_status()

        # Parse the JSON data and return wrapper object
        json_data = response.json()
        prayer_times = json_data['data']['timings']
        return DailyPrayerTimes(
            date = date,
            fajr = prayer_times['Fajr'],
            sunrise = prayer_times['Sunrise'],
            dhuhr = prayer_times['Dhuhr'],
            asr = prayer_times['Asr'],
            maghrib = prayer_times['Maghrib'],
            isha = prayer_times['Isha']
        )

    @classmethod
    def get_monthly_prayer_times(
            api,
            year: str,
            month: str,
            parameters: Parameters
        ) -> list[DailyPrayerTimes]:

        #print(f'Getting prayer times for {year}-{month} at {parameters.latitude},{parameters.longitude} using {parameters.method} method')
        endpoint = constants.ALADHAN_API.MONTHLY_PRAYER_TIMES_ENDPOINT.format(year=year, month=month)
        url = f'{constants.ALADHAN_API.API_URL}{endpoint}'
        response = requests.get(url, parameters.__dict__)

        # Raise an exception for HTTP errors
        response.raise_for_status()

        # Parse the JSON data and return wrapper object
        #clearprint(response.text)
        json_data = response.json()
        days = json_data['data']
        prayer_days = []
        for day in days:
            prayer_times = day['timings']
            date = datetime.strptime(day['date']['gregorian']['date'], '%d-%m-%Y')
            prayer_days.append(DailyPrayerTimes(
                date = date.strftime('%Y-%m-%d'),
                fajr = strip_timezone(prayer_times['Sunrise']),
                dhuhr = strip_timezone(prayer_times['Dhuhr']),
                asr = strip_timezone(prayer_times['Asr']),
                maghrib = strip_timezone(prayer_times['Maghrib']),
                isha = strip_timezone(prayer_times['Isha'])
            ))

        return prayer_days