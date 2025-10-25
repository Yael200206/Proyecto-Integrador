from flask import Flask, jsonify, request
from BD import BD
import google.generativeai as genai
import os

# ==============================
# CONFIGURACIÓN DEL SERVIDOR
# ==============================
app = Flask(__name__)
DB_FILE = "datos.json"
bd = BD(DB_FILE)

# ==============================
# CONFIGURACIÓN DE GEMINI
# ==============================
# Asegúrate de tener tu API key configurada
# Puedes obtenerla desde: https://makersuite.google.com/app/apikey
genai.configure(api_key="TU_API_KEY_DE_GEMINI")

# Seleccionamos el modelo de lenguaje de Google Gemini
model = genai.GenerativeModel("gemini-1.5-flash")

# ==============================
# RUTAS DE LA API
# ==============================

@app.route("/")
def inicio():
    return jsonify({
        "mensaje": "API del Chatbot Educativo PUCIO con integración de Gemini",
        "estado": "✅ Servidor en ejecución",
        "endpoints_disponibles": [
            "/api/usuarios (GET, POST)",
            "/api/usuarios/<id> (PUT, DELETE)",
            "/api/chat (POST)"
        ]
    })

# ------------------------------
# CRUD de Usuarios (JSON)
# ------------------------------

@app.route("/api/usuarios", methods=["GET"])
def obtener_usuarios():
    data = bd.load_data()
    return jsonify(data), 200


@app.route("/api/usuarios", methods=["POST"])
def crear_usuario():
    nuevo = request.get_json()
    if not nuevo or "nombre" not in nuevo or "edad" not in nuevo or "ciudad" not in nuevo:
        return jsonify({"error": "Faltan campos: nombre, edad o ciudad"}), 400

    data = bd.load_data()
    nuevo["id"] = len(data) + 1
    data.append(nuevo)
    bd.save_data(data)

    return jsonify({"mensaje": "✅ Usuario agregado correctamente", "usuario": nuevo}), 201


@app.route("/api/usuarios/<int:id>", methods=["PUT"])
def actualizar_usuario(id):
    data = bd.load_data()
    usuario = next((u for u in data if u["id"] == id), None)

    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    nuevos = request.get_json()
    usuario["nombre"] = nuevos.get("nombre", usuario["nombre"])
    usuario["edad"] = nuevos.get("edad", usuario["edad"])
    usuario["ciudad"] = nuevos.get("ciudad", usuario["ciudad"])
    bd.save_data(data)

    return jsonify({"mensaje": "✅ Usuario actualizado correctamente", "usuario": usuario}), 200


@app.route("/api/usuarios/<int:id>", methods=["DELETE"])
def eliminar_usuario(id):
    data = bd.load_data()
    new_data = [u for u in data if u["id"] != id]

    if len(new_data) == len(data):
        return jsonify({"error": "Usuario no encontrado"}), 404

    bd.save_data(new_data)
    return jsonify({"mensaje": "🗑️ Usuario eliminado correctamente"}), 200

# ------------------------------
# CHAT CON GEMINI
# ------------------------------

@app.route("/api/chat", methods=["POST"])
def chat_pucio():
    """
    Endpoint para interactuar con la IA de Gemini.
    Recibe un mensaje del usuario y devuelve una respuesta generada por la IA.
    """
    data = request.get_json()
    mensaje = data.get("mensaje", "")

    if not mensaje:
        return jsonify({"error": "No se recibió ningún mensaje"}), 400

    try:
        respuesta = model.generate_content(mensaje)
        texto_respuesta = respuesta.text
        return jsonify({
            "usuario": mensaje,
            "respuesta_pucio": texto_respuesta
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al comunicarse con Gemini: {str(e)}"}), 500

# ==============================
# INICIO DEL SERVIDOR
# ==============================
if __name__ == "__main__":
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as file:
            file.write("[]")
    app.run(debug=True, port=5000)
