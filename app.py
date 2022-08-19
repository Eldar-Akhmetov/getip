from flask import Flask
from config import Configuration
from flask_sqlalchemy import SQLAlchemy

# Создаем экземпляр класса Flask
app = Flask(__name__)

# Передаем конфиг с настройками
app.config.from_object(Configuration)

# Создаем объект нашей базы данных
db = SQLAlchemy(app)
