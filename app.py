import os
from flask import Flask, request, jsonify
from supabase import create_client, Client

app = Flask(__name__)

# CONEXIÓN A SUPABASE
SUPABASE_URL = "https://xjdbvtfaekeblhtqcpvs.supabase.co"
SUPABASE_KEY = "sb_publishable__vEjN-Zb_NQcup-N11IMTQ_g41Jgdi0"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Servir el HTML
@app.route('/')
def index():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Error: No se encontró el archivo index.html"

# Crear Usuario
@app.route('/api/usuarios', methods=['POST'])
def crear_usuario():
    try:
        data = request.json
        response = supabase.table('usuario').insert({
            'nombre': data['nombre'],
            'correo': data['correo'],
            'contrasena': data['contrasena'],
            'rol': data.get('rol', 'admin')
        }).execute()
        return jsonify({'id': response.data[0]['id_usuario']})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Crear Publicación
@app.route('/api/publicaciones', methods=['POST'])
def crear_publicacion():
    try:
        data = request.json
        response = supabase.table('publicacion').insert({
            'titulo': data['titulo'],
            'contenido': data['contenido'],
            'id_usuario': data['id_usuario'],
            'id_categoria': data.get('id_categoria', 1)
        }).execute()
        return jsonify({'id': response.data[0]['id_publicacion']})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Listar Publicaciones
@app.route('/api/publicaciones', methods=['GET'])
def listar_publicaciones():
    try:
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
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
