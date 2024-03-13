from flask import render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
from . import app, db
from .modelos import Usuario, Categoria, Estado, RegistroTarea


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
            fecha_inicio=datetime.strptime(fecha_inicio, '%Y-%m-%d'),
            fecha_fin=datetime.strptime(fecha_fin, '%Y-%m-%d') if fecha_fin else None,
            categoria_id=categoria_id,
            estado_id=estado_id,
            usuario_id=usuario_id
        )

        db.session.add(nueva_tarea)
        db.session.commit()
        flash('Tarea creada con éxito', 'success')
        return redirect(url_for('index'))

    categorias = Categoria.query.all()
    estados = Estado.query.all()
    return render_template('agregar_tarea.html', categorias=categorias, estados=estados)

@app.route('/tarea/editar/<int:tarea_id>', methods=['GET', 'POST'])
def editar_tarea(tarea_id):
    tarea = RegistroTarea.query.get_or_404(tarea_id)

    if request.method == 'POST':
        tarea.descripcion = request.form['descripcion']
        tarea.fecha_inicio = datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d')
        tarea.fecha_fin = datetime.strptime(request.form['fecha_fin'], '%Y-%m-%d') if request.form['fecha_fin'] else None
        tarea.categoria_id = int(request.form['categoria_id'])
        tarea.estado_id = int(request.form['estado_id'])

        db.session.commit()
        flash('Tarea actualizada con éxito', 'success')
        return redirect(url_for('index'))

    categorias = Categoria.query.all()
    estados = Estado.query.all()
    return render_template('modificar_tarea.html', tarea=tarea, categorias=categorias, estados=estados)

@app.route('/eliminar/<int:tarea_id>')
def eliminar_tarea(tarea_id):
    tarea = RegistroTarea.query.get_or_404(tarea_id)
    
    # no permitir eliminar si la tarea está completada
    if tarea.estado.nombre == "Completada" or tarea.estado.nombre == "En Progreso":
        flash('Las tareas completadas o en progreso no pueden ser eliminadas.', 'warning')
        return redirect(url_for('index'))
    
    db.session.delete(tarea)
    db.session.commit()
    flash('Tarea eliminada con éxito.', 'success')
    return redirect(url_for('index'))


@app.route('/categoria/nueva', methods=['GET', 'POST'])
def nueva_categoria():
    if request.method == 'POST':
        nombre = request.form['nombre']
        nueva_categoria = Categoria(nombre=nombre)
        db.session.add(nueva_categoria)
        db.session.commit()
        return redirect(url_for('categorias'))
    return render_template('nueva_categoria.html')

@app.route('/categorias')
def categorias():
    todas_categorias = Categoria.query.all()
    return render_template('categorias.html', categorias=todas_categorias)


@app.route('/categoria/editar/<int:id>', methods=['GET', 'POST'])
def editar_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    if request.method == 'POST':
        categoria.nombre = request.form['nombre']
        db.session.commit()
        return redirect(url_for('categorias'))
    return render_template('editar_categoria.html', categoria=categoria)


@app.route('/categoria/eliminar/<int:id>')
def eliminar_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    db.session.delete(categoria)
    db.session.commit()
    return redirect(url_for('categorias'))


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
