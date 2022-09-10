# getip-aws



Status of Last Deployment:<br>
<img src="https://github.com/Eldar-Akhmetov/getip-aws/workflows/CI-CD-Pipeline-to-AWS-ElasticBeanstalk/badge.svg?branch=main"><br>

## Описание

Это простой проект на Flask выполняющий 2 задачи:
1) Отображение ip адреса клиента при входе через браузер на корневую страницу (Get запрос).
2) Клиенты (компьютеры на базе ОС Windows) по расписанию отправляют Post запросы, передавая имя компьютера и urername пользователя. Если ip адрес компьютера не содержится в списке адресов приложения, данные пользователя записываются в базу данных.

В качестве базы данных я использую __MySQL__.  
ORM используется __SQLAlchemy__.

## Постановка задачи
В организации в которой я на данный момент работаю широко распространен удаленный режим работы. Для подключения к корпоративным ресурсам используется VPN шлюз. Подключение к VPN осуществляется только с корпоративных устройств, причем при подключении к интернету один из туннелей строится автоматически, следовательно с корпоративного устройства доступ в интернет выполняется через прокси сервер компании. Обойти это ограничение отключив необходимую службу для подключения к VPN могут только пользователи с правами локального администратора на ПК, коих в компании не мало, т.к. много IT специалистов на удаленке. Необходим ресурс во внешней сети на который будет подключаться ПК. Данный ресурс будет проверять ip адрес ПК и если ip не из пула глобальных адресов прокси сервера, он запишет в базу эти данные. Так как пользователи могут скомпрометировать корпоративное устройство.

## Точка входа для WSGI.
Файл для передачи WSGI [main](https://github.com/Eldar-Akhmetov/getip-aws/blob/main/main.py).  
В настройках среды Python на AWS необходимо указать данный файл в строке __WSGI Path__  
Для старта приложения на локальном сервере вы можете создать unit.

Пример unit файла c WSGI gunicorn:
```
[Unit]
Description=Gunicorn instance to serve getip
After=network.target
After=mysqld.service
Requires=mysqld.service

[Service]
User=webadmin
Group=nginx
WorkingDirectory=/var/www/flask-projects/getip
Environment="PATH=/var/www/flask-projects/getipvenv/bin"
OOMScoreAdjust=-100
ExecStart=/var/www/flask-projects/getipvenv/bin/gunicorn --workers 4 --bind unix:getip.sock -m 007 main:app

[Install]
WantedBy=multi-user.target
```
В данном примере база mysql находится на этом же сервере, поэтому служба будет ожидать запуска службы mysqld, если ваша база расположена на стороннем сервере, уберите "mysqld.service" из зависимостей.

## Файл конфигурации config.py
В данном файле прописываются параметры подключения к базе данных, а так же можно включить/отключить debug режим для Flask.
Так как настроен [пайплайн](https://github.com/Eldar-Akhmetov/getip-aws/blob/main/.github/workflows/main.yml) для автоматического деплоя приложения в AWS Elastic Beanstalk, настройки для подключения к базе данных MySQL AWS RDS я получаю из переменных окружения в инстансе где разворачивается приложение. Если вы разворачиваете приложение в локальной среде задайте переменные окружения на вашем сервере вручную или заполните параметры в этом файле.

## Если приложение за прокси сервером
Если запросы на WSGI проксируются с балансировщика например nginx, то на бэкенд необходимо передавать HTTP заголовок __HTTP_X_FORWARDED_FOR__.
В настройках по умолчанию среды на AWS используется nginx и данный заголовок уже добавлен.

Пример конфигурации сервера на nginx в локальной среде:
```
server {
    listen 443 ssl;
    server_name getip.example.com;
    ssl_certificate     /etc/nginx/ssl/certificate_example.crt;
    ssl_certificate_key /etc/nginx/ssl/certificate_example.key;
    access_log /var/log/nginx/getip/access.log;
    error_log /var/log/nginx/getip/error.log;

    location / {
        proxy_pass http://unix:/var/www/flask-projects/getip/getip.sock;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;    
        }
}
```

## Список разрешенных ip адресов, файл allowed_ip.csv
Список разрешенных ip адресов хранится в файле [allowed_ip.csv](https://github.com/Eldar-Akhmetov/getip-aws/blob/main/data/files/allowed_ip.csv), путь к файлу: data/files/allowed_ip.csv.
В данный файл вносятся глобальные ip адреса прокси сервера, с которого пользователи выходят в интернет.
Приложение проверяет наличие данного файла перед запуском, если файл отсутствует будет сгенерировано исключение FileNotFoundError.

## Класс FileRead
Данный класс для работы с файлом allowed_ip.csv.
При создании экземпляра класса, нужно передать путь к файлу [allowed_ip.csv](https://github.com/Eldar-Akhmetov/getip-aws/blob/main/data/files/allowed_ip.csv). В конструкторе будет вызван метод __read__. Он проверяет наличие файла, если файл существует по указанному пути, он считает его построчно и вернет в поле data экземпляра класса list с ip адресами.  
Если файл отсутствует по указанному пути, будет сгенерировано исключение FileNotFoundError.  
В класса есть 2 геттера: __file_pathfile_path__ для получения пути до файла и __data__ возвращает лист с данными из файла.

## Модели базы данных, файл models.py
В данном приложении описана одна простая модель, классом Computer.
Он наследуется от класса SQLAlchemy.

Поля класса Computer:
|  Имя столбца  |   Тип данных    |  Primary key  |
|:------------- |:---------------:| -------------:|
|      id       |     Integer     |      Yes      |
|   hostname    |     String      |       No      |
|   username    |     String      |       No      |
|   ipaddress   |     String      |       No      |
|    created    |    DateTime     |       No      |

Метод __repr__ выдает строковое представление объекта класса:
id: {self.id}, hostname: {self.hostname}, username: {self.username}, ipaddress: {self.ipaddress}.

## Статический класс DB_Manager
Он предназначен для инициализации и записи в базу данных.
Метод __init_db__ выполняет метод create_all супер класса SQLAlchemy, создает таблицы и поля в базе данных.  
Метод __writeData__ выполняет запись в базу данных.

## Логика обработки HTTP запросов
Логика обработки HTTP запросов описана в файле [view.py](https://github.com/Eldar-Akhmetov/getip-aws/blob/main/view.py)  
#### Если на корневую страницу пришел Get запрос:
1) Проверяем HTTP заголовок __HTTP_X_FORWARDED_FOR__, если он пустой, в переменную __ipaddress__ передаем значение из заголовка __REMOTE_ADDR__.
В остальных случаях из заголовка __HTTP_X_FORWARDED_FOR__ получаем первый ip адрес и передаем в переменную __ipaddress__ (так как при наличии нескольких прокси в заголовке будет несколько адресов).
2) Выполняем перенаправления клиента на корневую страницу и передаем на нее его ip адрес в переменную __ip__.

#### Если на корневую страницу пришел Post запрос:
1) Проверяем HTTP заголовок __HTTP_X_FORWARDED_FOR__, если он пустой, в переменную __ipaddress__ передаем значение из заголовка __REMOTE_ADDR__.
В остальных случаях из заголовка __HTTP_X_FORWARDED_FOR__ получаем первый ip адрес и передаем в переменную __ipaddress__ (так как при наличии нескольких прокси в заголовке будет несколько адресов).
2) Проверяем наличие ip адреса клиента в листе из прочитанного файла [allowed_ip.csv](https://github.com/Eldar-Akhmetov/getip-aws/blob/main/data/files/allowed_ip.csv).
Если ip адрес присутствует в листе, возвращаем клиенту json вида 'status': "0" и код 200. (Возврат клиенту json необходимо для отслеживания выполнения скрипта на критских ПК при помощи MS System Center Configuration Manager)  
Если ip адрес не найден в листе, будет выполнена запись ip клиента и данных переданных в post запросе в базу. Возвращаем клиенту json вида 'status': "0" и код 200. (Возврат клиенту json необходимо для отслеживания выполнения скрипта на критских ПК при помощи MS System Center Configuration Manager)

## Скрипт на клиентских машинах
На клиентских машинах с ОС Windows по расписанию запускается простой скрипт выполняющий Post запрос на корневую страницу сайта.  
Пример простого запроса в клиентском скрипте при помощи командлета powershell __Invoke-WebRequest__:
```
$response = Invoke-WebRequest -Uri "https://getip.example.com?hostname=$($env:COMPUTERNAME)&username=$($env:USERNAME)" -Method Post | ConvertFrom-Json
```




