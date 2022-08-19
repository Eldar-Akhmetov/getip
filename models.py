# ---------------------------------------------------------------------
# Класс Computer описывает объект компьютер в базе данных
#
# Поля класса:
# id - Int, порядковый номер в таблице, является первичным ключем
# hostname - String, имя компьютера клиента
# username - String, имя пользователя клиента
# ipaddress - String, ip адресс клиента
# created - DateTime, дата и время создания объекта
#
# ---------------------------------------------------------------------
from app import db
import re


class Computer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(15))
    username = db.Column(db.String(140))
    ipaddress = db.Column(db.String(45))
    created = db.Column(db.DateTime)

    # Вызываем конструктор родительского класса и передаем ему все аргументы
    def __init__(self, *args, **kwargs) -> None:
        super(Computer, self).__init__(*args, **kwargs)
    # Метод для строкового отображения полей экземпляра класса

    def __repr__(self) -> str:
        return f'<id: {self.id}, hostname: {self.hostname}, username: {self.username}, ipaddress: {self.ipaddress}>'
