import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import date

app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN DE LA BASE DE DATOS (SUPABASE / POSTGRESQL) ---
# Render inyectará la variable de entorno DATABASE_URL automáticamente
# Si estás en local, usa tu URL de Supabase
database_url = os.environ.get('DATABASE_URL', 'sqlite:///blog.db')

# Parche importante para que SQLAlchemy funcione con la URL de Supabase (postgres:// -> postgresql://)
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELOS DE LA BASE DE DATOS (Basado en tu diagrama) ---
# (Deja el resto de tus modelos exactamente igual que antes)
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

# --- RUTAS DEL BACKEND ---
@app.route('/')
def index():
    return render_template('index.html')

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
    # Render usa el puerto 10000 por defecto, o el que indique la variable PORT
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) # Debug False en producción