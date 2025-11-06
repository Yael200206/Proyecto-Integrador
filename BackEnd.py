from flask import Flask, jsonify, request, render_template
from BD import BD
import google.generativeai as genai
import os
import traceback
from dotenv import load_dotenv

# ==============================
# CONFIGURACIÓN DEL SERVIDOR
# ==============================
app = Flask(__name__)
DB_FILE = "datos.json"
bd = BD(DB_FILE)

# ==============================
# CARGAR VARIABLES DE ENTORNO
# ==============================
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ No se encontró GEMINI_API_KEY en el entorno o archivo .env")

genai.configure(api_key=GEMINI_API_KEY)

# ==============================
# CONFIGURACIÓN DE GEMINI
# ==============================
MODEL_NAME = "models/gemini-2.5-flash"

# ==============================
# CARGAR PROMPT INICIAL
# ==============================
PROMPT_FILE = "prompt.txt"
if not os.path.exists(PROMPT_FILE):
    print(f"⚠️ No se encontró {PROMPT_FILE}, crea el archivo con tu prompt base.")
    PROMPT_BASE = ""
else:
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        PROMPT_BASE = f.read().strip()
    print("✅ Prompt base cargado desde prompt.txt")

# ==============================
# RUTAS DEL FRONTEND
# ==============================
@app.route("/")
def inicio():
    return render_template("index.html")

# ==============================
# RUTAS DE LA API
# ==============================
@app.route("/api/info")
def info():
    return jsonify({
        "mensaje": "API del Chatbot Educativo PUCIO con integración Gemini de Google",
        "estado": "✅ Servidor en ejecución",
        "modelo": MODEL_NAME,
        "endpoints_disponibles": [
            "/api/usuarios (GET, POST)",
            "/api/usuarios/<id> (PUT, DELETE)",
            "/api/chat (POST)"
        ]
    })

@app.route("/api/usuarios", methods=["GET"])
def obtener_usuarios():
    try:
        data = bd.load_data()
        return jsonify(data), 200
    except Exception as e:
        print("❌ Error al obtener usuarios:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/usuarios", methods=["POST"])
def crear_usuario():
    try:
        nuevo = request.get_json()
        if not nuevo or "nombre" not in nuevo or "edad" not in nuevo or "ciudad" not in nuevo:
            return jsonify({"error": "Faltan campos: nombre, edad o ciudad"}), 400

        data = bd.load_data()
        nuevo["id"] = len(data) + 1
        data.append(nuevo)
        bd.save_data(data)
        return jsonify({"mensaje": "✅ Usuario agregado correctamente", "usuario": nuevo}), 201
    except Exception as e:
        print("❌ Error al crear usuario:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/usuarios/<int:id>", methods=["PUT"])
def actualizar_usuario(id):
    try:
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
    except Exception as e:
        print("❌ Error al actualizar usuario:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/usuarios/<int:id>", methods=["DELETE"])
def eliminar_usuario(id):
    try:
        data = bd.load_data()
        new_data = [u for u in data if u["id"] != id]
        if len(new_data) == len(data):
            return jsonify({"error": "Usuario no encontrado"}), 404
        bd.save_data(new_data)
        return jsonify({"mensaje": "🗑️ Usuario eliminado correctamente"}), 200
    except Exception as e:
        print("❌ Error al eliminar usuario:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ------------------------------
# CHAT CON GEMINI
# ------------------------------
def generar_respuesta_gemini(mensaje):
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        prompt_completo = f"{PROMPT_BASE}\nUsuario: {mensaje}\nAsistente:"
        respuesta = model.generate_content(prompt_completo)
        return respuesta.text.strip()
    except Exception as e:
        print(f"❌ Error al comunicarse con Gemini: {str(e)}")
        traceback.print_exc()
        return "⚠️ Error al conectarse con Gemini. Revisa tu API Key o el modelo."

def detectar_materia(mensaje):
    """ Usa Gemini para identificar la materia o tema del mensaje """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        prompt = f"Analiza el siguiente mensaje y responde con una sola palabra que indique la materia principal (por ejemplo: matemáticas, física, biología, historia, programación, literatura, etc).\nMensaje: {mensaje}\nMateria:"
        respuesta = model.generate_content(prompt)
        return respuesta.text.strip().lower()
    except Exception as e:
        print("⚠️ No se pudo detectar materia:", e)
        return "desconocida"

@app.route("/api/chat", methods=["POST"])
def chat_pucio():
    data = request.get_json()
    mensaje = data.get("mensaje", "")
    if not mensaje:
        return jsonify({"error": "No se recibió ningún mensaje"}), 400

    texto_respuesta = generar_respuesta_gemini(mensaje)
    materia = detectar_materia(mensaje)

    print(f"👤 Usuario: {mensaje}\n📘 Materia: {materia}\n🤖 PUCIO: {texto_respuesta}\n")

    # Guardar en datos.json
    try:
        data_json = bd.load_data()
        nuevo = {
            "id": len(data_json) + 1,
            "mensaje": mensaje,
            "respuesta": texto_respuesta,
            "materia": materia
        }
        data_json.append(nuevo)
        bd.save_data(data_json)
    except Exception as e:
        print("⚠️ Error al guardar la conversación:", e)

    return jsonify({
        "usuario": mensaje,
        "materia_detectada": materia,
        "respuesta_pucio": texto_respuesta
    }), 200

# ==============================
# INICIO DEL SERVIDOR
# ==============================
if __name__ == "__main__":
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as file:
            file.write("[]")
    print("🚀 Servidor Flask ejecutándose en http://localhost:5000")
    app.run(debug=True, port=5000)
