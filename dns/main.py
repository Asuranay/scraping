import re
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


url = 'https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/?order=2'

path_chrome = Service('C:/Users/Suramon/PycharmProjects/parser/dns/driver/chromedriver.exe')
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument('--disable-blink-features=AutomationControlled')
# options.add_argument('--start-maximized')

driver = webdriver.Chrome(service=path_chrome, options=options)
driver.set_window_size(1920, 1080)
data_dict = []

def page_loader(url:str) -> None:
    '''Загрузчик страницы по каталогу'''
    driver.get(url=url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[@class='catalog-product__name ui-link ui-link_black']"))
        # прогружаем до появления блока с кталогом
    )

def city(url:str, city:str) -> None:
    '''Не работает! Выделяет объект, но не кликает'''
    driver.get(url=url)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='header-top-menu__common-link header-top-menu__common-link_city']"))).click()
    # click_city = driver.find_elements(By.XPATH, "//div[@class='header-top-menu__common-link header-top-menu__common-link_city']")
    # click_city[0].click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[@class='lists-column_tkv']"))
        # прогружаем до появления блока с кталогом
    )
    driver.find_element(By.XPATH, '//*[@id="select-city"]/div[1]/div/div/div/div/input').send_keys(city, Keys.ENTER)


def create_data(url:str) -> None:
    '''Загрузка страницы ее обработка и запись в json'''
    page_loader(url)
    names = driver.find_elements(By.XPATH, "//a[@class='catalog-product__name ui-link ui-link_black']") # Блок с названием и ссылкой на товар
    prices = driver.find_elements(By.XPATH, "//div[@class='product-buy__price-wrap product-buy__price-wrap_interactive']") # Цена товара
    stores = driver.find_elements(By.XPATH, "//span[@class='catalog-product__avails avails-container']") # Наличие и магазины
    for num, name in enumerate(names):
        # Решил сделать регулярными выражениями. Ошибка в случае ненахождения будет AttributeError, но на всякий случай оставил все ошибки.
        try:
            if re.search(r'^В\sналичии', stores[num].text).group() == 'В наличии':
                # Определяем в скольки магазинах есть в наличии, через click() не удается посмотреть точное количество
                store = re.search(r'\d+', stores[num].text).group()
            else:
                store = 'Товара нет в наличии'
        except:
            store = 'Товара нет в наличии'
        try:
            url_card = name.get_attribute('href')
        except:
            url_card = 'Нет ссылки'
        try:
            # Актуальная цена. Так же в блоке есть старая цена и выплаты по кредиту
            price = str(re.match('^\d+\s?\d+',(prices[num].text)).group()).replace(' ', '')
        except:
            price = 'Нет цены'
        try:
            gpu = re.search(r'((RTX|RX|GTX|GT)\s\d+\s(Ti|SUPER)?)', name.text).group().strip()
        except:
            gpu = 'another'

        data = {
            'url': url_card,
            'name': name.text,
            'price': price,
            'gpu': gpu,
            'store': store
        }
        data_dict.append(data)

def main(url:str) -> None:
    '''Бегаем по страницам и собираем информацию'''
    page_loader(url)
    try:
        # Блок с количеством страниц хратиться в виде ссылки
        page = driver.find_element(By.XPATH,
            "//a[@class='pagination-widget__page-link pagination-widget__page-link_last ']").get_attribute('href')
        # Достаем нужное нам значение "/catalog/17a89aab16404e77/videokarty/?p=21"
        page = (re.search('\d+$', page)).group()
    except:
        page = 1
    for p in range(1, int(page) + 1):
        print(f'[+] Обработка страницы {p} ...')
        create_data(f'{url}&p={p}')


if __name__ == '__main__':
    try:
        # city(url, 'Москва')
        main(url)
    except Exception as ex:
        print(ex)
    finally:
        print(data_dict)
        with open('dns_data.json', 'w', encoding='utf-8') as file_data:
            json.dump(data_dict, file_data, indent=4, ensure_ascii=False)
        print('close')
        driver.close()
        driver.quit()





