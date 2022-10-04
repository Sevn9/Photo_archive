import logging
import fire
import boto3
import os
from botocore.exceptions import ClientError
import configparser


def hello():
    name = input("Введите имя: ")
    # print('-----------------------------------------------')
    return f'Hello {name}!'


# Отправка фотографий в облачное хранилище
# cloudphoto upload --album ALBUM [--path PHOTOS_DIR]
# где --path = директория где лежат файлы для загрузки, album - название альбома в облаке
def upload(album, path=None):
    if path is None:
        # используем текущий каталог
        newPath = './'
    else:
        # используем выбранный каталог
        newPath = path
    print('В выбранном каталоге найдены следующие файлы: ')
    for filename in os.listdir(newPath):
        print(filename)
    print('----------------------------------')

    # работает только из основной директории
    # s3.upload_file(f'{items[0]}', 'itis-vvot-30', uploadTemp)

    # загружаем файлы найденные в папке
    try:
        for filename in os.listdir(newPath):
            print('uploading file ' + filename)
            uploadDir = album + '/' + filename
            s3.put_object(Bucket='itis-vvot-30', Key=uploadDir, Body=filename)
        print('uploaded')
        print('----------------------------------')
    except ClientError as e:
        logging.error(e)
        return False
    return True


# Загрузка фотографий из облачного хранилища
# cloudphoto download --album ALBUM [--path PHOTOS_DIR]
# album = из какого альбома, path = куда загружать
def download(album, path=None):
    if path is None:
        # используем текущий каталог
        newPath = './'
    else:
        # используем выбранный каталог
        newPath = path
    try:
        s3.download_file('itis-vvot-30', f'{album}/pts.png', f'{newPath}/pts1.png')
    except ClientError as e:
        logging.error(e)
        return False
    return True


# Просмотр списка альбомов и фотографий в альбоме
# cloudphoto list [--album ALBUM]
def list(album=None):
    if album is None:
        print('Список альбомов: ')
        album_set = set()
        sites = []
        albums = []
        for key in s3.list_objects(Bucket=bucket_name)['Contents']:
            album_set.add(key["Key"].split("/")[0])

        # print(album_set)
        for item in album_set:
            my_str = str(item)
            if my_str.endswith('.html'):
                sites.append(my_str)
            else:
                albums.append(my_str)
        print(albums)
        print('Список html страниц: ')
        print(sites)
        print('----------------------------------')
    else:
        print('Список альбомов: ')
        album_set = set()
        for key in s3.list_objects(Bucket=bucket_name)["Contents"]:
            album_set.add(key["Key"].split("/")[0])
        print(album_set)
        print('----------------------------------')

        print(f'Список фотографий в альбоме {album}: ')
        photos = []
        for key in s3.list_objects(Bucket=bucket_name, Prefix=album + "/",
                                   Delimiter="/", )['Contents']:
            photos.append(key["Key"].split("/")[1])
            print(photos)
            # print(key['Key'] + "\n")
        print('----------------------------------')


# Удаление альбомов и фотографий
# cloudphoto delete --album ALBUM [--photo PHOTO]
def delete(album, photo=None):
    # Удалить весь альбом
    if photo == None:
        try:
            forDeletion = [
                {"Key": key.get('Key')}
                for key in s3.list_objects(
                    Bucket=bucket_name,
                    Prefix=album + "/",
                    Delimiter="/",
                )["Contents"]
            ]
            response = s3.delete_objects(Bucket=bucket_name, Delete={'Objects': forDeletion})
            print(f'Альбом {album} был успешно удален!')
            print('----------------------------------')
        except ClientError as e:
            logging.error(e)
            return False
        return True

    else:
        # Удалить фото
        try:
            forDeletion = [{'Key': f'{album}/{photo}'}]
            response = s3.delete_objects(Bucket=bucket_name, Delete={'Objects': forDeletion})
            print(f'фото {photo} в альбоме {album} было успешно удалено!')
            print('----------------------------------')
        except ClientError as e:
            logging.error(e)
            return False
        return True


#  Генерация и публикация веб-страниц фотоархива
# cloudphoto mksite
def mksite():
    # вывести список имен альбомов
    print('Список альбомов: ')
    album_set = set()
    sites = []
    albums = []
    for key in s3.list_objects(Bucket=bucket_name)['Contents']:
        album_set.add(key["Key"].split("/")[0])

    # print(album_set)
    for item in album_set:
        my_str = str(item)
        if my_str.endswith('.html'):
            sites.append(my_str)
        else:
            albums.append(my_str)
    print(albums)
    print('Список html страниц: ')
    print(sites)
    # Генерация страниц альбомов
    albumCh1 = '<!doctype html><html><head>' \
               '<link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/galleria/1.6.1/themes/classic/galleria.classic.min.css" />' \
               '<style> .galleria{ width: 960px; height: 540px; background: #000 }</style>' \
               '<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>' \
               '<script src="https://cdnjs.cloudflare.com/ajax/libs/galleria/1.6.1/galleria.min.js"></script>' \
               '<script src="https://cdnjs.cloudflare.com/ajax/libs/galleria/1.6.1/themes/classic/galleria.classic.min.js"></script>' \
               '</head><body><div class="galleria">'

    albumCh2 = '<img src="URL_на_фотографию_1_в_альбоме" data-title="Имя_исходного_файла_фотографии_1">' \
               '<img src="URL_на_фотографию_2_в_альбоме" data-title="Имя_исходного_файла_фотографии_2">' \
               '<img src="..." data-title="...">' \
               '<img src="URL_на_фотографию_N_в_альбоме" data-title="Имя_исходного_файла_фотографии_N">'

    albumCh3 = '</div><p>Вернуться на <a href="index.html">главную страницу</a> фотоархива</p>' \
               '<script>(function() {Galleria.run(\'.galleria\');}());</script> </body></html>'
    print(albumCh3)

    # создать переменную с кодом страницы index и error
    indexCh1 = '<!doctype html> <html> <head> <meta charset="utf-8"> ' \
               '<title>Фотоархив</title> </head> <body> <h1>Фотоархив</h1> <ul>'

    indexCh2 = '<li><a href="album1.html">Имя альбома 1</a></li>' \
            '<li><a href="album2.html">Имя альбома 2</a></li>' \
            '<li><a href="...">...</a></li>' \
            '<li><a href="album{N}.html">Имя альбома N</a></li>'
    indexCh3 = '</ul> </body'
    index = indexCh1 + indexCh2 + indexCh3
    error = '<!doctype html> <html> <head> <meta charset="utf-8"> <title>Фотоархив</title>' \
            '</head> <body><h1>Ошибка</h1><p>Ошибка при доступе к фотоархиву. Вернитесь на <a href="index.html">главную страницу</a> фотоархива.</p>' \
            '</body></html>'
    # сгенерировать index и error
    file = open("index.html", "w", encoding="utf-8")
    file.write(index)
    file.close()
    file = open("error.html", "w", encoding="utf-8")
    file.write(error)
    file.close()

    # загружаем файлы найденные в папке
    newPath = './'
    for filename in os.listdir(newPath):
        if filename == 'index.html' or filename == 'error.html':
            print('uploading file ' + filename)
            #s3.upload_file(filename, 'itis-vvot-30', filename)
    print('uploaded')
    print('----------------------------------')

    # Проверить
    # Define the website configuration
    website_configuration = {
        'ErrorDocument': {'Key': 'error.html'},
        'IndexDocument': {'Suffix': 'index.html'},
    }
    # Set the website configuration
    s3.put_bucket_website(Bucket=bucket_name,
                          WebsiteConfiguration=website_configuration)
    result = s3.get_bucket_website(Bucket=bucket_name)
    print(f'https://{bucket_name}.website.yandexcloud.net/')
    return result


def init():
    num = input('Конфиг. файл уже создан? 1 - да, 0 - нет: ')
    if (num == 0):
        bucket = input("Введите название bucket: ")
        awsAccessKeyId = input("Введите aws access key id: ")
        awsSecretAccessKey = input("Введите aws secret access key: ")

        # сохраняем в конфигурационный файл
        dirRoot = os.getcwd()
        print('Текущая деректория:', dirRoot)
        dirNeed = dirRoot + "/.config/cloudphoto/"
        if not os.path.isdir(dirNeed):
            os.makedirs(dirNeed)
        # создать новый текстовый файл
        text_file = open(dirNeed + "/cloudphotorc.ini", "w")
        # Запись текста в этот файл
        text_file.write(
            '[default]' + "\n" + 'bucket = ' + bucket + "\n" + 'aws_access_key_id = ' + awsAccessKeyId + "\n"
            + 'aws_secret_access_key = ' + awsSecretAccessKey + "\n" + 'region = ru-central1-a' + "\n" +
            'endpoint_url = https://storage.yandexcloud.net')
    return 'init завершен'


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    session = boto3.session.Session()
    dirRoot = os.getcwd()
    dirNeed = dirRoot + "/.config/cloudphoto/"
    # проверка на существование ini файла
    if os.path.isfile(f'{dirNeed}/cloudphotorc.ini'):
        config = configparser.ConfigParser()  # создаём объекта парсера
        config.read(f"{dirNeed}/cloudphotorc.ini")  # читаем конфиг

        # нужна проверка на существование бакета и если нет создавать с публичным доступом
        s3 = session.client(
            's3',
            aws_access_key_id=config["default"]["aws_access_key_id"],
            aws_secret_access_key=config["default"]["aws_secret_access_key"],
            region_name=config["default"]["region"],
            endpoint_url=config["default"]["endpoint_url"],
        )
        bucket_name = config["default"]["bucket"]
        print('----------------------------------')
        print('Доступные бакеты: ')
        for bucket in s3.list_buckets()['Buckets']:
            print(bucket['Name'])
        print('----------------------------------')
        fire.Fire()
    else:
        print('Конфиг не существует, используйте команду init')
