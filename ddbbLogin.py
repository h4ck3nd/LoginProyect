import psycopg2
from datetime import datetime
import psycopg2.errors

def conectar_db():
    try:
        conn = psycopg2.connect(
            dbname="login",
            user="postgres",
            password="1234",
            host="localhost",
            port="5432",
            client_encoding="UTF8"  # Asegura que la conexión use UTF-8
        )
        return conn
    except psycopg2.OperationalError as e:
        print("Error de conexión a PostgreSQL:", e)
        return None

def verificar_usuario(usuario, password):
    conn = conectar_db()
    cur = conn.cursor()
    try:
        # Comprobar si el valor ingresado es un email o un nombre de usuario
        query = "SELECT * FROM users WHERE (email = %s OR username = %s) AND password = %s"
        cur.execute(query, (usuario, usuario, password))
        user = cur.fetchone()
        if user:
            # Actualizamos el último login
            cur.execute("UPDATE users SET ultimo_login = %s WHERE email = %s", (datetime.now(), user[3]))  # Usamos el email para actualizar el último login
            conn.commit()
        return user
    finally:
        cur.close()
        conn.close()

def registrar_usuario(nombre_usuario, apellidos_usuario, email, password, fecha_nacimiento, rol):
    conn = conectar_db()
    cur = conn.cursor()
    try:
        # Verificar si el nombre de usuario o el email ya están registrados
        cur.execute("SELECT email FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            return "Error: Email ya registrado"

        cur.execute("SELECT username FROM users WHERE username = %s", (nombre_usuario,))
        if cur.fetchone():
            return "Error: Nombre de usuario ya registrado"

        # Insertar el nuevo usuario con nombre, apellidos, nombre de usuario, email, password, fecha de nacimiento y rol
        cur.execute("""
            INSERT INTO users (nombre, apellidos, username, email, password, fechaNacimiento, rol)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nombre_usuario, apellidos_usuario, nombre_usuario, email, password, fecha_nacimiento, rol))
        conn.commit()
        return "Usuario registrado con éxito!"
    finally:
        cur.close()
        conn.close()


def eliminar_usuario(user_id):
    conn = conectar_db()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))  # Usar el ID en lugar del email
        conn.commit()
        return "Usuario eliminado"
    finally:
        cur.close()
        conn.close()

