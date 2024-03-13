from . import db
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), unique=True, nullable=False)
    # tareas = db.relationship('RegistroTarea', backref='categoria_asignada', lazy=True)
    tareas = db.relationship('RegistroTarea', back_populates='categoria')
class Estado(db.Model):
    __tablename__ = 'estados'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)

class RegistroTarea(db.Model):
    __tablename__ = 'registro_tareas'
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.Text, nullable=False)
    fecha_inicio = db.Column(db.DateTime, nullable=True)
    fecha_fin = db.Column(db.DateTime, nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    estado_id = db.Column(db.Integer, db.ForeignKey('estados.id'), nullable=False)
  
    usuario = db.relationship('Usuario', backref=db.backref('tareas', lazy=True))
    # categoria = db.relationship('Categoria', backref=db.backref('tareas_registro', lazy=True))
    estado = db.relationship('Estado', backref=db.backref('tareas', lazy=True))
    categoria = db.relationship('Categoria', back_populates='tareas')