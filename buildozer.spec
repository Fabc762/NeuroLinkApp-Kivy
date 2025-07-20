# buildozer.spec
# This file is used to control the build process of your application.

[app]

# (str) Title of your application
title = NeuroLinkApp - Mi Zorrito IA

# (str) Package name
package.name = com.neurolink.foxpet

# (str) Package domain (needed for android/ios packaging)
package.domain = com.neurolink

# (str) Source code where the main.py live
source.dir = .

# (list) Application requirements
# comma separated e.g. requirements = kivy,python3
# ¡IMPORTANTE! Asegúrate de que todas tus librerías estén aquí.
# 'openssl' es CRUCIAL para que 'requests' funcione correctamente en Android.
requirements = python3,kivy,requests,google-generativeai,openssl

# (str) Kivy version to use
kivy.version = 2.3.0 # Puedes ajustar a la versión más reciente si lo deseas

# (list) List of target machine to build for.
# This is useful when you want to build for multiple architectures.
# android, ios, desktop, win, mac
target.host = android

# (str) The Android API level to build against
android.api = 33

# (str) The Android NDK version to use
# android.ndk = 25b # Deja esto comentado para que Buildozer use su NDK por defecto o lo descargue.

# (int) The Android SDK version to use
# android.sdk = 33 # Deja esto comentado para que Buildozer use su SDK por defecto o lo descargue.

# (int) The Android minimum API level your application require
android.minapi = 21

# (list) Android permissions
# Permisos necesarios para internet, estado de la red y mantener la app activa.
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WAKE_LOCK

# (bool) Enable/disable Android services
# ESTAS LÍNEAS FUERON ELIMINADAS/COMENTADAS YA QUE NO SON SINTAXIS VÁLIDA PARA BUILDER.SPEC
# android.add_services = firebase
# android.extra_services = FirebaseMessaging, FirebaseAuth, FirebaseFirestore

# (list) Logcat filters for Android debugging
# Descomenta esta línea para ver los logs de Python en logcat
android.logcat_filters = *:S python:I

# (bool) Enable/disable release build
android.release = false

# (list) Include extra extensions for your source code
# Esto asegura que tus archivos .py, .kv, .png, .jpg y .json se incluyan en el APK.
source.include_exts = py,kv,png,jpg,json

# (list) Exclude files from the build process
# exclude_exts = spec

# (str) Icon file
# Ruta a tu icono. Asegúrate de que 'images' esté en el mismo directorio que main.py.
icon.filename = %(source.dir)s/images/raccoon_pixel.png

# (str) Splash screen file
# splash.filename = %(source.dir)s/images/splash.png # Descomenta si tienes una imagen de splash

# (str) Orientation of the application
orientation = portrait

# (bool) Debug mode
debug = True

# (list) Android build tools version to use
# android.build_tools = 33.0.0

# (str) Android target SDK version (usually same as android.api)
# android.target_sdk = 33

# (str) Android NDK path (if not set, Buildozer will download it)
# android.ndk_path = /path/to/android-ndk-r25b

# (str) Android SDK path (if not set, Buildozer will try to find it)
# android.sdk_path = /path/to/android-sdk

# (str) Java Home path (if not set, Buildozer will try to find it)
# java.home = /path/to/jdk-11

# (list) Extra arguments to pass to the Android build tool (gradle)
# android.extra_gradle_args = --stacktrace

# (bool) Enable/disable aapt2 (Android Asset Packaging Tool 2)
# android.enable_aapt2 = True

# (list) Extra Java libraries to include in the build
# android.add_libs = path/to/mylib.jar

# (list) Extra native libraries (.so files) to include in the build
# android.add_native_libs = path/to/mylib.so

# (str) Application version string
version = 0.1

# (int) Application version code
version.code = 1
