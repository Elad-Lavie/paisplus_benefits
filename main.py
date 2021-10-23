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


def _get_paisplus_benefits(driver, benefit_keyword):
    """ scarping benefits that match the benefit_keyword.
    if there is at least one match, returns the amount, and png screenshot of the benefits.
    if there is no match, returns (0, None)"""

    url = PAIS_PLUS_SEARCH_ENDPOINT.format(parse.quote(benefit_keyword))
    driver.get(url)
    matched_items = driver.find_elements(By.CSS_SELECTOR, 'a.card_item')
    if matched_items:
        parent_item = matched_items[0].find_element(By.XPATH, "..")
        time.sleep(1)  # wait for the pictures to be loaded
        return len(matched_items), parent_item.screenshot_as_png

    return 0, None


def main():
    user_id, telegram_token = sys.argv[1:]
    bot = telegram.Bot(token=telegram_token)
    pais_plus_benefits = ["wolt", "ניצת", "רמי לוי"]
    driver = _create_webdriver()
    driver.implicitly_wait(2)  # keep polling for 2 seconds if any element is not immediately available

    while True:
        for benefit_name in pais_plus_benefits.copy():
            number_of_benefits, screenshot = _get_paisplus_benefits(driver, benefit_name)

            if number_of_benefits:
                caption = f"found {number_of_benefits} benefit" + "s" if number_of_benefits > 1 else ""
                caption += f"\n{driver.current_url}"
                bot.send_photo(chat_id=user_id, photo=screenshot, caption=caption)
                pais_plus_benefits.remove(benefit_name)
                print(f'{benefit_name} is available')

        time.sleep(CHECK_INTERVAL_IN_SECONDS)


if __name__ == '__main__':
    main()
