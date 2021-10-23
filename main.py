import sys
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
import telegram
from urllib import parse

PAIS_PLUS_SEARCH_ENDPOINT = r"https://www.paisplus.co.il/search?query={}"
CHECK_INTERVAL_IN_SECONDS = 5 * 60


def _create_webdriver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1080x1920')
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
        ' Chrome/61.0.3163.100 Safari/537.36')

    return webdriver.Chrome(options=chrome_options)


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
    driver = _create_webdriver()

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
