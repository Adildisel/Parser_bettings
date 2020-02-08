import logging.config

def main_log(name=''):
    dictLogConfig = {
        'version': 1,
        'formatters':{
            'consoleFormatter':{
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            },
            'fileFormatter':{
                'format': '%(asctime)s - %(name)s - %(message)s',
            },
        },
        'handlers':{
            'fileHandler':{
                'class': 'logging.FileHandler',
                'formatter': 'fileFormatter',
                'filename': 'logs/log_files/config_{0}'.format(name),
                'level': 'WARNING',
            },
            'consoleHandler':{
                'class': 'logging.StreamHandler',
                'formatter': 'consoleFormatter',
                'level': 'INFO',
            },
        },
        'loggers':{
            'Betting':{
                'handlers':['fileHandler', 'consoleHandler', ],
                'level': 'INFO',
            }
        }
    }

    logging.config.dictConfig(dictLogConfig)