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
# ¡DEBE SER TRUE PARA AAB/APK DE PRODUCCIÓN!
android.release = true

# (bool) Habilitar/deshabilitar la generación de Android App Bundle (AAB)
# ¡DEBE SER TRUE PARA GENERAR UN AAB!
android.enable_aab = true

# (str) Archivo Keystore para firmar el APK/AAB
# ¡CAMBIA ESTO AL NOMBRE DE TU ARCHIVO .keystore!
# Si no tienes uno, consulta la guía anterior sobre cómo generar un keystore.
android.release_keystore = my-release-key.keystore

# (str) Alias del Keystore para firmar el APK/AAB
# ¡CAMBIA ESTO AL ALIAS QUE ELEGISTE AL CREAR EL KEYSTORE!
android.release_keystore_alias = alias_name

# (str) Contraseña del Keystore (se solicitará si no se establece aquí)
# android.release_keystore_passphrase = tu_contraseña_keystore

# (str) Contraseña del alias de la clave (se solicitará si no se establece aquí)
# android.release_keyalias_passphrase = tu_contraseña_alias

# (bool) Modo depuración (debe ser False para compilaciones de lanzamiento)
debug = False

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
