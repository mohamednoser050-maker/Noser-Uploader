[app]

# (str) Title of your application
title = Noser Image Uploader

# (str) Package name
package.name = noseruploader

# (str) Package domain (needed for android/ios packaging)
package.domain = org.noser.hacks

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
requirements = python3, kivy==2.3.0, kivymd==1.1.1, python-telegram-bot, httpx, android, pyjnius, certifi

# (list) Permissions
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, FOREGROUND_SERVICE, POST_NOTIFICATIONS, REQUEST_IGNORE_BATTERY_OPTIMIZATIONS

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK will support.
android.minapi = 21

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# تقليل عدد المعالجات لمعالج واحد (64-bit) لتسريع البناء بنسبة 50% وضمان عدم الفشل
android.archs = arm64-v8a

# (list) services to declare
services = NoserService:service.py

[buildozer]

# (int) log level (0 = error only, 1 = info, 2 = debug (with command output))
# تقليل مستوى السجلات لتقليل حجم المخرجات ومنع GitHub من إغلاق العملية
log_level = 1

# (int) display warning if buildozer is run as root (0 = off, 1 = on)
warn_on_root = 1
