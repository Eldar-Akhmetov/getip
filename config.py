# ---------------------------------------------------------------------
# Класс Configuration, содержит настройки и параметры подключения к базе данных
# ---------------------------------------------------------------------
import os



db_name = os.environ['RDS_DB_NAME'],
db_user = os.environ['RDS_USERNAME'],
db_password = os.environ['RDS_PASSWORD'],
db_hostname = os.environ['RDS_HOSTNAME'],
db_port = os.environ['RDS_PORT'],
            
class Configuration(object):
    # Включить или отключить режим отладки
    DEBUG = True
    
    # Включение и отключение функции отслеживания изменения объектов
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Параметры для подключения к базе данных
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{db_user}:{db_password}@{db_hostname}:{db_port}/{db_name}'