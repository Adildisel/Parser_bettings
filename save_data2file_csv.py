import csv
import os
import logging

dirname = os.path.dirname(__file__)

class SaveDataToFile:
    def __init__(self, filename='filename'):
        """
        --------
        """
        self.filename = filename

    def clear_file(self):
        """"""
        with open(os.path.join(dirname, 
                            'data/{}.csv'.format(self.filename)),
                            'w',
                            ) as file:
            csv.writer(file)

    def save_to_csv(self, data):
        """"""
        logger = logging.getLogger('Betting.SaveDataToFile.save_to_csv')
        with open(os.path.join(dirname, 
                            'data/{}.csv'.format(self.filename)),
                            'a',
                            ) as file:
            writer = csv.writer(file)
            try:
                writer.writerow((data.values()))
            except AttributeError as error:
                logger.info(str(error))

if __name__ == "__main__":
    app = SaveDataToFile()
    app.clear_file()
    app.save_to_csv()