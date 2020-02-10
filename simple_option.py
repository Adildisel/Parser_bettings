"""
    Все необходимые данные сохраняются в файл simple_option.csv в папке data.
"""
import time 
import logging

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotVisibleException, ElementClickInterceptedException
import pyprind

from save_data2file_csv import SaveDataToFile
from logs import log

class MySeleniumSimple:
    def __init__(self):
        """
        -------------
        """
        self.file_name = 'simple_option'
        self.save_file = SaveDataToFile(filename=self.file_name)
        self.driver = None

        self.initUi()
    
    def initUi(self):
        """ Формируем файл для сохранения loggers уровня  WARNING """
        log.main_log(name=self.file_name)

    def init_driver(self):
        """ Инициализируем экземпляр драйвера. Драйвер ждет 5 секунд перед следующим действием """
        logger = logging.getLogger('Betting.MySeleniumSimple.init_driver')
        self.driver = webdriver.Firefox()
        self.driver.wait = WebDriverWait(self.driver, 5)
        logger.info('Инициализация экземпляра драйвера прошла успешно!')

    def get_all_feedbacks(self):
        """ Обработка автоматического нажатия кнопки для получения всех страниц с отзывами пользователей. 
            В переменную page мы сохраняем количество страниц.
            Далее в цикле ждем пока все необходимые элементы полностью загрузятся
            После чего жмем кнопку 
        """ 
        logger = logging.getLogger('Betting.MySeleniumSimple.get_all_feedbacks')
        element = self.driver.find_element_by_xpath("//button[@id='all-feedbacks-more-btn']")
        page = element.get_attribute('data-total-pages')
        bar = pyprind.ProgBar(int(page), title='Идет обновление страниц пожалуйста подождите...')
        for i in range(int(page)):
            self.driver.wait.until(EC.visibility_of_all_elements_located(
                (By.CLASS_NAME, 'single')
            ))
            self.driver.execute_script("arguments[0].click();", element)
            bar.update()
        logger.info('Загрузка страниц с отзывами закончена!')

    def get_elements_from_feedbacks(self):
        """ Ждем пока будет найдены элементы класса -single(класс отдельного блока отзыыва)-.
            Если класс не будет найден в течении 5 секунд возникнет исключение.
            Далее Находим элементы:
                - Имя букмекера (по умолчанию LigaStavok).
                - Источник отзыва (сайт https://bookmaker-ratings.ru/).
                - Имя автора.
                - Дата.
                - Оценка.
                - Текст.
        """
        logger = logging.getLogger('Betting.MySeleniumSimple.get_elements_from_feedbacks')
        try:
            all_list_feedbacks = self.driver.wait.until(EC.presence_of_element_located(
                (By.ID, "all-feedbacks-list")
            ))
            list_feedbacks = all_list_feedbacks.find_elements_by_class_name('single')
            dict_data = {'name_bookmaker': 'LigaStavok', 
                        'feedback_source': 'https://bookmaker-ratings.ru/review/obzor-bukmekerskoj-kontory-ligastavok/all-feedbacks/', 
                        }
            bar = pyprind.ProgBar(len(list_feedbacks), title='Идет сохранение данных в файл.')
            self.save_file.clear_file() # При необходимости предварительно очистить файл для DataSet
            for feedback in list_feedbacks:
                try:
                    name_auth = feedback.find_element_by_class_name('namelink').text
                    date_forming = feedback.find_element_by_class_name('date').text
                    rating = feedback.find_element_by_class_name('num').text
                    text_feedback = feedback.find_element_by_class_name('content').text
                except Exception as err:
                    dict_data['name_auth'] = ''
                    dict_data['date_forming']  = ''
                    dict_data['rating'] = ''
                    dict_data['text_feedback'] = ''
                    logger.warning(str(err))
                    logger.info('Element not found!')
                else:
                    dict_data['name_auth'] = name_auth
                    dict_data['date_forming']  = date_forming
                    dict_data['rating'] = rating
                    dict_data['text_feedback'] = text_feedback
                finally:
                    bar.update()
                self.save_file_to_csv(dict_data)
            logger.info('Сохранение данных в файл завершено!')         
        except TimeoutException:
            logger.info('Page not found')
    
    def save_file_to_csv(self, data):
        """ Переход на внешний модуль для сохранения данных в  csv формате"""
        self.save_file.save_to_csv(data)

    def lookup(self, url):
        """ Открывает страницу Отзывов в  Firefox"""
        logger = logging.getLogger('Betting.MySeleniumSimple.lookup')
        self.driver.get(url)
        logger.info('Страница успешно загружена!')
        
def main():
    url = 'https://bookmaker-ratings.ru/review/obzor-bukmekerskoj-kontory-ligastavok/all-feedbacks/'
    my_selenium = MySeleniumSimple()
    my_selenium.init_driver()
    my_selenium.lookup(url)
    my_selenium.get_all_feedbacks()
    my_selenium.get_elements_from_feedbacks()

    time.sleep(1)
    my_selenium.driver.quit()

if __name__ == "__main__":
    main()