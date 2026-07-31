import os
from flask import Flask, render_template_string, request, jsonify
from supabase import create_client, Client

app = Flask(__name__)

# --- CONEXIÓN DIRECTA A SUPABASE (Sin variables de entorno) ---
# ESTO ES TEMPORAL. Una vez que funcione, las moveremos a variables.
SUPABASE_URL = "https://xjdbvtfaekeblhtqcpvs.supabase.co"
SUPABASE_KEY = "sb_publishable__vEjN-Zb_NQcup-N11IMTQ_g41Jgdi0"

# Crear el cliente de Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- RUTAS ---

@app.route('/')
def index():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        return "Error: No se encontró el archivo 'index.html' en la raíz.", 500

@app.route('/api/usuarios', methods=['POST'])
def crear_usuario():
    data = request.json
    response = supabase.table('usuario').insert({
        'nombre': data['nombre'],
        'correo': data.get('correo'),
        'contrasena': data['contrasena'],
        'rol': data.get('rol')
    }).execute()
    
    if response.data:
        return jsonify({'mensaje': 'Usuario creado', 'id': response.data[0]['id_usuario']})
    else:
        return jsonify({'error': 'No se pudo crear el usuario'}), 400

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

@app.route('/api/publicaciones', methods=['GET'])
def listar_publicaciones():
    response = supabase.table('publicacion').select(
        'id_publicacion, titulo, contenido, fecha_publicacion, usuario(nombre)'
    ).order('fecha_publicacion', desc=True).execute()
    
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
