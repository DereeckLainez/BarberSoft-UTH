from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# Configuración de conexión para SQLite (Usará tu archivo barbersoft.db)
def conectar_db():
    # Buscamos el archivo en la carpeta del proyecto
    db_path = os.path.join(os.getcwd(), 'barbersoft.db')
    conn = sqlite3.connect(db_path)
    # Esto permite acceder a las columnas por nombre como hacías con dictionary=True
    conn.row_factory = sqlite3.Row 
    return conn

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        
        db = conectar_db()
        cursor = db.cursor()
        # En SQLite usamos '?' en lugar de '%s'
        cursor.execute("SELECT * FROM clientes WHERE correo = ? AND contraseña = ?", 
                      (correo, contraseña))
        user = cursor.fetchone()
        db.close()
        
        if user: 
            return redirect(url_for('dashboard'))
        else: 
            error = "Acceso denegado. Credenciales incorrectas."
    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard(): 
    return render_template('dashboard.html')

@app.route('/clientes')
def clientes():
    db = conectar_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM clientes")
    clientes_list = cursor.fetchall()
    db.close()
    return render_template('clientes.html', clientes=clientes_list)

@app.route('/nuevo_cliente', methods=['GET', 'POST'])
def nuevo_cliente():
    if request.method == 'POST':
        db = conectar_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO clientes (nombre_completo, telefono, correo, contraseña) VALUES (?, ?, ?, ?)", 
                      (request.form['nombre_completo'], request.form['telefono'], request.form['correo'], request.form['contraseña']))
        db.commit()
        db.close()
        return redirect(url_for('clientes'))
    return render_template('nuevo_cliente.html')

@app.route('/barberos')
def barberos():
    db = conectar_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM barberos")
    barberos_list = cursor.fetchall()
    db.close()
    return render_template('barberos.html', barberos=barberos_list)

@app.route('/nuevo_barbero', methods=['GET', 'POST'])
def nuevo_barbero():
    if request.method == 'POST':
        db = conectar_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO barberos (nombre_barbero, especialidad) VALUES (?, ?)", 
                      (request.form['nombre_barbero'], request.form['especialidad']))
        db.commit()
        db.close()
        return redirect(url_for('barberos'))
    return render_template('nuevo_barbero.html')

@app.route('/servicios')
def servicios():
    db = conectar_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM servicios")
    servicios_list = cursor.fetchall()
    db.close()
    return render_template('servicios.html', servicios=servicios_list)

@app.route('/nuevo_servicio', methods=['GET', 'POST'])
def nuevo_servicio():
    if request.method == 'POST':
        db = conectar_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO servicios (nombre_servicio, precio, tiempo_estimado) VALUES (?, ?, ?)", 
                      (request.form['nombre_servicio'], request.form['precio'], request.form['tiempo_estimado']))
        db.commit()
        db.close()
        return redirect(url_for('servicios'))
    return render_template('nuevo_servicio.html')

@app.route('/citas')
def citas():
    db = conectar_db()
    cursor = db.cursor()
    cursor.execute("""SELECT citas.*, clientes.nombre_completo, barberos.nombre_barbero, servicios.nombre_servicio 
                 FROM citas 
                 JOIN clientes ON citas.id_cliente = clientes.id_cliente 
                 JOIN barberos ON citas.id_barbero = barberos.id_barbero 
                 JOIN servicios ON citas.id_servicio = servicios.id_servicio""")
    citas_list = cursor.fetchall()
    db.close()
    return render_template('citas.html', citas=citas_list)

@app.route('/nueva_cita', methods=['GET', 'POST'])
def nueva_cita():
    db = conectar_db()
    cursor = db.cursor()
    if request.method == 'POST':
        cursor.execute("INSERT INTO citas (id_cliente, id_barbero, id_servicio, fecha_hora) VALUES (?, ?, ?, ?)", 
                      (request.form['id_cliente'], request.form['id_barbero'], request.form['id_servicio'], request.form['fecha_hora']))
        db.commit()
        db.close()
        return redirect(url_for('citas'))
    
    cursor.execute("SELECT id_cliente, nombre_completo FROM clientes")
    clientes_list = cursor.fetchall()
    cursor.execute("SELECT id_barbero, nombre_barbero FROM barberos")
    barberos_list = cursor.fetchall()
    cursor.execute("SELECT id_servicio, nombre_servicio FROM servicios")
    servicios_list = cursor.fetchall()
    db.close()
    return render_template('nueva_cita.html', clientes=clientes_list, barberos=barberos_list, servicios=servicios_list)

@app.route('/facturas')
def facturas():
    db = conectar_db()
    cursor = db.cursor()
    cursor.execute("SELECT facturas.*, clientes.nombre_completo FROM facturas JOIN clientes ON facturas.id_cliente = clientes.id_cliente ORDER BY id_factura DESC")
    facturas_list = cursor.fetchall()
    db.close()
    return render_template('facturas.html', facturas=facturas_list)

@app.route('/nueva_factura', methods=['GET', 'POST'])
def nueva_factura():
    db = conectar_db()
    cursor = db.cursor()
    if request.method == 'POST':
        cursor.execute("SELECT precio FROM servicios WHERE id_servicio = ?", (request.form['id_servicio'],))
        servicio = cursor.fetchone()
        precio = servicio['precio'] if servicio else 0
        cursor.execute("INSERT INTO facturas (id_cliente, total_pagar) VALUES (?, ?)", (request.form['id_cliente'], precio))
        db.commit()
        db.close()
        return redirect(url_for('facturas'))
    
    cursor.execute("SELECT id_cliente, nombre_completo FROM clientes")
    clientes_list = cursor.fetchall()
    cursor.execute("SELECT id_servicio, nombre_servicio, precio FROM servicios")
    servicios_list = cursor.fetchall()
    db.close()
    return render_template('nueva_factura.html', clientes=clientes_list, servicios=servicios_list)

@app.route('/reportes')
def reportes():
    db = conectar_db()
    cursor = db.cursor()
    cursor.execute("SELECT SUM(total_pagar) as total FROM facturas")
    fila_ventas = cursor.fetchone()
    ventas = fila_ventas['total'] if fila_ventas and fila_ventas['total'] else 0
    
    cursor.execute("SELECT COUNT(*) as total FROM citas")
    total_citas = cursor.fetchone()['total']
    
    cursor.execute("SELECT facturas.*, clientes.nombre_completo FROM facturas JOIN clientes ON facturas.id_cliente = clientes.id_cliente ORDER BY id_factura DESC LIMIT 5")
    facturas_recientes = cursor.fetchall()
    db.close()
    return render_template('reportes.html', total_ventas=ventas, total_citas=total_citas, facturas=facturas_recientes)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
