import datetime
from enum import Enum
from typing import Optional

class ScraperResult():
    def __init__(self, prayer_times, announcements):
        self.prayer_times = prayer_times
        self.announcements = announcements

class PrayerTime():
    class Fields(Enum):
        NAME = 'name'
        TIME = 'time'
    def __init__(self, name, time):
        self.name = name
        self.time = time

class Announcement():
    class Fields(Enum):
        URL = 'url'
    def __init__(self, url):
        self.url = url

class DailyPrayerTimes():
    class Fields(Enum):
        DATE = 'date'
        FAJR = 'fajr'
        ASR = 'asr'
        MAGHRIB = 'maghrib'
        ISHA = 'isha'
    
    def __init__(
            self,
            date: str,
            fajr: str,
            sunrise: str,
            dhuhr: str,
            asr: str,
            maghrib: str,
            isha: str,
            duha: Optional[str] = None,
        ):
        self.date = date
        self.fajr = fajr
        self.sunrise = sunrise
        self.dhuhr = dhuhr
        self.asr = asr
        self.maghrib = maghrib
        self.isha = isha
        
        # Duha is usually not provided by the API, but it is always 15 minutes after sunrise
        if not duha:
            duha = '00:00'
        self.duha = duha

    def __str__(self):
        return f'{self.date} {self.fajr} {self.sunrise} {self.dhuhr} {self.asr} {self.maghrib} {self.isha}'