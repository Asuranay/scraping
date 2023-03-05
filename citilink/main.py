import re
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


# отфильтровано: цена по убыванию, память 6гг и более
url = 'https://www.citilink.ru/catalog/videokarty/?sorting=price_desc&pf=discount.any%2Crating.any%2C304_296d1gb%' \
      '2C304_298d1gb%2C304_2910d1gb%2C304_2912d1gb%2C304_2916d1gb%2C304_2920d1gb%2C304_2924d1gb&f=discount.any%' \
      '2Crating.any%2C304_296d1gb%2C304_298d1gb%2C304_2910d1gb%2C304_2912d1gb%2C304_2916d1gb%2C304_2920d1gb%' \
      '2C304_2924d1gb%2C304_2948d1gb&pprice_min=3890&pprice_max=555770&price_min=3890&price_max=555770'

path_chrome = Service('C:/Users/Suramon/PycharmProjects/parser/citilink/driver/chromedriver.exe')
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument('--disable-blink-features=AutomationControlled')

driver = webdriver.Chrome(service=path_chrome, options=options)
driver.set_window_size(1920, 1080)

data_dict = []

def city(url:str, city:str) -> None:
    '''Выбираем город'''
    driver.get(url=url)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@data-meta-name='CityChangeButton']"))).click()


    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, city))).click()

    while True:
        try:
            card()
            page_scroll()
        except:
            break

def page_scroll():
    '''Скролим всю страницу до конца'''
    time.sleep(2)
    # driver.find_element(By.XPATH, "//div[@class='app-catalog-165t4zf ey27zj40']/div/div[2]/button").click()
    link = driver.find_element(By.PARTIAL_LINK_TEXT, "Следующая")
    link.click()
    print(link.text)
    time.sleep(2)
def card():
    '''Заполнение карточек товаров'''
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'app-catalog-9gnskf')))
    names = driver.find_elements(By.XPATH, "//div[@class='e12wdlvo0 app-catalog-1bogmvw e1loosed0']/div/div[3]/div[1]")
    urls = driver.find_elements(By.XPATH, "//div[@class='e12wdlvo0 app-catalog-1bogmvw e1loosed0']/div/div[3]/div[1]/a")
    gpus = driver.find_elements(By.XPATH, "//div[@class='e12wdlvo0 app-catalog-1bogmvw e1loosed0']/div/div[6]/ul/li[1]")
    prices = driver.find_elements(By.XPATH, "//div[@class='e12wdlvo0 app-catalog-1bogmvw e1loosed0']/div/div[7]/div[1]/div[2]/span/span/span[1]")
    time.sleep(5)
    for num, name in enumerate(names):
        # name = name.text
        url = urls[num].get_attribute('href')
        try:
            gpu = re.search(r'((RTX|RX|GTX|GT)\s?\d+\s?(Ti|SUPER)?)', gpus[num].text).group().strip()
        except:
            gpu = 'another'
        try:
            price = prices[num].text.replace(' ', '')
        except:
            price = 'Товара нет в наличии'
        # try: Отрабатывает 2 раза и уходит в except даже не пробуя try, без атрибута --headless отрабатывает лишь раз
        #     time.sleep(2)
        #     # driver.find_element(By.XPATH, "//div[@class='e12wdlvo0 app-catalog-1bogmvw e1loosed0']/div/div[6]/div/div/div/div/button").click()
        #     driver.find_element(By.XPATH, "//div[@class='e12wdlvo0 app-catalog-1bogmvw e1loosed0']/div/div[7]/div[2]/button").click()
        #     time.sleep(2)
        #     WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'css-1uvjxrj'))).send_keys('999')
        #     time.sleep(2)
        #     store = driver.find_element(By.CLASS_NAME, 'css-1uvjxrj').get_attribute('value')
        #     time.sleep(2)
        #     driver.find_element(By.CLASS_NAME, 'e1nu7pom0').click()
        # except:
        #     store = 0

        data = {
            'url': url,
            'name': name.text,
            'gpu': gpu,
            'price': price
        }
        data_dict.append(data)


if __name__ == '__main__':
    try:
        city(url, 'Москва')
    except Exception as ex:
        print(ex)
    finally:
        print(len(data_dict))
        # with open('citilink_data.json', 'w', encoding='utf-8') as file_data:
        #     json.dump(data_dict, file_data, indent=4, ensure_ascii=False)
        print('close')
        driver.close()
        driver.quit()

