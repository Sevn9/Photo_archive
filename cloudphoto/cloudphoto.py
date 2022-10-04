import logging
import fire
import boto3
import os
from botocore.exceptions import ClientError
import configparser

# Для теста;)
def hello():
    name = input("Введите имя: ")
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


    # загружаем файлы найденные в папке
    try:
        for key in os.listdir(newPath):
            print('uploading file ' + key)
            uploadDir = album + '/' + key
            filename = newPath + '/' + str(key)
            s3.upload_file(filename, bucket_name, uploadDir)

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
        # Загрузка из альбома
        for key in s3.list_objects(
                Bucket=bucket_name, Prefix=album + "/", Delimiter="/")["Contents"]:
            s3.download_file(Bucket=bucket_name,
                             Key=key['Key'],
                             Filename=os.path.join(newPath, key['Key'].split('/')[1]))

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
    url = f'https://{bucket_name}.website.yandexcloud.net/'
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
    albumCh1 = '<!doctype html><html><head> <meta charset="utf-8"> ' \
               '<link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/galleria/1.6.1/themes/classic/galleria.classic.min.css" />' \
               '<style> .galleria{ width: 960px; height: 540px; background: #000 }</style>' \
               '<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>' \
               '<script src="https://cdnjs.cloudflare.com/ajax/libs/galleria/1.6.1/galleria.min.js"></script>' \
               '<script src="https://cdnjs.cloudflare.com/ajax/libs/galleria/1.6.1/themes/classic/galleria.classic.min.js"></script>' \
               '</head><body><div class="galleria">'

    albumCh2 = ''

    # достать фото из каждого альбома и засунуть в страницу альбома
    for item in albums:
        album = item
        print(f'Список фотографий в альбоме {album}: ')
        photos = []
        for key in s3.list_objects(Bucket=bucket_name, Prefix=album + "/",
                                   Delimiter="/", )['Contents']:
            photo = key["Key"].split("/")[1]
            photos.append(photo)
            albumCh2 = albumCh2 + f'<img src="https://{bucket_name}.website.yandexcloud.net/{item}/{photo}" data-title="{photo}">'
        print(photos)
        print('----------------------------------')

    albumCh3 = '</div><p>Вернуться на <a href="index.html">главную страницу</a> фотоархива</p>' \
               '<script>(function() {Galleria.run(\'.galleria\');}());</script> </body></html>'

    album = albumCh1 + albumCh2 + albumCh3

    indexCh2 = ''
    itter = 0
    for item in albums:
        itter = itter + 1
        indexCh2 = indexCh2 + f'<li><a href="album{itter}.html">{item}</a></li>'
        file = open(f"album{itter}.html", "w", encoding="utf-8")
        file.write(album)
        file.close()

    newPath = './'
    # Загрузить страницы альбомов
    for i in range(len(albums)):
        filename_album = newPath + "/" + f'album{i+1}.html'
        print('uploading album: ', i+1)
        s3.upload_file(filename_album, bucket_name, f'album{i+1}.html')
    print('albums uploaded')
    print('----------------------------------')
    # создать переменную с кодом страницы index и error
    indexCh1 = '<!doctype html> <html> <head> <meta charset="utf-8"> ' \
               '<title>Фотоархив</title> </head> <body> <h1>Фотоархив</h1> <ul>'

    indexCh3 = '</ul> </body>'
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
    for key in os.listdir(newPath):
        if key == 'index.html' or key == 'error.html':
            print('uploading file ' + key)
            filename = newPath + str(key)
            s3.upload_file(filename, bucket_name, key)
    print('uploaded')
    print('----------------------------------')

    # Define the website configuration
    website_configuration = {
        'ErrorDocument': {'Key': 'error.html'},
        'IndexDocument': {'Suffix': 'index.html'},
    }
    try:
        # Set the website configuration
        s3.put_bucket_website(Bucket=bucket_name,
                              WebsiteConfiguration=website_configuration)
        result = s3.get_bucket_website(Bucket=bucket_name)
        print("Ваша ссылка: ")
        print(f'https://{bucket_name}.website.yandexcloud.net/')
        print('----------------------------------')
    except ClientError as e:
        logging.error(e)
        return False
    return True


def init():
    num = input('Конфиг. файл уже создан? 1 - да, 0 - нет: ')
    if (num == 0):
        print('Доступные бакеты: ')
        bucketList = []
        for bucket in s3.list_buckets()['Buckets']:
            print(bucket['Name'])
            bucketList.append(bucket['Name'])
        print('----------------------------------')
        bucket = input("Введите название bucket: ")
        find_bucket_count = 0
        for item in bucketList:
            if item == bucket:
                find_bucket_count = 1

        if find_bucket_count == 1:
            # Создать новый бакет
            s3.create_bucket(Bucket=f'{bucket}', ACL='public-read-write')

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

        s3 = session.client(
            's3',
            aws_access_key_id=config["default"]["aws_access_key_id"],
            aws_secret_access_key=config["default"]["aws_secret_access_key"],
            region_name=config["default"]["region"],
            endpoint_url=config["default"]["endpoint_url"],
        )
        bucket_name = config["default"]["bucket"]
        print('----------------------------------')
        fire.Fire()
    else:
        print('Конфиг не существует, используйте команду init')