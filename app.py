import os
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import date

app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN DE LA BASE DE DATOS (SUPABASE / POSTGRESQL) ---
database_url = os.environ.get('DATABASE_URL', 'sqlite:///blog.db')

if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELOS DE LA BASE DE DATOS ---
class Usuario(db.Model):
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(150))
    contrasena = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20))
    fecha_registro = db.Column(db.Date, default=date.today)
    publicaciones = db.relationship('Publicacion', backref='autor', lazy=True)

class Categoria(db.Model):
    __tablename__ = 'categoria'
    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255))
    publicaciones = db.relationship('Publicacion', backref='categoria', lazy=True)

class Etiqueta(db.Model):
    __tablename__ = 'etiqueta'
    id_etiqueta = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)

class Publicacion(db.Model):
    __tablename__ = 'publicacion'
    id_publicacion = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    contenido = db.Column(db.Text)
    imagen_url = db.Column(db.String(255))
    fecha_publicacion = db.Column(db.Date, default=date.today)
    estado = db.Column(db.String(20))
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categoria.id_categoria'))
    comentarios = db.relationship('Comentario', backref='publicacion', lazy=True)

publicacion_etiqueta = db.Table('publicacion_etiqueta',
    db.Column('id_publicacion', db.Integer, db.ForeignKey('publicacion.id_publicacion'), primary_key=True),
    db.Column('id_etiqueta', db.Integer, db.ForeignKey('etiqueta.id_etiqueta'), primary_key=True)
)

class Comentario(db.Model):
    __tablename__ = 'comentario'
    id_comentario = db.Column(db.Integer, primary_key=True)
    autor = db.Column(db.String(100))
    contenido = db.Column(db.Text)
    fecha = db.Column(db.Date, default=date.today)
    id_publicacion = db.Column(db.Integer, db.ForeignKey('publicacion.id_publicacion'), nullable=False)

# Crear las tablas en la base de datos (si no existen)
with app.app_context():
    db.create_all()

# --- RUTAS DEL BACKEND ---

# 1. Servir el index.html DESDE LA RAÍZ (ya no usa templates)
@app.route('/')
def index():
    # Esta función lee el archivo index.html que está en la misma carpeta que app.py
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        return "Error: No se encontró el archivo 'index.html' en la raíz del proyecto.", 500

# 2. API: Crear Usuario
@app.route('/api/usuarios', methods=['POST'])
def crear_usuario():
    data = request.json
    nuevo_usuario = Usuario(
        nombre=data['nombre'],
        correo=data.get('correo'),
        contrasena=data['contrasena'],
        rol=data.get('rol')
    )
    db.session.add(nuevo_usuario)
    db.session.commit()
    return jsonify({'mensaje': 'Usuario creado', 'id': nuevo_usuario.id_usuario})

# 3. API: Crear Publicación
@app.route('/api/publicaciones', methods=['POST'])
def crear_publicacion():
    data = request.json
    nueva_pub = Publicacion(
        titulo=data['titulo'],
        contenido=data.get('contenido'),
        id_usuario=data['id_usuario'],
        id_categoria=data.get('id_categoria')
    )
    db.session.add(nueva_pub)
    db.session.commit()
    return jsonify({'mensaje': 'Publicación creada', 'id': nueva_pub.id_publicacion})

# 4. API: Listar Publicaciones
@app.route('/api/publicaciones', methods=['GET'])
def listar_publicaciones():
    publicaciones = Publicacion.query.order_by(Publicacion.fecha_publicacion.desc()).all()
    resultado = []
    for pub in publicaciones:
        resultado.append({
            'id_publicacion': pub.id_publicacion,
            'titulo': pub.titulo,
            'contenido': pub.contenido,
            'fecha_publicacion': pub.fecha_publicacion.strftime('%d/%m/%Y'),
            'autor': pub.autor.nombre if pub.autor else 'Anónimo'
        })
    return jsonify(resultado)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
