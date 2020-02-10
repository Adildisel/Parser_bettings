"""
    Все необходимые данные сохраняются в файл difficult_option.csv в папке data.
"""

import logging
import time

import pyprind
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from logs import log
from save_data2file_csv import SaveDataToFile

class MySeleniumDifficult:
    def __init__(self):
        """
        -------------
        """
        self.file_name = 'difficult_option'
        self.save_file = SaveDataToFile(filename=self.file_name)
        self.driver = None

        self.initUi()
    
    def initUi(self):
        """ Формируем файл для сохранения loggers уровня  WARNING """
        log.main_log(name=self.file_name)
    
    def init_driver(self):
        """ Инициализируем экземпляр драйвера. Драйвер ждет 5 секунд перед следующим действием """
        logger = logging.getLogger('Betting.MySeleniumDifficult.init_driver')
        self.driver = webdriver.Firefox()
        self.driver.wait = WebDriverWait(self.driver, 5)
        logger.info('Инициализация экземпляра драйвера прошла успешно!')
    
    def look_up(self, url):
        """ Открывает страницу Отзывов из iTunes в Firefox"""
        logger = logging.getLogger('Betting.MySeleniumDifficult.look_up')
        try:
            self.driver.get(url)
        except Exception as error:
            logger.warning(str(error))
        else:
            logger.info('Страница успешно загружена!')

    def scroll_to_the_end_of_the_page(self):
        """ Для того что бы получить новыйе отзывы необходимо проскролить страницу до конца,
            каждое обновление дает плюс 10 отзывов, общее количество отзывов около 1600. 
            задержка в 1.5 секунд задана чтоб страница успела загрузить комментарии.
        """
        logger = logging.getLogger('Betting.MySeleniumDifficult.scroll_to_the_end_of_the_page')
        page_scroll = 160
        bar = pyprind.ProgBar(page_scroll, title='Идет обновление страниц пожалуйста подождите...')
        try:
            for i in range(page_scroll):
                scroll_element = self.driver.find_element_by_xpath("//div[@id='modal-container']")
                self.driver.execute_script("arguments[0].scrollIntoView();", scroll_element)
                time.sleep(1.5)
                bar.update()
        except Exception as error:
            logger.warning(str(error))
        else:
            logger.info('Загрузка страниц с отзывами закончена!')
    
    def get_elements_from_feedbacks(self):
        """ Ждем пока будет найдены элементы класса -single(класс отдельного блока отзыыва)-.
            Если класс не будет найден в течении 5 секунд возникнет исключение.
            Далее Находим элементы:
                - Имя букмекера (по умолчанию LigaStavok).
                - Источник отзыва (сайт https://apps.apple.com)
                - Имя автора.
                - Дата.
                - Оценка.
                - Заголовок.
                - Текст.
        """
        logger = logging.getLogger('Betting.MySeleniumDifficult.get_elements_from_feedbacks')
        all_list_feedbacks = self.driver.wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "l-content-width")
        ))
        list_feedbacks = all_list_feedbacks.find_elements_by_class_name('l-column--grid')
        dict_data = {'name_bookmaker': 'LigaStavok', 
                    'feedback_source': 'https://apps.apple.com/ru/app/%D0%BB%D0%B8%D0%B3%D0%B0-%D1%81%D1%82%D0%B0%D0%B2%D0%BE%D0%BA-%D1%81%D1%82%D0%B0%D0%B2%D0%BA%D0%B8-%D0%BD%D0%B0-%D1%81%D0%BF%D0%BE%D1%80%D1%82/id1065803457#see-all/reviews', 
                    }
        bar = pyprind.ProgBar(len(list_feedbacks), title='Идет сохранение данных в файл.')
        self.save_file.clear_file() # При необходимости предварительно очистить файл для DataSet
        for feedback in list_feedbacks:
            try:
                name_auth = feedback.find_element_by_class_name('we-customer-review__user').text
                date_forming = feedback.find_element_by_class_name('we-customer-review__date').text

                rating_element = feedback.find_element_by_class_name('we-customer-review__rating')
                rating = rating_element.get_attribute('aria-label').split()[0]
                title_feedback = feedback.find_element_by_class_name('we-customer-review__title').text
                text_feedback = feedback.find_element_by_class_name('we-customer-review__body'
                                                                    ).find_element_by_tag_name('p'
                                                                    ).text
            except Exception as error:
                dict_data['name_auth'] = ''
                dict_data['date_forming']  = ''
                dict_data['rating'] = ''
                dict_data['title_feedback'] = ''
                dict_data['text_feedback'] = ''

                logger.warning(str(error))
            else:
                dict_data['name_auth'] = name_auth
                dict_data['date_forming']  = date_forming
                dict_data['rating'] = rating
                dict_data['title_feedback'] = title_feedback
                dict_data['text_feedback'] = text_feedback
            finally:
                bar.update()
                self.save_file_to_csv(dict_data)
        logger.info('Сохранение данных в файл завершено!')  
        
    
    def save_file_to_csv(self, data):
        """ Переход на внешний модуль для сохранения данных в  csv формате"""
        self.save_file.save_to_csv(data)

def main():
    url = r'https://apps.apple.com/ru/app/%D0%BB%D0%B8%D0%B3%D0%B0-%D1%81%D1%82%D0%B0%D0%B2%D0%BE%D0%BA-%D1%81%D1%82%D0%B0%D0%B2%D0%BA%D0%B8-%D0%BD%D0%B0-%D1%81%D0%BF%D0%BE%D1%80%D1%82/id1065803457#see-all/reviews'

    my_selenium = MySeleniumDifficult()
    my_selenium.init_driver()
    my_selenium.look_up(url)
    my_selenium.scroll_to_the_end_of_the_page()
    my_selenium.get_elements_from_feedbacks()

    time.sleep(1)
    my_selenium.driver.quit()
    
if __name__ == '__main__':
    main()
    