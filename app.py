import os
from flask import Flask, render_template_string, request, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# --- CONEXIÓN A SUPABASE ---
# Render leerá estas variables desde "Environment Variables"
SUPABASE_URL = os.environ.get("https://xjdbvtfaekeblhtqcpvs.supabase.co")
SUPABASE_KEY = os.environ.get("sb_publishable__vEjN-Zb_NQcup-N11IMTQ_g41Jgdi0")   

# Crear el cliente de Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- RUTAS ---

# 1. Servir el index.html desde la raíz
@app.route('/')
def index():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        return "Error: No se encontró el archivo 'index.html' en la raíz.", 500

# 2. API: Crear Usuario (Usando Supabase)
@app.route('/api/usuarios', methods=['POST'])
def crear_usuario():
    data = request.json
    # Insertar en la tabla 'usuario' de Supabase
    response = supabase.table('usuario').insert({
        'nombre': data['nombre'],
        'correo': data.get('correo'),
        'contrasena': data['contrasena'],
        'rol': data.get('rol')
    }).execute()
    
    # Devolver el ID del nuevo usuario
    if response.data:
        return jsonify({'mensaje': 'Usuario creado', 'id': response.data[0]['id_usuario']})
    else:
        return jsonify({'error': 'No se pudo crear el usuario'}), 400

# 3. API: Crear Publicación (Usando Supabase)
@app.route('/api/publicaciones', methods=['POST'])
def crear_publicacion():
    data = request.json
    response = supabase.table('publicacion').insert({
        'titulo': data['titulo'],
        'contenido': data.get('contenido'),
        'id_usuario': data['id_usuario'],
        'id_categoria': data.get('id_categoria')
    }).execute()
    
    if response.data:
        return jsonify({'mensaje': 'Publicación creada', 'id': response.data[0]['id_publicacion']})
    else:
        return jsonify({'error': 'No se pudo crear la publicación'}), 400

# 4. API: Listar Publicaciones (Con JOIN para traer el nombre del autor)
@app.route('/api/publicaciones', methods=['GET'])
def listar_publicaciones():
    # Hacemos un JOIN entre 'publicacion' y 'usuario' para traer el nombre del autor
    response = supabase.table('publicacion').select(
        'id_publicacion, titulo, contenido, fecha_publicacion, usuario(nombre)'
    ).order('fecha_publicacion', desc=True).execute()
    
    # Formatear la respuesta para que el frontend la entienda igual que antes
    resultado = []
    for pub in response.data:
        resultado.append({
            'id_publicacion': pub['id_publicacion'],
            'titulo': pub['titulo'],
            'contenido': pub['contenido'],
            'fecha_publicacion': pub['fecha_publicacion'],
            'autor': pub['usuario']['nombre'] if pub['usuario'] else 'Anónimo'
        })
    
    return jsonify(resultado)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
