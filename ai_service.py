# ai_service.py
import google.generativeai as genai
import asyncio
import os # Aunque no lo usaremos para cargar la API Key aquí, es buena práctica

# ==============================================================================
# CONFIGURACIÓN DE LA API DE GEMINI (¡TU CLAVE API YA INSERTADA!)
# ==============================================================================
# ADVERTENCIA: En una aplicación de producción real, NUNCA debes incrustar tu API Key
# directamente en el código del cliente. Deberías usar un backend seguro (como
# Firebase Cloud Functions) para hacer las llamadas a la API de Gemini.
# Para este proyecto de demostración, lo hacemos directamente para simplificar.
GEMINI_API_KEY = "AIzaSyANIY0bAZ4xDu0CeTk8OKpItkpvCvSjXGI" # TU CLAVE API REAL

genai.configure(api_key=GEMINI_API_KEY)

class GeminiAICaller:
    def __init__(self, model_name="gemini-2.0-flash"):
        self.model = genai.GenerativeModel(model_name)
        # Inicializar el historial de chat para la conversación del pet
        self.chat_session = self.model.start_chat(history=[])

    async def chat_with_pet(self, user_message, current_chat_history):
        """
        Permite al usuario chatear con el zorrito (IA).
        Mantiene el contexto de la conversación.
        current_chat_history: Lista de tuplas (role, message) para el contexto.
        """
        try:
            # Reconstruir el historial para la sesión si es necesario (ej. al cargar el juego)
            # Para simplificar aquí, solo usamos el historial de la sesión actual.
            # Si quieres persistencia del chat, tendrías que pasar el historial completo
            # a la inicialización de start_chat cada vez que se carga la pantalla.
            # Por ahora, la sesión de chat se reinicia con la instancia de GeminiAICaller.

            # Enviar el mensaje del usuario a la IA
            response = await asyncio.to_thread(self.chat_session.send_message, user_message)
            return response.text
        except Exception as e:
            print(f"Error al chatear con Gemini: {e}")
            return "Lo siento, mi cerebro pixelado está un poco ocupado ahora mismo. ¿Podrías repetirlo?"

    async def generate_pixel_pet_mission(self, user_prompt):
        """Genera una misión para el Pixel Pet basada en un prompt del usuario."""
        try:
            prompt = (
                f"Crea una pequeña misión interactiva para un 'Pixel Pet' (un zorrito virtual) "
                f"basada en la siguiente idea del usuario: '{user_prompt}'. "
                f"La misión debe ser algo que el usuario pueda hacer con su teléfono (ej. tomar una foto, grabar un sonido, "
                f"encontrar algo en el mundo real). Sé creativo y conciso. "
                f"Ejemplo: 'Encuentra algo brillante y toma una foto.' o 'Graba el sonido de un pájaro cantando.'"
            )
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            return response.text
        except Exception as e:
            print(f"Error al generar misión de Pixel Pet: {e}")
            return "¡Vamos a explorar algo nuevo! No se pudo generar una misión ahora."

    async def generate_puzzle_hint(self, puzzle_state, previous_attempts):
        """Genera una pista inteligente para un rompecabezas."""
        try:
            prompt = (
                f"Un jugador está resolviendo un rompecabezas de lógica. "
                f"El estado actual del rompecabezas es: {puzzle_state}. "
                f"Intentos previos fallidos: {previous_attempts}. "
                f"Ofrece una pista sutil que guíe al jugador sin dar la solución directa. "
                f"Enfócate en la lógica o el patrón necesario. Sé breve."
            )
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            return response.text
        except Exception as e:
            print(f"Error al generar pista de rompecabezas: {e}")
            return "Sigue intentándolo, ¡casi lo tienes! Piensa fuera de la caja."

    async def generate_post_content(self, user_prompt):
        """Genera contenido para un post de influencer en la Ecosfera Digital."""
        try:
            prompt = (
                f"Eres un experto en redes sociales. Genera un post corto y atractivo "
                f"para un influencer digital sobre el siguiente tema: '{user_prompt}'. "
                f"Incluye hashtags relevantes y un tono moderno. Máximo 100 palabras."
            )
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            return response.text
        except Exception as e:
            print(f"Error al generar contenido con Gemini: {e}")
            return "No se pudo generar el contenido del post."
