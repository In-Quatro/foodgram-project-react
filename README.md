#  Foodgram — социальная сеть для обмена рецептами. 

## Описание

Проект создан для обмена рецептами.
Проект развернут на хосте https://fgrm-shubenkov.ddns.net/recipes

### Установка

1. Склонируйте репозиторий на свой компьютер
2. Создайте в корне проекта файл `.env`, используя свои данные. Пример можно посмотреть в файле `.env.example`.

#### Процесс создания Docker-образов

1. Вместо `username` используйте свой логин на DockerHub:

    ```
    cd frontend
    docker build -t username/foodgram_frontend .
    cd ../backend
    docker build -t username/foodgram_backend .
    cd ../nginx
    docker build -t username/foodgram_gateway . 
    ```

2. Отправьте собранные образы фронтенда, бэкенда и Nginx на Docker Hub:

    ```
    docker push username/foodgram_frontend
    docker push username/foodgram_backend
    docker push username/foodgram_gateway
    ```
    
### Deploy на сервере

1. Произведите подключение своему удаленному серверу

    ```bash
    ssh -i path_to_SSH/SSH_KEY_NAME username@username@server_ip 
    ```

2. Создайте на сервере директорию `foodgram`:

    ```
    mkdir foodgram
    ```

3. Произведите установку Docker Compose на сервере:

    ```
    sudo apt update
    sudo apt install curl
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo apt install docker-compose
    ```

4. Скопируйте на сервер в директорию `foodgram` файлы `docker-compose.production.yml` и `.env`:

    ```
    scp -i path_to_SSH/SSH_name docker-compose.production.yml username@server_ip:/home/username/foodgram/docker-compose.production.yml
    ```
    
    ```
    scp -i path_to_SSH/SSH_name .env username@server_ip:/home/username/foodgram/.env
    ```
    
      - path_to_SSH — путь к файлу с SSH-ключом;
      - SSH_name — имя файла с SSH-ключом (без расширения);
      - username — ваше имя пользователя на сервере;
      - server_ip — IP вашего сервера.
  
5. Запустите Docker Compose из директории `foodgram` в режиме демона:

     ```
     sudo docker compose -f docker-compose.production.yml up -d
     ```
    
6. Выполните миграции, соберите статические файлы бэкенда и скопируйте их в /backend_static/static/:

     ```
     sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
     sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
     sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /static/static/
     ```

7. Откройте конфигурационный файл Nginx в редакторе nano:

    ```
    sudo nano /etc/nginx/sites-enabled/default
    ```

8. Замените настройки `location` в секции `server`:

    ```
    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:9000;
    }
    ```

9. Чтобы убедиться, что в конфиге Nginx нет ошибок — выполните команду проверки конфигурации::

    ```
    sudo nginx -t
    ```

    Если всё в порядке, то в консоли появится следующий ответ:

    ```
    nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
    nginx: configuration file /etc/nginx/nginx.conf test is successful
    ```

10. Перезагрузите конфиг Nginx:

    ```
    sudo service nginx reload
    ```

### Настройка CI/CD

Готовый Workflow находится в директории  `.github/workflows/main.yml` проекта.
Чтобы его использовать необходимо создать `secrets` в GitHub Actions:

`DockerHub`
 - DOCKER_USERNAME - имя пользователя DockerHub
 - DOCKER_PASSWORD - пароль пользователя DockerHub

`Server `
 - HOST - IP-адрес сервера
 - USER - имя пользователя сервера

`SSH`
 - SSH_KEY - приватный SSH-ключ
 - SSH_PASSPHRASE - пароль для SSH-ключа

`Telegram`
 - TELEGRAM_TO - ID аккаунта от telegram (использовать @userinfobot)
 - TELEGRAM_TOKEN - токен бота (использовать @BotFather)



### Технологии
 - Python 3.19
 - Django 3.2.3
 - Django Rest Framework 3.12.4
 - PostgreSQL 13.10

### Автор
[Shubenkov Aleksey](https://github.com/In-Quatro)
