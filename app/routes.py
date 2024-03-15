from flask import jsonify, render_template, request, redirect, url_for, flash, Flask
from datetime import datetime, timedelta
from . import app, db
from .modelos import Usuario, Categoria, Estado, RegistroTarea
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from . import login_manager

from flask import render_template, request, redirect, url_for, flash
from flask_login import UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash



#ruta y funcion de filtrado de tareas
@app.route('/home')
def index():
    try:
        filtro = request.args.get('filtro', 'todas')
        categorias = Categoria.query.all()
        
        if filtro == 'pendientes':
            tareas = RegistroTarea.query.filter_by(estado_id=Estado.query.filter_by(nombre='Pendiente').first().id).all()
        elif filtro == 'en_progreso':
            tareas = RegistroTarea.query.filter_by(estado_id=Estado.query.filter_by(nombre='En Progreso').first().id).all()
        elif filtro == 'completadas':
            tareas = RegistroTarea.query.filter_by(estado_id=Estado.query.filter_by(nombre='Completada').first().id).all()
        else:
            tareas = RegistroTarea.query.all()
        
        return render_template('index.html', categorias=categorias, tareas=tareas, filtro_actual=filtro)
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error al acceder a la base de datos.', 'danger')
        return render_template('error.html'), 500
    except Exception as e:
        flash('Ocurrió un error inesperado.', 'danger')
        return render_template('error.html'), 500
    

#agregar una nueva tarea 
@app.route('/tarea/nueva', methods=['GET', 'POST'])
def nueva_tarea():
    try:
        if request.method == 'POST':
            descripcion = request.form['descripcion']
            fecha_inicio = request.form['fecha_inicio']
            fecha_fin = request.form.get('fecha_fin', None)
            categoria_id = int(request.form['categoria_id'])
            estado_id = int(request.form['estado_id'])
            usuario_id = 1  # Asumiendo un ID de usuario fijo; reemplazar con el ID del usuario autenticado

            nueva_tarea = RegistroTarea(
                descripcion=descripcion,
                fecha_inicio=datetime.strptime(fecha_inicio, '%Y-%m-%dT%H:%M'),
                fecha_fin=datetime.strptime(fecha_fin, '%Y-%m-%dT%H:%M') if fecha_fin else None,
                categoria_id=categoria_id,
                estado_id=estado_id,
                usuario_id=usuario_id
            )

            db.session.add(nueva_tarea)
            db.session.commit()
            flash('Tarea creada con éxito.', 'success')
            return redirect(url_for('index'))

        categorias = Categoria.query.all()
        estados = Estado.query.all()
        return render_template('agregar_tarea.html', categorias=categorias, estados=estados)
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error al acceder a la base de datos.', 'danger')
        return render_template('error.html'), 500
    except Exception as e:
        flash('Ocurrió un error inesperado.', 'danger')
        return render_template('error.html'), 500

# Editar una tarea existente
@app.route('/tarea/editar/<int:tarea_id>', methods=['GET', 'POST'])
def editar_tarea(tarea_id):
    try:
        tarea = RegistroTarea.query.get_or_404(tarea_id)

        if request.method == 'POST':
            tarea.descripcion = request.form['descripcion']
            tarea.fecha_inicio = datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%dT%H:%M')
            tarea.fecha_fin = datetime.strptime(request.form['fecha_fin'], '%Y-%m-%dT%H:%M') if request.form['fecha_fin'] else None
            tarea.categoria_id = int(request.form['categoria_id'])
            tarea.estado_id = int(request.form['estado_id'])

            db.session.commit()
            flash('Tarea actualizada con éxito.', 'success')
            return redirect(url_for('index'))

        categorias = Categoria.query.all()
        estados = Estado.query.all()
        return render_template('modificar_tarea.html', tarea=tarea, categorias=categorias, estados=estados)
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error al acceder a la base de datos.', 'danger')
        return render_template('error.html'), 500
    except Exception as e:
        flash('Ocurrió un error inesperado.', 'danger')
        return render_template('error.html'), 500

#eliminar una tarea con estado pendiente
@app.route('/eliminar/<int:tarea_id>')
def eliminar_tarea(tarea_id):
    try:
        tarea = RegistroTarea.query.get_or_404(tarea_id)
        
        # no permitir eliminar si la tarea está completada
        if tarea.estado.nombre == "Completada" or tarea.estado.nombre == "En Progreso":
            flash('Las tareas completadas o en progreso no pueden ser eliminadas.', 'warning')
            return redirect(url_for('index'))
        
        db.session.delete(tarea)
        db.session.commit()
        flash('Tarea eliminada con éxito.', 'success')
        return redirect(url_for('index'))
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error al acceder a la base de datos.', 'danger')
        return render_template('error.html'), 500
    except Exception as e:
        flash('Ocurrió un error inesperado.', 'danger')
        return render_template('error.html'), 500



#crear una nueva categoria
@app.route('/categoria/nueva', methods=['GET', 'POST'])
def nueva_categoria():
    try:
        if request.method == 'POST':
            nombre = request.form['nombre']
            nueva_categoria = Categoria(nombre=nombre)
            db.session.add(nueva_categoria)
            db.session.commit()
            return redirect(url_for('categorias'))
        return render_template('nueva_categoria.html')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error al acceder a la base de datos.', 'danger')
        return render_template('error.html'), 500
    except Exception as e:
        flash('Ocurrió un error inesperado.', 'danger')
        return render_template('error.html'), 500

#mostrar todas las categorias
@app.route('/categorias')
def categorias():
    try:
        todas_categorias = Categoria.query.all()
        return render_template('categorias.html', categorias=todas_categorias)
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error al acceder a la base de datos.', 'danger')
        return render_template('error.html'), 500
    except Exception as e:
        flash('Ocurrió un error inesperado.', 'danger')
        return render_template('error.html'), 500
    

#editar una categoria existente
@app.route('/categoria/editar/<int:id>', methods=['GET', 'POST'])
def editar_categoria(id):
    try:
        categoria = Categoria.query.get_or_404(id)
        if request.method == 'POST':
            categoria.nombre = request.form['nombre']
            db.session.commit()
            return redirect(url_for('categorias'))
        return render_template('editar_categoria.html', categoria=categoria)
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error al acceder a la base de datos.', 'danger')
        return render_template('error.html'), 500
    except Exception as e:
        flash('Ocurrió un error inesperado.', 'danger')
        return render_template('error.html'), 500
    

#eliminar una categoria existente
@app.route('/categoria/eliminar/<int:id>')
def eliminar_categoria(id):
    try:
        categoria = Categoria.query.get_or_404(id)
        db.session.delete(categoria)
        db.session.commit()
        return redirect(url_for('categorias'))
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error al acceder a la base de datos.', 'danger')
        return render_template('error.html'), 500
    except Exception as e:
        flash('Ocurrió un error inesperado.', 'danger')
        return render_template('error.html'), 500

#cambiar el estado de una tarea
@app.route('/tarea/cambiar_estado/<int:tarea_id>/<nuevo_estado>')
def cambiar_estado_tarea(tarea_id, nuevo_estado):
    try:
        tarea = RegistroTarea.query.get_or_404(tarea_id)
        estado = Estado.query.filter_by(nombre=nuevo_estado).first()
        if estado:
            tarea.estado_id = estado.id
            db.session.commit()
            flash(f'Estado de la tarea actualizado a {nuevo_estado}', 'success')
        else:
            flash('Estado no válido', 'danger')
        return redirect(url_for('index'))
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error al acceder a la base de datos.', 'danger')
        return render_template('error.html'), 500
    except Exception as e:
        flash('Ocurrió un error inesperado.', 'danger')
        return render_template('error.html'), 500

#registro de usuario
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            nuevo_usuario = Usuario(username=username, password=password, is_active=True)

            db.session.add(nuevo_usuario)
            db.session.commit()

            flash('Usuario registrado con éxito', 'success')
            return redirect(url_for('login'))

        return render_template('registro.html')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error al acceder a la base de datos.', 'danger')
        return render_template('error.html'), 500
    except Exception as e:
        flash('Ocurrió un error inesperado.', 'danger')
        return render_template('error.html'), 500

#login
@app.route('/', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            usuario = Usuario.query.filter_by(username=username).first()

            if usuario and usuario.password == password and usuario.is_active:
                flash('Inicio de sesión exitoso', 'success')
                return redirect(url_for('index'))
            else:
                flash('Nombre de usuario o contraseña incorrectos', 'danger')

        return render_template('login.html')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error al acceder a la base de datos.', 'danger')
        return render_template('error.html'), 500
    except Exception as e:
        flash('Ocurrió un error inesperado.', 'danger')
        return render_template('error.html'), 500

#logout
@app.route('/logout')
def logout():
    try:
        flash('Has cerrado sesión', 'success')
        return redirect(url_for('login'))
    except Exception as e:
        flash('Ocurrió un error inesperado.', 'danger')
        return render_template('error.html'), 500


#ordenar tareas por fecha, descripcion
@app.route('/tareas', methods=['GET'])
def obtener_tareas():
    ordenar_por_fecha = request.args.get('ordenar_por_fecha', 'false').lower() == 'true'
    ordenar_por_descripcion = request.args.get('ordenar_por_descripcion', 'false').lower() == 'true'
    consulta = RegistroTarea.query

    if ordenar_por_fecha:
        consulta = consulta.order_by(RegistroTarea.fecha_creacion)

    if ordenar_por_descripcion:
        consulta = consulta.order_by(RegistroTarea.descripcion)

    tareas = consulta.all()
    return render_template('tareas.html', tareas=tareas)

#reporte
@app.route('/reporte')
def reporte():
    try:
        total_tareas = RegistroTarea.query.count()
        completadas = RegistroTarea.query.filter_by(estado_id=Estado.query.filter_by(nombre='Completada').first().id).count()
        pendientes = RegistroTarea.query.filter_by(estado_id=Estado.query.filter_by(nombre='Pendiente').first().id).count()
        en_progreso = RegistroTarea.query.filter_by(estado_id=Estado.query.filter_by(nombre='En Progreso').first().id).count()

        porcentaje_completadas = (completadas / total_tareas) * 100 if total_tareas else 0
        porcentaje_pendientes = (pendientes / total_tareas) * 100 if total_tareas else 0
        porcentaje_en_progreso = (en_progreso / total_tareas) * 100 if total_tareas else 0

        tiempo_promedio = db.session.query(func.avg(RegistroTarea.fecha_fin - RegistroTarea.fecha_inicio)).scalar()
        tiempo_maximo = db.session.query(func.max(RegistroTarea.fecha_fin - RegistroTarea.fecha_inicio)).scalar()
        tiempo_minimo = db.session.query(func.min(RegistroTarea.fecha_fin - RegistroTarea.fecha_inicio)).scalar()

        categoria_con_mas_tareas = Categoria.query.join(RegistroTarea).group_by(Categoria.id).order_by(func.count().desc()).first()

        return render_template('reporte.html',
                               porcentaje_completadas=porcentaje_completadas,
                               porcentaje_pendientes=porcentaje_pendientes,
                               porcentaje_en_progreso=porcentaje_en_progreso,
                               tiempo_promedio=tiempo_promedio,
                               tiempo_maximo=tiempo_maximo,
                               tiempo_minimo=tiempo_minimo,
                               categoria_con_mas_tareas=categoria_con_mas_tareas)
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error al acceder a la base de datos.', 'danger')
        return render_template('error.html'), 500
    except Exception as e:
        flash('Ocurrió un error inesperado.', 'danger')
        return render_template('error.html'), 500

