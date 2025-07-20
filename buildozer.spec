# buildozer.spec
# Este archivo controla el proceso de compilación de tu aplicación.

[app]

# (str) Título de tu aplicación
title = NeuroLinkApp - Mi Zorrito IA

# (str) Nombre del paquete (identificador único de la aplicación)
package.name = neurolinkappfoxpet

# (str) Dominio del paquete (necesario para Android/iOS)
package.domain = com.neurolink

# (str) Directorio del código fuente donde reside main.py
source.dir = .

# (list) Requisitos de la aplicación (librerías Python)
# Separados por comas, ej. requirements = kivy,python3
# ¡IMPORTANTE! Asegúrate de que todas tus librerías estén aquí.
requirements = python3,kivy,requests,google-generativeai,openssl

# (str) Versión de Kivy a usar (ajusta si usas otra)
kivy.version = 2.3.0

# (list) Plataformas objetivo para compilar.
# Para Android, especifica 'android'
target.host = android

# (str) Nivel de API de Android contra el que se compilará (ej. 33 para Android 13)
android.api = 33

# (int) Nivel mínimo de API de Android que tu aplicación requiere (ej. 21 para Android 5.0 Lollipop)
android.minapi = 21

# (list) Permisos de Android que tu aplicación necesita
# ¡IMPORTANTE! Añadidos permisos comunes para apps con red.
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WAKE_LOCK

# (bool) Habilitar/deshabilitar la compilación de lanzamiento (release build)
# Para APK debug, esto es FALSE.
android.release = false

# (bool) Habilitar/deshabilitar la generación de Android App Bundle (AAB)
# Para APK debug, esto es FALSE.
android.enable_aab = false

# (str) Archivo Keystore para firmar el APK/AAB (solo para release)
# android.release_keystore = my-release-key.keystore

# (str) Alias del Keystore para firmar el APK/AAB (solo para release)
# android.release_keystore_alias = alias_name

# (bool) Modo depuración (DEBE SER TRUE PARA APK DEBUG)
debug = True

# (list) Extensiones de archivos a incluir en el código fuente
source.include_exts = py,kv,png,jpg,json

# (str) Archivo de icono de la aplicación
icon.filename = %(source.dir)s/images/raccoon_pixel.png

# (str) Orientación de la aplicación (portrait o landscape)
orientation = portrait

# (str) Versión de la aplicación (visible para el usuario)
version = 0.1

# (int) Código de versión de la aplicación (debe ser un entero, incrementa con cada nueva versión)
version.code = 1
