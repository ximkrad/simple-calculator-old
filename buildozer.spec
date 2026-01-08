[app]

# App information
title = My Calendar
package.name = mycalendar
package.domain = com.example

# Source code
source.dir = .
source.main = main.py

# Version
version = 1.0

# Requirements (упростите!)
requirements = python3,kivy==2.3.0

# Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Android settings
android.minapi = 21
android.targetapi = 33
android.sdk = 33
android.ndk = 25b

# Architecture (БЕЗ КОММЕНТАРИЕВ В СТРОКЕ!)
android.arch = arm64-v8a

# Orientation
orientation = portrait
fullscreen = 0
window.size = 400, 700

# Build settings
android.accept_sdk_license = True
android.allow_backup = True

# Log level
log_level = 2
