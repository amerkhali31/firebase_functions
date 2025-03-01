from utils.models import Announcement
from utils.models import PrayerTime
from utils.models import ScraperResult
from bs4 import BeautifulSoup
import utils.constants as constants
import requests
import re

def scrape_magr():

    prayer_name_mapping = {
        "Fajr": "Fajr",
        "Zuhr": "Dhuhr",
        "Asr": "Asr",
        "Maghrib": "Maghrib",
        "Isha": "Isha",
    }

    # Make a GET request to fetch the JSON data
    response = requests.get(constants.FRONT_PAGE_URL, headers=constants.HEADERS)

    # Raise an exception for HTTP errors
    response.raise_for_status()

    # Parse the JSON data
    json_data = response.json()
    #print(f'DEBUGGING json_data: {json_data}')
    soup = BeautifulSoup(json_data['content']['rendered'], 'html.parser')

    fajr_row = soup.find('td', string=lambda t: t and 'Fajr' in t)

    soup.find_all()
    
    prayer_times = []

    for prayer in constants.PRAYER_NAMES:
        # Find the <td> element for the prayer
        prayer_row = soup.find('td', string=lambda t: t and t.strip() == prayer)

        if not prayer_row:
            continue

        # Get the time from the next sibling <td>
        next_td = prayer_row.find_next_sibling('td')

        if not next_td:
            continue

        # Standardize the prayer name to match normal spelling
        standardized_name = prayer_name_mapping.get(prayer.strip(), prayer)

        # If the prayer time was found, add it to the list
        prayer_times.append(
            PrayerTime(standardized_name, next_td.get_text(strip=True))
        )

    # Extract announcements
    announcements=[]
    for image in soup.find_all('img', attrs={'class': re.compile('wp-image-*')}):
        announcements.append(
            Announcement(image['src'])
        )

    # Output the prayer times
    return ScraperResult(prayer_times, announcements)