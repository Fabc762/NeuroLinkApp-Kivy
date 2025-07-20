# main.py
import asyncio
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.image import Image # Para mostrar las imágenes del zorrito, casa, coche
from kivy.uix.progressbar import ProgressBar # Para las barras de estado del zorrito
from kivy.clock import mainthread, Clock
from kivy.metrics import dp
from kivy.animation import Animation
from functools import partial # Para pasar argumentos a Clock.schedule_once
from random import randint # Para generar números aleatorios en el juego
from datetime import datetime # Para registrar la última interacción
from kivy.properties import ListProperty # Importar ListProperty para los colores de la barra

# Importar el servicio de Firebase
from firebase_service import (
    register_user_with_email_password,
    sign_in_user_with_email_password,
    sign_out_user,
    save_user_data,
    get_user_data
)

# Importar el servicio de IA (nuevo archivo)
from ai_service import GeminiAICaller

# Variable global para almacenar el ID del usuario y el token de autenticación
current_user_id = None
current_id_token = None

# Instancia global del invocador de IA
gemini_ai_caller = GeminiAICaller()

# --- Clase para el ZORRITO (Pet) ---
class FoxPet:
    def __init__(self, name="Zorrito", hunger=50, happiness=50, energy=50, cleanliness=50, level=1, xp=0):
        self.name = name
        self.hunger = hunger # Hambre (0-100, 0 es lleno)
        self.happiness = happiness # Felicidad (0-100, 100 es muy feliz)
        self.energy = energy # Energía (0-100, 100 es lleno de energía)
        self.cleanliness = cleanliness # Limpieza (0-100, 100 es limpio)
        self.level = level
        self.xp = xp
        self.last_interaction_time = datetime.now().isoformat() # Para la persistencia

    def to_dict(self):
        """Convierte los atributos del pet a un diccionario para guardar en Firestore."""
        return {
            "name": self.name,
            "hunger": self.hunger,
            "happiness": self.happiness,
            "energy": self.energy,
            "cleanliness": self.cleanliness,
            "level": self.level,
            "xp": self.xp,
            "last_interaction_time": self.last_interaction_time
        }

    @staticmethod
    def from_dict(data):
        """Crea una instancia de FoxPet desde un diccionario de Firestore."""
        pet = FoxPet(
            name=data.get("name", "Zorrito"),
            hunger=data.get("hunger", 50),
            happiness=data.get("happiness", 50),
            energy=data.get("energy", 50),
            cleanliness=data.get("cleanliness", 50),
            level=data.get("level", 1),
            xp=data.get("xp", 0)
        )
        pet.last_interaction_time = data.get("last_interaction_time", datetime.now().isoformat())
        return pet

    def update_stats(self, dt):
        """Actualiza las estadísticas del zorrito con el tiempo."""
        # El zorrito se vuelve más hambriento, menos feliz, etc.
        self.hunger = min(100, self.hunger + 0.5 * dt) # Aumenta el hambre
        self.happiness = max(0, self.happiness - 0.2 * dt) # Disminuye la felicidad
        self.energy = max(0, self.energy - 0.1 * dt) # Disminuye la energía
        self.cleanliness = max(0, self.cleanliness - 0.3 * dt) # Disminuye la limpieza

        # Asegurar que los valores estén en el rango [0, 100]
        self.hunger = max(0, min(100, self.hunger))
        self.happiness = max(0, min(100, self.happiness))
        self.energy = max(0, min(100, self.energy))
        self.cleanliness = max(0, min(100, self.cleanliness))

        # Ganar XP lentamente por estar vivo (opcional)
        # self.xp += 0.01 * dt
        # self.check_level_up()

    def feed(self):
        """Alimenta al zorrito, reduciendo el hambre y aumentando la felicidad."""
        self.hunger = max(0, self.hunger - 30)
        self.happiness = min(100, self.happiness + 15)
        self.xp += 5
        self.check_level_up()
        self.last_interaction_time = datetime.now().isoformat()

    def play(self):
        """Juega con el zorrito, aumentando la felicidad y reduciendo la energía."""
        self.happiness = min(100, self.happiness + 25)
        self.energy = max(0, self.energy - 20)
        self.xp += 10
        self.check_level_up()
        self.last_interaction_time = datetime.now().isoformat()

    def clean(self):
        """Limpia al zorrito, aumentando la limpieza y un poco la felicidad."""
        self.cleanliness = min(100, self.cleanliness + 40)
        self.happiness = min(100, self.happiness + 5)
        self.xp += 3
        self.check_level_up()
        self.last_interaction_time = datetime.now().isoformat()

    def sleep(self):
        """Hace que el zorrito duerma, restaurando la energía."""
        self.energy = min(100, self.energy + 50)
        self.happiness = min(100, self.happiness + 5) # Un poco más feliz al despertar
        self.xp += 2
        self.check_level_up()
        self.last_interaction_time = datetime.now().isoformat()

    def check_level_up(self):
        """Verifica si el zorrito sube de nivel."""
        xp_needed = self.level * 100 # Ejemplo: 100 XP para Nivel 2, 200 para Nivel 3
        if self.xp >= xp_needed:
            self.level += 1
            self.xp = 0 # Reiniciar XP para el siguiente nivel
            print(f"¡{self.name} ha subido al Nivel {self.level}!")
            return True
        return False

# --- Clase Python para PetProgressBar (NUEVA) ---
class PetProgressBar(ProgressBar):
    # Definir las propiedades de color como ListProperty con valores por defecto
    bar_bg_color = ListProperty([0.9, 0.9, 0.9, 1]) # Color de fondo de la barra
    bar_fg_color = ListProperty([0.2, 0.5, 0.8, 1]) # Color de la barra de progreso

# --- Kivy KV Language for UI ---
Builder.load_string("""
# Definición de un estilo base para TextInput moderno
<AuthTextInput@TextInput>:
    font_size: '18sp'
    padding: [dp(16), dp(16)]
    size_hint_y: None
    height: dp(56)
    background_normal: ''
    background_active: ''
    background_color: 0.95, 0.95, 0.95, 1 # Gris claro
    foreground_color: 0.1, 0.1, 0.1, 1 # Texto oscuro
    cursor_color: 0.2, 0.6, 1, 1 # Azul vibrante para el cursor
    multiline: False
    write_tab: False
    border: [dp(2), dp(2), dp(2), dp(2)]
    canvas.before:
        Color:
            rgba: 0.8, 0.8, 0.8, 1 # Borde gris claro
        Line:
            width: dp(1.5)
            rectangle: self.x, self.y, self.width, self.height
        Color:
            rgba: self.background_color
        Rectangle:
            size: self.size
            pos: self.pos

# Definición de un estilo base para Button moderno
<AuthButton@Button>:
    font_size: '20sp'
    size_hint_y: None
    height: dp(60)
    background_normal: ''
    background_color: 0.2, 0.5, 0.8, 1 # Azul vibrante
    color: 1, 1, 1, 1 # Texto blanco
    canvas.before:
        Color:
            rgba: self.background_color
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [dp(10)] # Bordes redondeados

# Estilo para un botón secundario o de texto
<TextButton@Button>:
    font_size: '16sp'
    color: 0.5, 0.5, 0.5, 1 # Gris
    background_normal: ''
    background_color: 0,0,0,0 # Transparente
    size_hint_y: None
    height: dp(40)

# Estilo para las barras de progreso (AHORA DIBUJA CON RECTÁNGULOS Y COLORES)
<PetProgressBar>:
    max: 100
    height: dp(20)
    size_hint_y: None
    # Los valores por defecto de estas propiedades se definen en la clase Python
    # bar_bg_color: 0.9, 0.9, 0.9, 1 # Se puede sobrescribir aquí si es necesario
    # bar_fg_color: 0.2, 0.5, 0.8, 1 # Se puede sobrescribir aquí si es necesario

    canvas:
        # Dibuja el fondo de la barra
        Color:
            rgba: self.bar_bg_color
        Rectangle:
            pos: self.pos
            size: self.size
        # Dibuja la parte llena de la barra
        Color:
            rgba: self.bar_fg_color if self.value > 0 else (0,0,0,0) # Asegura que no sea transparente si el valor es 0
        Rectangle:
            pos: self.pos
            size: self.value_normalized * self.width, self.height


# Pantalla de Carga/Splash Screen
<SplashScreen>:
    name: 'splash'
    FloatLayout:
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1 # Fondo blanco
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: 'NeuroLinkApp'
            font_size: '48sp'
            color: 0.2, 0.5, 0.8, 1 # Azul del logo
            pos_hint: {'center_x': 0.5, 'center_y': 0.6}
            size_hint: None, None
            size: self.texture_size
        Label:
            text: 'Cargando...'
            font_size: '20sp'
            color: 0.5, 0.5, 0.5, 1 # Gris
            pos_hint: {'center_x': 0.5, 'center_y': 0.3}
            size_hint: None, None
            size: self.texture_size

# Pantalla de Login
<LoginScreen>:
    name: 'login'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(40)
        spacing: dp(20)
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1 # Fondo blanco
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: 'Bienvenido a NeuroLink'
            font_size: '36sp'
            halign: 'center'
            size_hint_y: None
            height: self.texture_size[1] + dp(20) # Espacio extra
            color: 0.1, 0.1, 0.1, 1 # Texto oscuro
        AuthTextInput:
            id: email_input_login
            hint_text: 'Email'
        AuthTextInput:
            id: password_input_login
            hint_text: 'Contraseña'
            password: True
        AuthButton:
            text: 'Iniciar Sesión'
            on_release: root.login()
        TextButton:
            text: '¿Olvidaste tu contraseña?'
            on_release: print('Forgot password clicked')
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(40)
            Label:
                text: '¿Nuevo usuario?'
                font_size: '16sp'
                color: 0.3, 0.3, 0.3, 1
                halign: 'right'
            TextButton:
                text: 'Regístrate aquí'
                color: 0.2, 0.5, 0.8, 1
                halign: 'left'
                on_release: app.root.current = 'register'

# Pantalla de Registro
<RegisterScreen>:
    name: 'register'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(40)
        spacing: dp(20)
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1 # Fondo blanco
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: 'Crea tu cuenta'
            font_size: '36sp'
            halign: 'center'
            size_hint_y: None
            height: self.texture_size[1] + dp(20)
            color: 0.1, 0.1, 0.1, 1
        AuthTextInput:
            id: email_input_register
            hint_text: 'Email'
        AuthTextInput:
            id: password_input_register
            hint_text: 'Contraseña (mín. 6 caracteres)'
            password: True
        AuthButton:
            text: 'Registrarse'
            on_release: root.register()
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(40)
            Label:
                text: '¿Ya tienes una cuenta?'
                font_size: '16sp'
                color: 0.3, 0.3, 0.3, 1
                halign: 'right'
            TextButton:
                text: 'Inicia sesión'
                color: 0.2, 0.5, 0.8, 1
                halign: 'left'
                on_release: app.root.current = 'login'

# Pantalla Principal del Juego (Pet Screen)
<PetScreen>:
    name: 'pet_game'
    FloatLayout:
        canvas.before:
            Color:
                rgba: 0.95, 0.95, 0.95, 1 # Fondo gris claro
            Rectangle:
                pos: self.pos
                size: self.size
        
        # Fondo de la casa
        Image:
            source: 'images/house.png' # Ruta de la imagen local
            size_hint: 1, 0.7
            pos_hint: {'center_x': 0.5, 'y': 0.3}
            allow_stretch: True
            keep_ratio: False

        # Zorrito (Pet)
        Image:
            id: pet_image
            source: 'images/raccoon_pixel.png' # Ruta de la imagen local
            size_hint: 0.4, 0.4
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
            allow_stretch: True
            keep_ratio: True

        # Nombre y Nivel del Zorrito
        Label:
            id: pet_name_label
            text: 'Zorrito Nivel 1'
            font_size: '24sp'
            color: 0.1, 0.1, 0.1, 1
            pos_hint: {'center_x': 0.5, 'top': 0.95}
            size_hint_y: None
            height: self.texture_size[1]

        # Barras de estado
        BoxLayout:
            orientation: 'vertical'
            size_hint: 0.8, None
            height: dp(100)
            pos_hint: {'center_x': 0.5, 'top': 0.85}
            spacing: dp(5)
            Label:
                text: 'Hambre:'
                font_size: '14sp'
                color: 0.3, 0.3, 0.3, 1
                size_hint_y: None
                height: self.texture_size[1]
            PetProgressBar:
                id: hunger_bar
                value: 50
            Label:
                text: 'Felicidad:'
                font_size: '14sp'
                color: 0.3, 0.3, 0.3, 1
                size_hint_y: None
                height: self.texture_size[1]
            PetProgressBar:
                id: happiness_bar
                value: 50
            Label:
                text: 'Energía:'
                font_size: '14sp'
                color: 0.3, 0.3, 0.3, 1
                size_hint_y: None
                height: self.texture_size[1]
            PetProgressBar:
                id: energy_bar
                value: 50
            Label:
                text: 'Limpieza:'
                font_size: '14sp'
                color: 0.3, 0.3, 0.3, 1
                size_hint_y: None
                height: self.texture_size[1]
            PetProgressBar:
                id: cleanliness_bar
                value: 50

        # Botones de interacción
        BoxLayout:
            orientation: 'horizontal'
            size_hint: 0.9, None
            height: dp(70)
            pos_hint: {'center_x': 0.5, 'y': 0.05}
            spacing: dp(10)
            AuthButton:
                text: 'Comer'
                on_release: root.feed_pet()
            AuthButton:
                text: 'Jugar'
                on_release: root.play_pet()
            AuthButton:
                text: 'Limpiar'
                on_release: root.clean_pet()
            AuthButton:
                text: 'Dormir'
                on_release: root.sleep_pet()

        # Botón para ir al chat
        AuthButton:
            text: 'Chatear con Zorrito'
            size_hint: 0.5, None
            height: dp(50)
            pos_hint: {'center_x': 0.5, 'y': 0.15}
            on_release: app.root.current = 'pet_chat'
        
        # Botón de Cerrar Sesión (para volver al login)
        TextButton:
            text: 'Cerrar Sesión'
            pos_hint: {'right': 0.98, 'top': 0.05}
            size_hint: None, None
            width: dp(120)
            height: dp(40)
            on_release: root.logout()


# Pantalla de Chat con el Zorrito
<PetChatScreen>:
    name: 'pet_chat'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: 0.9, 0.98, 1, 1 # Fondo azul claro
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: 'Chatea con tu Zorrito'
            font_size: '30sp'
            color: 0.1, 0.1, 0.1, 1
            size_hint_y: None
            height: self.texture_size[1] + dp(10)

        # Área de chat
        BoxLayout:
            orientation: 'vertical'
            id: chat_history_layout
            size_hint_y: 1
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1 # Fondo blanco para el historial de chat
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [dp(10)]
            ScrollView:
                id: chat_scroll_view
                Label:
                    id: chat_display_label
                    text: '¡Hola! Soy tu Zorrito. ¿Qué quieres contarme?'
                    font_size: '16sp'
                    color: 0.2, 0.2, 0.2, 1
                    text_size: self.width, None
                    halign: 'left'
                    valign: 'top'
                    padding: dp(10), dp(10)
                    size_hint_y: None
                    height: self.texture_size[1] + dp(20) # Ajusta la altura dinámicamente

        # Entrada de usuario y botón de enviar
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(60)
            spacing: dp(10)
            AuthTextInput:
                id: user_chat_input
                hint_text: 'Escribe tu mensaje aquí...'
                multiline: False
                write_tab: False
                size_hint_x: 0.8
                on_text_validate: root.send_chat_message() # Enviar al presionar Enter
            AuthButton:
                text: 'Enviar'
                size_hint_x: 0.2
                on_release: root.send_chat_message()

        AuthButton:
            text: 'Volver al Juego'
            size_hint_y: None
            height: dp(50)
            on_release: app.root.current = 'pet_game'
""")

# --- Clases de Pantalla ---

class SplashScreen(Screen):
    def on_enter(self, *args):
        Clock.schedule_once(self.go_to_login, 2) # 2 segundos de splash

    def go_to_login(self, dt):
        self.manager.current = 'login'

class LoginScreen(Screen):
    def on_enter(self, *args):
        self.ids.email_input_login.focus = True

    def login(self):
        email = self.ids.email_input_login.text
        password = self.ids.password_input_login.text
        # Validaciones básicas de entrada
        if not email or not password:
            self._show_message("Error de Inicio de Sesión", "Por favor, ingresa correo y contraseña.")
            return

        # Mostrar indicador de carga
        self._show_loading_popup("Iniciando sesión...")
        asyncio.create_task(self._perform_login(email, password))

    async def _perform_login(self, email, password):
        global current_user_id, current_id_token
        result = await sign_in_user_with_email_password(email, password)
        self._dismiss_loading_popup() # Cerrar popup de carga
        if result.get("success"):
            current_user_id = result.get("user_id")
            current_id_token = result.get("id_token")
            self._show_message_and_navigate(result, "Inicio de Sesión")
        else:
            self._show_message(f"Error de Inicio de Sesión", result.get("message", "Error desconocido."))

    @mainthread
    def _show_message(self, title, msg):
        popup_content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        popup_content.add_widget(Label(text=msg, halign='center', valign='middle', size_hint_y=None, height=dp(50), color=(0.1, 0.1, 0.1, 1)))
        close_button = Button(text='OK', size_hint=(1, None), height=dp(40))
        popup_content.add_widget(close_button)

        popup = Popup(title=title,
                      content=popup_content,
                      size_hint=(0.8, 0.4),
                      pos_hint={'center_x': 0.5, 'center_y': 0.5})
        close_button.bind(on_release=popup.dismiss)
        popup.open()

    @mainthread
    def _show_message_and_navigate(self, result, operation_name):
        self._show_message(f'{operation_name} Resultado', result.get("message", "Error desconocido"))
        if result.get("success"):
            # Al iniciar sesión, ir directamente a la pantalla del juego
            self.manager.current = 'pet_game'
            # Inicializar o cargar el pet en la pantalla del juego
            self.manager.get_screen('pet_game').load_pet_data()
            self.ids.email_input_login.text = ''
            self.ids.password_input_login.text = ''

    _loading_popup = None
    @mainthread
    def _show_loading_popup(self, message="Cargando..."):
        if self._loading_popup is None:
            popup_content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            popup_content.add_widget(Label(text=message, halign='center', valign='middle', size_hint_y=None, height=dp(50), color=(0.1, 0.1, 0.1, 1)))
            self._loading_popup = Popup(title='Procesando',
                                        content=popup_content,
                                        size_hint=(0.6, 0.3),
                                        pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                        auto_dismiss=False)
        self._loading_popup.open()

    @mainthread
    def _dismiss_loading_popup(self):
        if self._loading_popup:
            self._loading_popup.dismiss()
            self._loading_popup = None


class RegisterScreen(Screen):
    def on_enter(self, *args):
        self.ids.email_input_register.focus = True

    def register(self):
        email = self.ids.email_input_register.text
        password = self.ids.password_input_register.text
        # Validaciones básicas de entrada
        if not email or not password:
            self._show_message("Error de Registro", "Por favor, ingresa correo y contraseña.")
            return
        if len(password) < 6:
            self._show_message("Error de Registro", "La contraseña debe tener al menos 6 caracteres.")
            return

        # Mostrar indicador de carga
        self._show_loading_popup("Registrando usuario...")
        asyncio.create_task(self._perform_register(email, password))

    async def _perform_register(self, email, password):
        global current_user_id, current_id_token
        result = await register_user_with_email_password(email, password)
        self._dismiss_loading_popup() # Cerrar popup de carga
        if result.get("success"):
            current_user_id = result.get("user_id")
            current_id_token = result.get("id_token")
            self._show_message_and_navigate(result, "Registro")
        else:
            self._show_message(f"Error de Registro", result.get("message", "Error desconocido."))

    @mainthread
    def _show_message(self, title, msg):
        popup_content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        popup_content.add_widget(Label(text=msg, halign='center', valign='middle', size_hint_y=None, height=dp(50), color=(0.1, 0.1, 0.1, 1)))
        close_button = Button(text='OK', size_hint=(1, None), height=dp(40))
        popup_content.add_widget(close_button)

        popup = Popup(title=title,
                      content=popup_content,
                      size_hint=(0.8, 0.4),
                      pos_hint={'center_x': 0.5, 'center_y': 0.5})
        close_button.bind(on_release=popup.dismiss)
        popup.open()

    @mainthread
    def _show_message_and_navigate(self, result, operation_name):
        self._show_message(f'{operation_name} Resultado', result.get("message", "Error desconocido"))
        if result.get("success"):
            self.manager.current = 'pet_game'
            self.manager.get_screen('pet_game').load_pet_data()
            self.ids.email_input_register.text = ''
            self.ids.password_input_register.text = ''

    _loading_popup = None
    @mainthread
    def _show_loading_popup(self, message="Cargando..."):
        if self._loading_popup is None:
            popup_content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            popup_content.add_widget(Label(text=message, halign='center', valign='middle', size_hint_y=None, height=dp(50), color=(0.1, 0.1, 0.1, 1)))
            self._loading_popup = Popup(title='Procesando',
                                        content=popup_content,
                                        size_hint=(0.6, 0.3),
                                        pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                        auto_dismiss=False)
        self._loading_popup.open()

    @mainthread
    def _dismiss_loading_popup(self):
        if self._loading_popup:
            self._loading_popup.dismiss()
            self._loading_popup = None


class PetScreen(Screen):
    pet = None # Instancia del zorrito

    def on_enter(self, *args):
        # Cargar los datos del pet cuando se entra a la pantalla
        self.load_pet_data()
        # Iniciar el bucle de actualización del pet si no está ya activo
        if not hasattr(self, '_pet_update_event') or self._pet_update_event is None:
            self._pet_update_event = Clock.schedule_interval(self.update_pet_stats_ui, 1) # Actualizar cada segundo

    def on_leave(self, *args):
        # Detener el bucle de actualización cuando se sale de la pantalla
        if hasattr(self, '_pet_update_event') and self._pet_update_event is not None:
            self._pet_update_event.cancel()
            self._pet_update_event = None
        # Guardar los datos del pet al salir de la pantalla principal del juego
        self.save_pet_data()

    def load_pet_data(self):
        global current_user_id, current_id_token
        if current_user_id and current_id_token:
            self._show_loading_popup("Cargando datos del zorrito...")
            asyncio.create_task(self._perform_load_pet_data(current_user_id, current_id_token))
        else:
            # Si no hay usuario logueado, crear un nuevo zorrito por defecto
            self.pet = FoxPet()
            self.update_pet_stats_ui(0) # Actualizar UI inmediatamente
            print("No hay usuario logueado, creando un nuevo zorrito por defecto.")

    async def _perform_load_pet_data(self, user_id, id_token):
        result = await get_user_data(user_id, id_token)
        self._dismiss_loading_popup()
        if result.get("success") and result.get("data"):
            self.pet = FoxPet.from_dict(result["data"])
            print(f"Datos del zorrito cargados: {self.pet.to_dict()}")
        else:
            self.pet = FoxPet() # Crear nuevo si no se encontraron datos
            print("No se encontraron datos del zorrito, creando uno nuevo.")
            self._show_message("Info", "No se encontraron datos de tu zorrito. ¡Hemos creado uno nuevo para ti!")
        self.update_pet_stats_ui(0) # Actualizar UI con los datos cargados/nuevos

    def save_pet_data(self):
        global current_user_id, current_id_token
        if self.pet and current_user_id and current_id_token:
            self._show_loading_popup("Guardando datos del zorrito...")
            asyncio.create_task(self._perform_save_pet_data(current_user_id, self.pet.to_dict(), current_id_token))

    async def _perform_save_pet_data(self, user_id, data, id_token):
        result = await save_user_data(user_id, data, id_token)
        self._dismiss_loading_popup()
        if result.get("success"):
            print("Datos del zorrito guardados exitosamente.")
            # self._show_message("Guardar Datos", "Datos del zorrito guardados exitosamente.")
        else:
            print(f"Error al guardar datos del zorrito: {result.get('message')}")
            self._show_message("Error al Guardar", result.get("message", "Error desconocido al guardar datos del zorrito."))

    def update_pet_stats_ui(self, dt):
        """Actualiza las estadísticas del zorrito y la UI."""
        if self.pet:
            self.pet.update_stats(dt) # Actualiza los stats internos
            self.ids.pet_name_label.text = f"{self.pet.name} Nivel {self.pet.level}"
            self.ids.hunger_bar.value = 100 - self.pet.hunger # La barra va de 0 a 100, 0 es lleno
            self.ids.happiness_bar.value = self.pet.happiness
            self.ids.energy_bar.value = self.pet.energy
            self.ids.cleanliness_bar.value = self.pet.cleanliness

            # Animación de "respiración" para el zorrito
            anim = Animation(y=self.ids.pet_image.y + dp(5), duration=0.8) + \
                   Animation(y=self.ids.pet_image.y, duration=0.8)
            anim.start(self.ids.pet_image)

            # Guardar automáticamente los datos cada cierto tiempo (ej. cada 30 segundos)
            if int(Clock.get_time()) % 30 == 0: # Guarda cada 30 segundos
                self.save_pet_data()

    def feed_pet(self):
        if self.pet:
            self.pet.feed()
            self.update_pet_stats_ui(0)
            self._show_message("¡Ñam ñam!", f"{self.pet.name} ha comido y está menos hambriento.")
            self.animate_pet_action(self.ids.pet_image, 'feed')

    def play_pet(self):
        if self.pet:
            self.pet.play()
            self.update_pet_stats_ui(0)
            self._show_message("¡Diversión!", f"{self.pet.name} ha jugado y está más feliz.")
            self.animate_pet_action(self.ids.pet_image, 'play')

    def clean_pet(self):
        if self.pet:
            self.pet.clean()
            self.update_pet_stats_ui(0)
            self._show_message("¡Limpiecito!", f"{self.pet.name} está reluciente.")
            self.animate_pet_action(self.ids.pet_image, 'clean')

    def sleep_pet(self):
        if self.pet:
            self.pet.sleep()
            self.update_pet_stats_ui(0)
            self._show_message("¡A dormir!", f"{self.pet.name} ha descansado y tiene más energía.")
            self.animate_pet_action(self.ids.pet_image, 'sleep')

    def animate_pet_action(self, widget, action_type):
        """Animación simple para las acciones del pet."""
        original_x, original_y = widget.pos
        original_scale = widget.scale if hasattr(widget, 'scale') else 1

        if action_type == 'feed':
            anim = Animation(scale=1.1, duration=0.2) + \
                   Animation(scale=original_scale, duration=0.2)
        elif action_type == 'play':
            anim = Animation(y=original_y + dp(20), duration=0.1) + \
                   Animation(y=original_y, duration=0.1)
            anim += Animation(angle=15, duration=0.1) + \
                    Animation(angle=-15, duration=0.1) + \
                    Animation(angle=0, duration=0.1) # Pequeño salto y giro
        elif action_type == 'clean':
            anim = Animation(opacity=0.5, duration=0.2) + \
                   Animation(opacity=1, duration=0.2) # Parpadeo
        elif action_type == 'sleep':
            anim = Animation(opacity=0.7, duration=0.5) + \
                   Animation(opacity=1, duration=0.5) # Atenuar y volver

        anim.start(widget)


    def logout(self):
        self._show_loading_popup("Cerrando sesión...")
        asyncio.create_task(self._perform_logout())

    async def _perform_logout(self, *args): # Añadido *args para compatibilidad con eventos
        global current_user_id, current_id_token
        # Detener el bucle de actualización del pet antes de cerrar sesión
        pet_screen = self.manager.get_screen('pet_game')
        if hasattr(pet_screen, '_pet_update_event') and pet_screen._pet_update_event is not None:
            pet_screen._pet_update_event.cancel()
            pet_screen._pet_update_event = None

        # Guardar los datos del pet por última vez antes de cerrar sesión
        self.save_pet_data() # Llamar al método de la propia pantalla PetScreen
        
        result = await sign_out_user()
        self._dismiss_loading_popup() # Cerrar popup de carga
        if result.get("success"):
            current_user_id = None
            current_id_token = None
            self._show_message_and_navigate(result, "Cerrar Sesión")
        else:
            self._show_message(f"Error al Cerrar Sesión", result.get("message", "Error desconocido."))

    @mainthread
    def _show_message(self, title, msg):
        popup_content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        popup_content.add_widget(Label(text=msg, halign='center', valign='middle', size_hint_y=None, height=dp(50), color=(0.1, 0.1, 0.1, 1)))
        close_button = Button(text='OK', size_hint=(1, None), height=dp(40))
        popup_content.add_widget(close_button)

        popup = Popup(title=title,
                      content=popup_content,
                      size_hint=(0.8, 0.4),
                      pos_hint={'center_x': 0.5, 'center_y': 0.5})
        close_button.bind(on_release=popup.dismiss)
        popup.open()

    @mainthread
    def _show_message_and_navigate(self, result, operation_name):
        self._show_message(f'{operation_name} Resultado', result.get("message", "Error desconocido"))
        if result.get("success"):
            self.manager.current = 'login'
            # Eliminada la línea que intentaba acceder a 'home'
            # self.manager.get_screen('home').ids.user_id_label.text = 'ID de usuario: N/A' 

    _loading_popup = None
    @mainthread
    def _show_loading_popup(self, message="Cargando..."):
        if self._loading_popup is None:
            popup_content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            popup_content.add_widget(Label(text=message, halign='center', valign='middle', size_hint_y=None, height=dp(50), color=(0.1, 0.1, 0.1, 1)))
            self._loading_popup = Popup(title='Procesando',
                                        content=popup_content,
                                        size_hint=(0.6, 0.3),
                                        pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                        auto_dismiss=False)
        self._loading_popup.open()

    @mainthread
    def _dismiss_loading_popup(self):
        if self._loading_popup:
            self._loading_popup.dismiss()
            self._loading_popup = None


class PetChatScreen(Screen):
    chat_history = [] # Almacena el historial de chat para mantener el contexto de la IA

    def on_enter(self, *args):
        # Asegurar que el TextInput de chat tenga foco al entrar a la pantalla
        self.ids.user_chat_input.focus = True
        # Actualizar el historial de chat al entrar
        self.update_chat_display()

    def update_chat_display(self):
        """Actualiza el Label con todo el historial de chat."""
        full_chat_text = ""
        for role, message in self.chat_history:
            if role == "user":
                full_chat_text += f"[b]Tú:[/b] {message}\n"
            else: # role == "model" (pet)
                full_chat_text += f"[b]Zorrito:[/b] {message}\n"
        self.ids.chat_display_label.text = full_chat_text
        # Desplazarse al final del ScrollView
        self.ids.chat_scroll_view.scroll_y = 0

    def send_chat_message(self):
        user_message = self.ids.user_chat_input.text.strip()
        self.ids.user_chat_input.text = '' # Limpiar el campo de entrada

        if not user_message:
            return

        # Añadir mensaje del usuario al historial
        self.chat_history.append(("user", user_message))
        self.update_chat_display()

        self._show_loading_popup("Zorrito está pensando...")
        asyncio.create_task(self._get_pet_response(user_message))

    async def _get_pet_response(self, user_message):
        response_text = "Lo siento, no puedo responder ahora mismo."
        try:
            # Pasar el historial de chat a la IA para mantener el contexto
            response_text = await gemini_ai_caller.chat_with_pet(user_message, self.chat_history)
        except Exception as e:
            response_text = f"Error en la conversación: {e}"
            print(f"Error en _get_pet_response: {e}")
        finally:
            self._dismiss_loading_popup()
            # Añadir respuesta del pet al historial
            self.chat_history.append(("model", response_text))
            self.update_chat_display()

    @mainthread
    def _show_message(self, title, msg):
        popup_content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        popup_content.add_widget(Label(text=msg, halign='center', valign='middle', size_hint_y=None, height=dp(50), color=(0.1, 0.1, 0.1, 1)))
        close_button = Button(text='OK', size_hint=(1, None), height=dp(40))
        popup_content.add_widget(close_button)

        popup = Popup(title=title,
                      content=popup_content,
                      size_hint=(0.8, 0.4),
                      pos_hint={'center_x': 0.5, 'center_y': 0.5})
        close_button.bind(on_release=popup.dismiss)
        popup.open()

    _loading_popup = None
    @mainthread
    def _show_loading_popup(self, message="Cargando..."):
        if self._loading_popup is None:
            popup_content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            popup_content.add_widget(Label(text=message, halign='center', valign='middle', size_hint_y=None, height=dp(50), color=(0.1, 0.1, 0.1, 1)))
            self._loading_popup = Popup(title='Procesando',
                                        content=popup_content,
                                        size_hint=(0.6, 0.3),
                                        pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                        auto_dismiss=False)
        self._loading_popup.open()

    @mainthread
    def _dismiss_loading_popup(self):
        if self._loading_popup:
            self._loading_popup.dismiss()
            self._loading_popup = None


# --- Clase Principal de la Aplicación ---
class NeuroLinkApp(App):
    def build(self):
        self.title = "NeuroLinkApp - Mi Zorrito IA"
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(SplashScreen())
        sm.add_widget(LoginScreen())
        sm.add_widget(RegisterScreen())
        sm.add_widget(PetScreen()) # Pantalla principal del juego
        sm.add_widget(PetChatScreen()) # Pantalla de chat con el zorrito
        return sm

    def on_start(self):
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self._check_initial_auth_state())

    async def _check_initial_auth_state(self):
        print("Verificando estado de autenticación inicial...")
        await asyncio.sleep(0.1) # Pequeña pausa para que la SplashScreen se muestre
        # En una aplicación real, aquí podrías intentar cargar un token de sesión
        # para iniciar sesión automáticamente. Por ahora, siempre va a 'login'.
        pass

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(NeuroLinkApp().async_run())
    loop.close()
