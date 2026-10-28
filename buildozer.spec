[app]
# Название приложения
title = Phone Flipper

# Имя пакета (без пробелов)
package.name = phoneflipper

# Домен (можно оставить так)
package.domain = org.test

# Где лежат исходники (в корне)
source.dir = .

# Какие файлы включать
source.include_exts = py,png,jpg,kv,atlas

# Версия
version = 1.0

# Требования (обязательно python3 и kivy)
requirements = python3,kivy

# Ориентация экрана
orientation = portrait

# Не на весь экран (чтобы были кнопки управления)
fullscreen = 0

# --- САМОЕ ВАЖНОЕ: Собираем только под 64-бит ---
android.archs = arm64-v8a

# Автоматически принимаем лицензии
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
