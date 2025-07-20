# firebase_service.py
import asyncio
import requests
import json

# ==============================================================================
# ESTE ES EL CÓDIGO PARA LA INTEGRACIÓN REAL CON FIREBASE.
# ==============================================================================

# ==============================================================================
# PASO 1: CONFIGURACIÓN DE FIREBASE (¡TUS CREDENCIALES YA INSERTADAS!)
# ==============================================================================
FIREBASE_API_KEY = "AIzaSyB08LrlfeH3DX8NA3KQr1QgG7EqcWTXoA" # TU CLAVE API REAL
FIREBASE_AUTH_URL = "https://identitytoolkit.googleapis.com/v1/accounts:"
FIREBASE_FIRESTORE_URL = f"https://firestore.googleapis.com/v1/projects/neurolinkapp/databases/(default)/documents" # TU ID DE PROYECTO REAL

# ==============================================================================
# PASO 2: FUNCIONES PARA AUTENTICACIÓN (Email/Password)
# ==============================================================================

async def _firebase_auth_request(endpoint, payload):
    """Función auxiliar para hacer solicitudes a la API de Firebase Authentication."""
    url = f"{FIREBASE_AUTH_URL}{endpoint}?key={FIREBASE_API_KEY}"
    headers = {"Content-Type": "application/json"}
    try:
        # requests.post es una función síncrona, asyncio.to_thread la ejecuta en un hilo
        # separado para no bloquear el bucle de eventos de Kivy/asyncio.
        response = await asyncio.to_thread(
            requests.post, url, headers=headers, data=json.dumps(payload)
        )
        response.raise_for_status() # Lanza un error para códigos de estado HTTP 4xx/5xx
        return {"success": True, "data": response.json()}
    except requests.exceptions.HTTPError as http_err:
        error_data = http_err.response.json()
        error_message = error_data.get("error", {}).get("message", "Error desconocido de Firebase Auth.")
        print(f"Error HTTP ocurrido en Firebase Auth: {error_message}")
        return {"success": False, "message": error_message}
    except Exception as err:
        print(f"Otro error ocurrido en Firebase Auth: {err}")
        return {"success": False, "message": f"Error de red o desconocido: {err}"}

async def register_user_with_email_password(email, password):
    """Registra un nuevo usuario con correo y contraseña en Firebase Authentication."""
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True # Para obtener un token de sesión inmediatamente
    }
    result = await _firebase_auth_request("signUp", payload)
    if result["success"]:
        user_id = result["data"]["localId"]
        id_token = result["data"]["idToken"]
        return {"success": True, "user_id": user_id, "id_token": id_token, "message": "¡Registro exitoso! Bienvenido."}
    return result

async def sign_in_user_with_email_password(email, password):
    """Inicia sesión con correo y contraseña en Firebase Authentication."""
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    result = await _firebase_auth_request("signInWithPassword", payload)
    if result["success"]:
        user_id = result["data"]["localId"]
        id_token = result["data"]["idToken"]
        return {"success": True, "user_id": user_id, "id_token": id_token, "message": "¡Inicio de sesión exitoso!"}
    return result

async def sign_out_user():
    """Cierra la sesión del usuario (conceptual)."""
    print("Cerrando sesión (limpiando token localmente en una app real).")
    await asyncio.sleep(0.5) # Simular una operación rápida
    return {"success": True, "message": "Sesión cerrada correctamente."}

# ==============================================================================
# PASO 3: FUNCIONES PARA FIRESTORE (Base de Datos en la Nube)
# ==============================================================================

async def _firestore_request(method, path, data=None, id_token=None):
    """Función auxiliar para hacer solicitudes a la API de Firestore."""
    url = f"{FIREBASE_FIRESTORE_URL}/{path}"
    headers = {"Content-Type": "application/json"}
    if id_token:
        headers["Authorization"] = f"Bearer {id_token}"

    try:
        if method == "POST": # Para crear un documento con ID automático (equivalente a addDoc)
            response = await asyncio.to_thread(
                requests.post, url, headers=headers, data=json.dumps({"fields": data})
            )
        elif method == "PATCH": # Para actualizar un documento (equivalente a setDoc/updateDoc)
            response = await asyncio.to_thread(
                requests.patch, url, headers=headers, data=json.dumps({"fields": data})
            )
        elif method == "GET": # Para obtener un documento (equivalente a getDoc)
            response = await asyncio.to_thread(
                requests.get, url, headers=headers
            )
        else:
            raise ValueError(f"Método HTTP no soportado: {method}")

        response.raise_for_status()
        return {"success": True, "data": response.json()}
    except requests.exceptions.HTTPError as http_err:
        error_data = http_err.response.json()
        error_message = error_data.get("error", {}).get("message", "Error desconocido de Firestore.")
        print(f"Error HTTP ocurrido en Firestore: {error_message}")
        return {"success": False, "message": error_message}
    except Exception as err:
        print(f"Otro error ocurrido en Firestore: {err}")
        return {"success": False, "message": f"Error de red o desconocido: {err}"}

# Helper para convertir de Python dict a Firestore JSON format
def _to_firestore_format(data):
    firestore_fields = {}
    for key, value in data.items():
        if isinstance(value, str):
            firestore_fields[key] = {"stringValue": value}
        elif isinstance(value, int):
            firestore_fields[key] = {"integerValue": value}
        elif isinstance(value, bool):
            firestore_fields[key] = {"booleanValue": value}
        elif isinstance(value, float):
            firestore_fields[key] = {"doubleValue": value}
        elif isinstance(value, list):
            array_elements = []
            for item in value:
                if isinstance(item, str):
                    array_elements.append({"stringValue": item})
                elif isinstance(item, int):
                    array_elements.append({"integerValue": item})
                elif isinstance(item, float):
                    array_elements.append({"doubleValue": item})
                elif isinstance(item, bool):
                    array_elements.append({"booleanValue": item})
                elif isinstance(item, dict):
                    array_elements.append({"mapValue": {"fields": _to_firestore_format(item)}})
            firestore_fields[key] = {"arrayValue": {"values": array_elements}}
        elif isinstance(value, dict):
            firestore_fields[key] = {"mapValue": {"fields": _to_firestore_format(value)}}
        else:
            print(f"Advertencia: Tipo de dato no soportado para Firestore: {type(value)}")
    return firestore_fields

# Helper para convertir de Firestore JSON format a Python dict
def _from_firestore_format(data):
    python_data = {}
    if not data:
        return python_data
    for key, value_obj in data.items():
        if "stringValue" in value_obj:
            python_data[key] = value_obj["stringValue"]
        elif "integerValue" in value_obj:
            python_data[key] = int(value_obj["integerValue"])
        elif "booleanValue" in value_obj:
            python_data[key] = value_obj["booleanValue"]
        elif "doubleValue" in value_obj:
            python_data[key] = float(value_obj["doubleValue"])
        elif "arrayValue" in value_obj and "values" in value_obj["arrayValue"]:
            array_list = []
            for item_obj in value_obj["arrayValue"]["values"]:
                # Recursivamente convertir elementos del array
                if "stringValue" in item_obj:
                    array_list.append(item_obj["stringValue"])
                elif "integerValue" in item_obj:
                    array_list.append(int(item_obj["integerValue"]))
                elif "doubleValue" in item_obj:
                    array_list.append(float(item_obj["doubleValue"]))
                elif "booleanValue" in item_obj:
                    array_list.append(item_obj["booleanValue"])
                elif "mapValue" in item_obj:
                    array_list.append(_from_firestore_format(item_obj["mapValue"].get("fields", {})))
            python_data[key] = array_list
        elif "mapValue" in value_obj and "fields" in value_obj["mapValue"]:
            python_data[key] = _from_firestore_format(value_obj["mapValue"]["fields"])
    return python_data


async def save_user_data(user_id, data_to_save, id_token):
    """Guarda datos de usuario en Firestore."""
    firestore_fields = _to_firestore_format(data_to_save)
    path = f"users/{user_id}/pet_data" # Ruta específica para los datos del pet
    result = await _firestore_request("PATCH", path, firestore_fields, id_token) # PATCH para set/update
    return result

async def get_user_data(user_id, id_token):
    """Recupera datos de usuario de Firestore."""
    path = f"users/{user_id}/pet_data" # Ruta específica para los datos del pet
    result = await _firestore_request("GET", path, id_token=id_token)
    if result["success"] and "fields" in result["data"]:
        python_data = _from_firestore_format(result["data"]["fields"])
        return {"success": True, "data": python_data}
    return {"success": False, "message": "Datos no encontrados o error al recuperar."}
