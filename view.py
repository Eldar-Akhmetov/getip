from app import application
from flask import render_template, request, jsonify
from models import Computer
from fileRead import FileRead
from db_manager import DB_Manager
from datetime import datetime
import re

# Создаем таблицы в базе данных, если они уже существуют, то не чего не произойдет
DB_Manager.init_db()

# Создаем экземпляр класса FileRead, передаем путь до файла с разрешенными ip адресами
file = FileRead("data/files/allowed_ip.csv")

pattern = '(^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'

# Функция выводит ip адрес клиента при get запросе на корневую страницу


@application.route("/", methods=['GET'])
def index():
    # Если заголовок HTTP_X_FORWARDED_FOR пустой, значит мы не за прокси и выводим ip из заголовка REMOTE_ADDR
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ipaddress = request.environ['REMOTE_ADDR']
    # В остальных случаях HTTP_X_FORWARDED_FOR не пустой, выводим ip адрес из него
    else:
        try:
            ipaddress = re.match(
                pattern, request.environ['HTTP_X_FORWARDED_FOR']).group(0)
        except:
            ipaddress = None
    return render_template('index.html', ip=ipaddress)

# При получении post запроса на корневую страницу, соотносим ip клиента с массивом разрешенных ip адресов.
# Если ip клиента нет в массиве разрешенных адресов, то записываем hostname, username и ip полученные из
# post запроса в базу данных


@application.route("/", methods=['POST'])
def writeData():
    # Если заголовок HTTP_X_FORWARDED_FOR пустой, значит мы не за прокси и выводим ip из заголовка REMOTE_ADDR
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ipaddress = request.environ['REMOTE_ADDR']
    # В остальных случаях HTTP_X_FORWARDED_FOR не пустой, выводим ip адрес из него
    else:
        try:
            ipaddress = re.match(
                pattern, request.environ['HTTP_X_FORWARDED_FOR']).group(0)
        except:
            ipaddress = None
    # Если ip клиента нет в массиве разрешенных адресов, то записываем hostname, username и ip полученные из
    # post запроса в базу данных
    if ipaddress not in file.data:
        hostname = request.args.get('hostname')
        username = request.args.get('username')
        host = Computer(hostname=hostname, username=username,
                        ipaddress=ipaddress, created=datetime.now())
        DB_Manager.writeData(host)
    # После записи в базу данных возвращаем клиенту ответ с кодом 200
        return jsonify({'status': "0"}), 200
    # Если ip клиента в списке разрешенных, то просто возвращаем ответ с кодом 200
    else:
        return jsonify({'status': "0"}), 200
