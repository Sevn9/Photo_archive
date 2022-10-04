# Photo_archive

## Запуск
# на linux
1) установите python3
2) установите pip
3) Установите зависимости: pip3 install -r requirements.txt
4) Запустите программу: python3 cloudphoto.py команда --параметр

# на windows
4) Запустите программу: python cloudphoto.py команда --параметр

# использование
1) Отправка фотографий в облачное хранилище: python cloudphoto.py upload --album ALBUM [--path PHOTOS_DIR]
2) Загрузка фотографий из облачного хранилища: python cloudphoto.py download --album ALBUM [--path PHOTOS_DIR]
3) Просмотр списка альбомов и фотографий в альбоме: python cloudphoto.py list [--album ALBUM]
4) Удаление альбомов и фотографий: python cloudphoto.py delete --album ALBUM [--photo PHOTO]
5) Генерация и публикация веб-страниц фотоархива: python cloudphoto.py mksite
6) Инициализация программы: python cloudphoto.py init