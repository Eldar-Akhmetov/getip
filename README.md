# getip
Status of Last Deployment:<br>
<img src="https://github.com/Eldar-Akhmetov/getip/workflows/CI-CD-Pipeline-to-AWS-ElasticBeanstalk/badge.svg?branch=main"><br>

- [Описание](#описание)
- [Постановка задачи](#задачи)
- [Требования](#требования)
- [Запуск приложения](#запуск)
- [Если приложение за прокси сервером](#прокси)
- [Логика обработки HTTP запросов](#логика)
- [Скрипт на клиентских компьютерах](#клиент)
- [Описание классов приложения](#классы)

## Описание <a name="описание"></a>

Это простой проект на Flask выполняющий 2 задачи:
1) Отображение ip адреса клиента при входе через браузер на корневую страницу (Get запрос).
2) Клиенты (компьютеры на базе ОС Windows) по расписанию отправляют Post запросы, передавая имя компьютера и urername пользователя. Если ip адрес компьютера не содержится в списке адресов приложения, данные пользователя записываются в базу данных.

В качестве базы данных я использую __MySQL__.  
ORM используется __SQLAlchemy__.  
WSGI сервер __Gunicorn__.

## Постановка задачи <a name="задачи"></a>
В организации в которой я на данный момент работаю широко распространен удаленный режим работы. Для подключения к корпоративным ресурсам используется VPN шлюз. Подключение к VPN осуществляется только с корпоративных устройств, причем при подключении к интернету один из туннелей строится автоматически, следовательно с корпоративного устройства доступ в интернет выполняется через прокси сервер компании. Обойти это ограничение отключив необходимую службу для подключения к VPN могут только пользователи с правами локального администратора на ПК, коих в компании не мало, т.к. много IT специалистов на удаленке. Необходим ресурс во внешней сети на который будет подключаться ПК. Данный ресурс будет проверять ip адрес ПК и если ip не из пула глобальных адресов прокси сервера, он запишет в базу эти данные. Так как пользователи могут скомпрометировать корпоративное устройство.

## Требования <a name="требования"></a>
- python (3.4+)
- pip

## Запуск приложения <a name="запуск"></a>
#### 1) Клонировать проект на ваш сервер.  

По HTTPS ссылке: 
```
git clone https://github.com/Eldar-Akhmetov/getip.git
```
По SSH ссылке:
```
git clone git@github.com:Eldar-Akhmetov/getip.git
```
Или скачать ZIP архив: [getip.zip](https://github.com/Eldar-Akhmetov/getip/archive/refs/heads/main.zip)  

#### 2) Установить зависимости из файла [requirements.txt](https://github.com/Eldar-Akhmetov/getip/blob/main/requirements.txt)
```
pip install -r requirements.txt
```
> **Note**
> Вы можете создать виртуальную среду python и установить все зависимости в ней.  
Пример:
```
python -m venv venv-name
```
#### 3) Заполнить файл [allowed_ip.csv](https://github.com/Eldar-Akhmetov/getip-aws/blob/main/data/files/allowed_ip.csv) со списком разрешенных ip адресов. 
В данный файл вносятся глобальные ip адреса прокси серверов, с которых пользователи выходят в интернет или статические ip адреса пользователей, для исключения записи данных этих клиентов в базу. Путь к файлу: __data/files/allowed_ip.csv__.
Приложение проверяет наличие данного файла перед запуском, если файл отсутствует, будет сгенерировано исключение FileNotFoundError.
#### 4) Настройка точки входа для WSGI
Файл для передачи WSGI [main](https://github.com/Eldar-Akhmetov/getip-aws/blob/main/main.py).  
В настройках среды Python на AWS необходимо указать данный файл в строке __WSGI Path__  
> **Note**  
Для локального развертывания приложения необходимо установить WSGI, например __Gunicorn__.
Простой вариант добавить зависимость в файл [requirements.txt](https://github.com/Eldar-Akhmetov/getip/blob/main/requirements.txt) для развертывания на локальном сервере или в виртуальной среде. Пример: gunicorn==20.1.0.  

В AWS оркестратор Elastic Beanstalk сам создает unit для работы приложения как сервис, на локальном сервере вы можете самостоятельно создать unit файл.

Пример unit файла c WSGI gunicorn в виртуальной среде:
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
ExecStart=/var/www/flask-projects/getipvenv/bin/gunicorn --workers 4 --bind unix:getip.sock -m 007 main:application

[Install]
WantedBy=multi-user.target
```
В данном примере база mysql находится на этом же сервере, поэтому служба будет ожидать запуска службы mysqld, если ваша база расположена на стороннем сервере, уберите сервис "mysqld.service" из зависимостей в unit файле.

## Файл конфигурации config.py
В данном файле прописываются параметры подключения к базе данных, а так же можно включить/отключить debug режим для Flask.
Так как настроен [пайплайн](https://github.com/Eldar-Akhmetov/getip-aws/blob/main/.github/workflows/main.yml) для автоматического деплоя приложения в AWS Elastic Beanstalk, настройки для подключения к базе данных MySQL AWS RDS я получаю из переменных окружения в инстансе где разворачивается приложение. Если вы разворачиваете приложение в локальной среде задайте переменные окружения на вашем сервере вручную или заполните параметры в этом файле.

## Если приложение за прокси сервером <a name="прокси"></a>
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

## Логика обработки HTTP запросов <a name="логика"></a>
Логика обработки HTTP запросов описана в файле [view.py](https://github.com/Eldar-Akhmetov/getip-aws/blob/main/view.py)  
#### Если на корневую страницу пришел Get запрос:
1) Проверяем HTTP заголовок HTTP_X_FORWARDED_FOR, если он пустой, в переменную ipaddress передаем значение из заголовка REMOTE_ADDR.
В остальных случаях из заголовка HTTP_X_FORWARDED_FOR получаем первый ip адрес и передаем в переменную ipaddress (так как при наличии нескольких прокси в заголовке будет несколько адресов).
2) Выполняем перенаправления клиента на корневую страницу и передаем на нее его ip адрес в переменную ip.

#### Если на корневую страницу пришел Post запрос:
1) Проверяем HTTP заголовок HTTP_X_FORWARDED_FOR, если он пустой, в переменную ipaddress передаем значение из заголовка REMOTE_ADDR.
В остальных случаях из заголовка HTTP_X_FORWARDED_FOR получаем первый ip адрес и передаем в переменную ipaddress (так как при наличии нескольких прокси в заголовке будет несколько адресов).
2) Проверяем наличие ip адреса клиента в листе из прочитанного файла [allowed_ip.csv](https://github.com/Eldar-Akhmetov/getip-aws/blob/main/data/files/allowed_ip.csv).
Если ip адрес присутствует в листе, возвращаем клиенту json вида 'status': "0" и код 200. (Возврат клиенту json необходимо для отслеживания выполнения скрипта на клиентских ПК при помощи MS System Center Configuration Manager)  
Если ip адрес не найден в листе, будет выполнена запись ip клиента и данных переданных в post запросе в базу. Возвращаем клиенту json вида 'status': "0" и код 200. (Возврат клиенту json необходимо для отслеживания выполнения скрипта на клиентских ПК при помощи MS System Center Configuration Manager)

## Скрипт на клиентских компьютерах <a name="клиент"></a>
На клиентских машинах с ОС Windows по расписанию запускается простой скрипт выполняющий Post запрос на корневую страницу сайта.  
Пример простого запроса в клиентском скрипте при помощи командлета powershell __Invoke-WebRequest__:
```
$response = Invoke-WebRequest -Uri "https://getip.example.com?hostname=$($env:COMPUTERNAME)&username=$($env:USERNAME)" -Method Post | ConvertFrom-Json

if ($null -ne $response) {
    Exit $response.status
}

else {
    Exit 1
}
```

## Описание классов приложения <a name="классы"></a>
### Класс FileRead
Данный класс для работы с файлом allowed_ip.csv.
При создании экземпляра класса, нужно передать путь к файлу [allowed_ip.csv](https://github.com/Eldar-Akhmetov/getip-aws/blob/main/data/files/allowed_ip.csv). В конструкторе будет вызван метод __read__. Он проверяет наличие файла, если файл существует по указанному пути, он считает его построчно и вернет в поле data экземпляра класса list с ip адресами.  
Если файл отсутствует по указанному пути, будет сгенерировано исключение FileNotFoundError.  
В класса есть 2 геттера: __file_pathfile_path__ для получения пути до файла и __data__ возвращает лист с данными из файла.

### Модели базы данных, класс Computer
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

### Статический класс DB_Manager
Он предназначен для инициализации и записи в базу данных.
Метод __init_db__ выполняет метод create_all супер класса SQLAlchemy, создает таблицы и поля в базе данных.  
Метод __writeData__ выполняет запись в базу данных.



