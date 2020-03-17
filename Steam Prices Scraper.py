import requests
from bs4 import BeautifulSoup
import smtplib
from logininfo import username, password, to_address
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}


def transform_price(num):
    # Get numbers only from price and turn them into float
    price = num.strip().split(' ')[1]
    price = price.replace('.', '').replace(',', '.')
    return float(price)


def bypass_age_prompt(URL):
    driver_options = webdriver.ChromeOptions()
    driver_options.add_argument('--incognito')
    driver_options.add_argument('--headless')
    driver = webdriver.Chrome('C:\webdrivers\chromedriver.exe', options=driver_options)
    driver.get(URL)

    # Birthday input
    select_ageDay = Select(driver.find_element_by_id('ageDay'))
    select_ageDay.select_by_visible_text('29')
    select_ageMonth = Select(driver.find_element_by_id('ageMonth'))
    select_ageMonth.select_by_visible_text('August')
    select_ageYear = Select(driver.find_element_by_id('ageYear'))
    select_ageYear.select_by_visible_text('1990')

    # Click 'Ver página'
    button = driver.find_element_by_xpath('//*[@id="app_agegate"]/div[1]/div[3]/a[1]/span')
    
    button.click()

    time.sleep(5)

    return driver.page_source


def check_price(URL):
    try:
        page_source = requests.get(url=URL, headers=headers).content
        soup = BeautifulSoup(page_source, 'html.parser')
        title = soup.find(attrs={'class':'apphub_AppName'}).get_text().strip()
    except:
        # Skip age check of age-restricted games
        page_source = bypass_age_prompt(URL=URL)
        soup = BeautifulSoup(page_source, 'html.parser')
        title = soup.find(attrs={'class': 'apphub_AppName'}).get_text().strip()
    
    try:
        price = soup.find(attrs={'class': 'discount_final_price'}).get_text()
    except:
        price = soup.find(attrs={'class': 'game_purchase_price price'}).get_text()
    
    price = transform_price(price)

    return {'Title': title, 'Price': price}


def send_email(URL_priceThreshold, username, password, to_address):
    for game in URL_priceThreshold.keys():
        URL = game
        price_threshold = URL_priceThreshold[game]
        
        # Get item's title and price
        title_price_dict = check_price(URL=URL)
        title = title_price_dict['Title'].replace('"', '')
        title_ascii = title.encode(encoding='ascii', errors='ignore')
        price = title_price_dict['Price']
        
        if price < price_threshold:
            # Start e-mail server
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.ehlo()
            server.starttls()
            server.ehlo()

            # Login
            server.login(user=username, password=password)

            # Setup e-mail message
            subject = f"{title_ascii}'s price went down!"
            body = f'Check the following link: {URL}'
            message = f'Subject: {subject}\n\n{body}'

            # Send e-mail
            server.sendmail(from_addr=username, to_addrs=to_address, msg=message)

            print('E-mail has been sent')

            # Close server connection
            server.quit()


URL_priceThreshold = {
    'https://store.steampowered.com/app/582160/Assassins_Creed_Origins/': 400,
    'https://store.steampowered.com/app/851850/DRAGON_BALL_Z_KAKAROT/': 1400
    }

while True:
    send_email(URL_priceThreshold=URL_priceThreshold, username=username, password=password, to_address=to_address)
    time.sleep(60 * 60 * 8)