from flask import render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
from . import app, db
from .modelos import Usuario, Categoria, Estado, RegistroTarea
from sqlalchemy import func 

#ruta y funcion de filtrado de tareas
@app.route('/')
def index():
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


#agregar una nueva tarea 
@app.route('/tarea/nueva', methods=['GET', 'POST'])
def nueva_tarea():
    if request.method == 'POST':
        descripcion = request.form['descripcion']
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form.get('fecha_fin', None)
        categoria_id = int(request.form['categoria_id'])
        estado_id = int(request.form['estado_id'])
        usuario_id = 1 

        nueva_tarea = RegistroTarea(
            descripcion=descripcion,
            fecha_inicio=datetime.strptime(fecha_inicio,  '%Y-%m-%dT%H:%M'),
            fecha_fin=datetime.strptime(fecha_fin,  '%Y-%m-%dT%H:%M') if fecha_fin else None,
            categoria_id=categoria_id,
            estado_id=estado_id,
            usuario_id=usuario_id
        )

        db.session.add(nueva_tarea)
        db.session.commit()
        return redirect(url_for('index'))

    categorias = Categoria.query.all()
    estados = Estado.query.all()
    return render_template('agregar_tarea.html', categorias=categorias, estados=estados)


#editar una tarea existente
@app.route('/tarea/editar/<int:tarea_id>', methods=['GET', 'POST'])
def editar_tarea(tarea_id):
    tarea = RegistroTarea.query.get_or_404(tarea_id)

    if request.method == 'POST':
        tarea.descripcion = request.form['descripcion']
        tarea.fecha_inicio = datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%dT%H:%M')
        tarea.fecha_fin = datetime.strptime(request.form['fecha_fin'],'%Y-%m-%dT%H:%M') if request.form['fecha_fin'] else None
        tarea.categoria_id = int(request.form['categoria_id'])
        tarea.estado_id = int(request.form['estado_id'])

        db.session.commit()
        flash('Tarea actualizada con éxito', 'success')
        return redirect(url_for('index'))

    categorias = Categoria.query.all()
    estados = Estado.query.all()
    return render_template('modificar_tarea.html', tarea=tarea, categorias=categorias, estados=estados)



#eliminar una tarea con estado pendiente
@app.route('/eliminar/<int:tarea_id>')
def eliminar_tarea(tarea_id):
    tarea = RegistroTarea.query.get_or_404(tarea_id)
    
    # no permitir eliminar si la tarea está completada
    if tarea.estado.nombre == "Completada" or tarea.estado.nombre == "En Progreso":
        flash('Las tareas completadas no pueden ser eliminadas.', 'warning')
        return redirect(url_for('index'))
    
    db.session.delete(tarea)
    db.session.commit()
    flash('Tarea eliminada con éxito.', 'success')
    return redirect(url_for('index'))


#crear una nueva categoria
@app.route('/categoria/nueva', methods=['GET', 'POST'])
def nueva_categoria():
    if request.method == 'POST':
        nombre = request.form['nombre']
        nueva_categoria = Categoria(nombre=nombre)
        db.session.add(nueva_categoria)
        db.session.commit()
        return redirect(url_for('categorias'))
    return render_template('nueva_categoria.html')


#mostrar todas las categorias
@app.route('/categorias')
def categorias():
    todas_categorias = Categoria.query.all()
    return render_template('categorias.html', categorias=todas_categorias)


#editar una categoria existente
@app.route('/categoria/editar/<int:id>', methods=['GET', 'POST'])
def editar_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    if request.method == 'POST':
        categoria.nombre = request.form['nombre']
        db.session.commit()
        return redirect(url_for('categorias'))
    return render_template('editar_categoria.html', categoria=categoria)

#eliminar una categoria existente
@app.route('/categoria/eliminar/<int:id>')
def eliminar_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    db.session.delete(categoria)
    db.session.commit()
    return redirect(url_for('categorias'))


#cambiar el estado de una tarea
@app.route('/tarea/cambiar_estado/<int:tarea_id>/<nuevo_estado>')
def cambiar_estado_tarea(tarea_id, nuevo_estado):
    tarea = RegistroTarea.query.get_or_404(tarea_id)
    estado = Estado.query.filter_by(nombre=nuevo_estado).first()
    if estado:
        tarea.estado_id = estado.id
        db.session.commit()
        flash(f'Estado de la tarea actualizado a {nuevo_estado}', 'success')
    else:
        flash('Estado no válido', 'danger')
    return redirect(url_for('index'))

# 
@app.route('/reporte')
def reporte():
    # Calcula porcentajes de tareas por estado
    total_tareas = RegistroTarea.query.count()
    completadas = RegistroTarea.query.filter_by(estado_id=Estado.query.filter_by(nombre='Completada').first().id).count()
    pendientes = RegistroTarea.query.filter_by(estado_id=Estado.query.filter_by(nombre='Pendiente').first().id).count()
    en_progreso = RegistroTarea.query.filter_by(estado_id=Estado.query.filter_by(nombre='En Progreso').first().id).count()

    porcentaje_completadas = (completadas / total_tareas) * 100 if total_tareas else 0
    porcentaje_pendientes = (pendientes / total_tareas) * 100 if total_tareas else 0
    porcentaje_en_progreso = (en_progreso / total_tareas) * 100 if total_tareas else 0

    # Tiempo promedio, maximo y minimo en completar una tarea
    tiempo_promedio = db.session.query(func.avg(RegistroTarea.fecha_fin - RegistroTarea.fecha_inicio)).scalar()
    tiempo_maximo = db.session.query(func.max(RegistroTarea.fecha_fin - RegistroTarea.fecha_inicio)).scalar()
    tiempo_minimo = db.session.query(func.min(RegistroTarea.fecha_fin - RegistroTarea.fecha_inicio)).scalar()

    # Categoria con mas tareas
    categoria_con_mas_tareas = Categoria.query.join(RegistroTarea).group_by(Categoria.id).order_by(func.count().desc()).first()

    return render_template('reporte.html',
                           porcentaje_completadas=porcentaje_completadas,
                           porcentaje_pendientes=porcentaje_pendientes,
                           porcentaje_en_progreso=porcentaje_en_progreso,
                           tiempo_promedio=tiempo_promedio,
                           tiempo_maximo=tiempo_maximo,
                           tiempo_minimo=tiempo_minimo,
                           categoria_con_mas_tareas=categoria_con_mas_tareas)
