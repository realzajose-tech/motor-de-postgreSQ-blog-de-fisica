
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from database import Database
    print("✅ Database importado correctamente")
except ImportError as e:
    print(f"❌ Error importando Database: {e}")
    Database = None

app = Flask(__name__)
CORS(app)

# ============================================
# SERVIR ARCHIVOS ESTÁTICOS
# ============================================

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_archivos(filename):
    return send_from_directory('.', filename)

# ============================================
# FUNCIÓN AYUDANTE
# ============================================

def get_db():
    if not Database:
        return None
    try:
        return Database()
    except Exception as e:
        print(f"❌ Error al crear Database: {e}")
        return None

# ============================================
# API - CREAR USUARIO
# ============================================

@app.route('/api/usuarios', methods=['POST'])
def crear_usuario():
    data = request.get_json()
    nombre = data.get('nombre', '').strip()
    correo = data.get('correo', '').strip().lower()
    contrasena = data.get('contrasena', '')
    rol = data.get('rol', 'admin')

    if not nombre or not correo or not contrasena:
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400

    db = get_db()
    if not db:
        return jsonify({'error': 'Error de conexión a la base de datos'}), 500

    try:
        # Verificar si el correo ya existe
        response = db.table('usuario').select('id_usuario').eq('correo', correo).execute()
        if response.data:
            return jsonify({'error': 'El correo ya está registrado'}), 400

        # Insertar el nuevo usuario (SIN .execute() al final)
        response = db.table('usuario').insert({
            'nombre': nombre,
            'correo': correo,
            'contrasena': contrasena,
            'rol': rol
        })

        if response.data:
            return jsonify({'mensaje': 'Usuario creado', 'id': response.data[0]['id_usuario']})
        else:
            return jsonify({'error': 'No se pudo crear el usuario'}), 500
    except Exception as e:
        print(f"❌ ERROR REGISTRO: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================
# API - CREAR PUBLICACIÓN
# ============================================

@app.route('/api/publicaciones', methods=['POST'])
def crear_publicacion():
    data = request.get_json()
    titulo = data.get('titulo', '').strip()
    contenido = data.get('contenido', '').strip()
    id_usuario = data.get('id_usuario')
    id_categoria = data.get('id_categoria', 1)

    if not titulo or not contenido or not id_usuario:
        return jsonify({'error': 'Título, contenido e ID de usuario obligatorios'}), 400

    db = get_db()
    if not db:
        return jsonify({'error': 'Error de conexión a la base de datos'}), 500

    try:
        # Insertar la publicación (SIN .execute() al final)
        response = db.table('publicacion').insert({
            'titulo': titulo,
            'contenido': contenido,
            'id_usuario': id_usuario,
            'id_categoria': id_categoria
        })

        if response.data:
            return jsonify({'mensaje': 'Publicación creada', 'id': response.data[0]['id_publicacion']})
        else:
            return jsonify({'error': 'No se pudo crear la publicación'}), 500
    except Exception as e:
        print(f"❌ ERROR PUBLICACIÓN: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================
# API - LISTAR PUBLICACIONES
# ============================================

@app.route('/api/publicaciones', methods=['GET'])
def listar_publicaciones():
    db = get_db()
    if not db:
        return jsonify({'error': 'Error de conexión a la base de datos'}), 500

    try:
        print("🔍 Consultando publicaciones...")
        response = db.table('publicacion').select(
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
        
        print(f"✅ {len(resultado)} publicaciones encontradas")
        return jsonify(resultado)
    except Exception as e:
        print(f"❌ ERROR LISTAR: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================
# INICIAR SERVIDOR
# ============================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
