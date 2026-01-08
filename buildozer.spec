[app]

# Название приложения
title = Мой Календарь

# Имя пакета (уникальное!)
package.name = mycalendar

# Домен пакета
package.domain = com.example

# Путь к исходникам
source.dir = .

# Основной файл
source.main = main.py

# Версия приложения
version = 1.0.0

# Требования
requirements = python3,kivy,pillow,kivyMD

# Разрешения для Android
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Версия Android
android.minapi = 21
android.targetapi = 34
android.sdk = 34
android.ndk = 25b

# Архитектура (упростим для первой сборки)
android.arch = armeabi-v7a

# Ориентация
orientation = portrait

# Полноэкранный режим
fullscreen = 0

# Иконка (создайте или скачайте)
# icon.filename = icon.png

# Заставка при запуске
# presplash.filename = presplash.png

# Включить опцию для новых версий SDK
android.enable_androidx = True

# Разрешить бэкапы
android.allow_backup = True

# API ключи (опционально)
# android.api_key = xxx
# android.store_file = /path/to/.keystore
# android.keyalias = mykeyalias

# Дополнительные настройки
log_level = 2
android.accept_sdk_license = True

# Размер окна (для эмулятора)
window.size = 400, 700

# Автоматически скрывать панель навигации
android.hide_navigation_bar = False

# Разрешить поворот экрана
android.allow_rotation = True

# Включить отладку
android.debug = True

# Включить мультидексы (для больших приложений)
android.multidex = False

# Создавать отчеты об ошибках
android.create_error_report = True

# Дополнительные аргументы для сборки
# android.extra_cmake_args = -DANDROID_STL=c++_shared

[buildozer]

# Логи
log_level = 2

# Папка для сборки
build_dir = .buildozer

# Папка для бинарников
bin_dir = ./bin


