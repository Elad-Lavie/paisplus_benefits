import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import telegram
from urllib import parse
from webdriver_manager.chrome import ChromeDriverManager

PAIS_PLUS_SEARCH_ENDPOINT = r"https://www.paisplus.co.il/search?query={}"
CHECK_INTERVAL_IN_SECONDS = 5 * 60


def is_benefit_available(driver, benefit_name):
    url = PAIS_PLUS_SEARCH_ENDPOINT.format(benefit_name)
    driver.get(url)
    # let the page enough load time.
    time.sleep(0.5)
    # There is a div with class='results' only when there is no matched benefit
    elements = driver.find_elements(By.CSS_SELECTOR, 'div.results')
    return bool(not elements)


def main():
    user_id, telegram_token = sys.argv[1:]
    bot = telegram.Bot(token=telegram_token)
    pais_plus_benefits = ["wolt", "ניצת", "רמי לוי"]
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    while True:
        for benefit_name in pais_plus_benefits.copy():
            if is_benefit_available(driver, benefit_name):
                pais_plus_benefits.remove(benefit_name)
                print(f'{benefit_name} is available')
                url = PAIS_PLUS_SEARCH_ENDPOINT.format(parse.quote(benefit_name))
                bot.send_message(text=f"{benefit_name} available: {url}", chat_id=user_id)
        time.sleep(CHECK_INTERVAL_IN_SECONDS)


if __name__ == '__main__':
    main()
