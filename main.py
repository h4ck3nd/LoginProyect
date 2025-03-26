import subprocess
import threading
import time
import flet as ft
from ddbbLogin import *
from datetime import datetime

def main(page: ft.Page):
    page.title = "LOGIN HACKEND"
    page.window_width = 400
    page.window_height = 600
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    # Campos de entrada
    nombre_usuario = ft.TextField(label="Nombre de Usuario", autofocus=True)
    apellidos = ft.TextField(label="Apellidos de Usuario")
    email = ft.TextField(label="Email")
    password = ft.TextField(label="Contraseña", password=True)
    fecha_nacimiento = ft.TextField(label="Fecha de Nacimiento (YYYY-MM-DD)")
    mensaje = ft.Text()

    # Dropdown para elegir el rol
    rol = ft.Dropdown(
        label="Selecciona el rol",
        options=[
            ft.dropdown.Option("user", "Usuario"),
            ft.dropdown.Option("admin", "Administrador")
        ],
        value="user"  # Valor por defecto
    )

    def set_mensaje(texto, color="green"):
        mensaje.value = texto
        mensaje.color = color
        page.update()

    def limpiar_campos():
        nombre_usuario.value = ""
        apellidos.value = ""
        email.value = ""
        password.value = ""
        fecha_nacimiento.value = ""
        mensaje.value = ""
        rol.value = None  # Limpiar el valor del rol
        page.update()

    def register(e):
        try:
            # Verificar si el formato de la fecha es correcto
            datetime.strptime(fecha_nacimiento.value, "%Y-%m-%d")
        except ValueError:
            set_mensaje("Error: Formato de fecha incorrecto. Usa YYYY-MM-DD.", "red")
            return

        # Verificar que el nombre de usuario no esté vacío
        if not nombre_usuario.value:
            set_mensaje("Error: El nombre de usuario no puede estar vacío.", "red")
            return

        # Verificar que el campo de apellidos no esté vacío
        if not apellidos.value:
            set_mensaje("Error: Los apellidos no pueden estar vacíos.", "red")
            return

        # Verificar que el campo de email no esté vacío
        if not email.value:
            set_mensaje("Error: El email no puede estar vacío.", "red")
            return

        # Verificar que el campo de contraseña no esté vacío
        if not password.value:
            set_mensaje("Error: La contraseña no puede estar vacía.", "red")
            return

        # Verificar que se haya seleccionado un rol
        if not rol.value:
            set_mensaje("Error: Debes seleccionar un rol (Usuario o Administrador).", "red")
            return

        # Registrar usuario con nombre de usuario, apellidos, email, password, fecha de nacimiento y rol
        msg = registrar_usuario(nombre_usuario.value, apellidos.value, email.value, password.value,
                                fecha_nacimiento.value, rol.value)
        set_mensaje(msg, "green" if "éxito" in msg else "red")
        if "éxito" in msg:
            limpiar_campos()

    def mostrar_registro(e=None):
        limpiar_campos()
        page.clean()
        page.add(
            ft.Column([
                nombre_usuario, apellidos, email, password, fecha_nacimiento, rol, mensaje,
                ft.ElevatedButton("Registrar", on_click=register, bgcolor="green", color="white"),
                ft.ElevatedButton("Volver", on_click=mostrar_login, bgcolor="gray", color="white")
            ], alignment="center")
        )
        page.update()

    def instalar_ddbb(e):
        """Función para ejecutar el script y mostrar la barra de progreso."""

        def ejecutar_script():
            progreso.value = 0
            progreso.visible = True
            page.update()

            # Simulación de progreso mientras se ejecuta el script
            for i in range(1, 11):  # Divide el progreso en 10 pasos
                time.sleep(1)  # Simula tiempo de ejecución
                progreso.value = i / 10  # Incrementa el progreso
                page.update()

            # Ejecutar el script Bash
            proceso = subprocess.run(["bash", "installDDBB.sh"], capture_output=True, text=True)

            # Ocultar barra y mostrar mensaje de éxito o error
            progreso.visible = False
            if proceso.returncode == 0:
                mensaje.value = "✅ Instalación completada correctamente."
            else:
                mensaje.value = f"❌ Error en la instalación:\n{proceso.stderr}"

            page.update()

        # Ejecutar en un hilo para no bloquear la interfaz
        threading.Thread(target=ejecutar_script, daemon=True).start()

    def mostrar_login(e=None):
        limpiar_campos()
        page.clean()
        email.label = "Email/Usuario"

        global progreso, mensaje
        progreso = ft.ProgressBar(width=300, visible=False)  # Barra de progreso oculta al inicio
        mensaje = ft.Text("", color="red")  # Mensaje de estado

        page.add(
            ft.Column([
                email, password, mensaje,
                ft.ElevatedButton("Iniciar sesión", on_click=login, bgcolor="blue", color="white"),
                ft.ElevatedButton("Registrarse", on_click=mostrar_registro, bgcolor="green", color="white"),
                ft.ElevatedButton("Instalar DDBB (Local)", on_click=instalar_ddbb, bgcolor="orange", color="white"),
                progreso  # Agregar la barra de progreso
            ], alignment="center")
        )
        page.update()

    def login(e):
        user = verificar_usuario(email.value, password.value)
        if user:
            ultimo_login = user[9] if user[9] else "Nunca"
            set_mensaje("Login exitoso!", "green")
            page.clean()

            # Imprimir el valor del rol para verificarlo
            print(f"Rol del usuario: {user[10]}")  # Esto es para ver el valor real del rol en la base de datos.

            # Verificar si el usuario tiene rol de admin
            if user[10] == "admin":  # Asegúrate de que user[10] tiene el rol de admin
                mostrar_home(user[1], ultimo_login, es_admin=True)
            else:
                mostrar_home(user[1], ultimo_login, es_admin=False)
        else:
            set_mensaje("Email/Usuario o contraseña incorrectos. Por favor, intenta nuevamente.", "red")

    def realizar_backup(e):
        page.clean()
        ruta_origen = ft.TextField(label="Ruta de origen")
        ruta_destino = ft.TextField(label="Ruta de destino")
        frecuencia_minutos = ft.TextField(label="Frecuencia en minutos")

        def ejecutar_backup(e):
            origen = ruta_origen.value
            destino = ruta_destino.value
            frecuencia = frecuencia_minutos.value
            if origen and destino and frecuencia:
                subprocess.run(["bash", "backup.sh", origen, destino, frecuencia])
                mostrar_home("Usuario", "Nunca", es_admin=True)

        page.add(
            ft.Column([
                ft.Text("Configurar Backup", size=20, weight="bold", color="blue"),
                ruta_origen,
                ruta_destino,
                frecuencia_minutos,
                ft.ElevatedButton("Ejecutar Backup", on_click=ejecutar_backup, bgcolor="green", color="white"),
                ft.ElevatedButton("Volver", on_click=lambda e: mostrar_home("Usuario", "Nunca", es_admin=True),
                                  bgcolor="gray", color="white")
            ], alignment="center")
        )
        page.update()

    def actualizar_procesos(lista_procesos_column, page):
        procesos = subprocess.run(["ps", "aux"], capture_output=True, text=True)
        procesos_lista = procesos.stdout.splitlines()

        # Limpiar la lista y agregar los procesos actualizados
        lista_procesos_column.controls.clear()
        for p in procesos_lista:
            lista_procesos_column.controls.append(ft.Text(p, size=12))

        lista_procesos_column.update()

        # Recargar la lista automáticamente cada 5 segundos
        page.after(5000, lambda: actualizar_procesos(lista_procesos_column, page))

    def matar_proceso(e):
        page = e.page  # Obtener la página correctamente
        page.controls.clear()  # Limpiar la pantalla sin errores

        proceso_pid = ft.TextField(label="Número de PID")
        lista_procesos_column = ft.ListView(expand=True, spacing=5, auto_scroll=True)

        def ejecutar_matar(e):
            pid = proceso_pid.value
            if pid:
                subprocess.run(["bash", "killPID.sh", pid])
                proceso_pid.value = ""  # Limpiar el campo después de matar el proceso
                proceso_pid.update()
                actualizar_procesos(lista_procesos_column, page)  # Actualizar la lista sin salir

        # Agregar elementos a la página
        page.add(
            ft.Column([
                ft.Text("Matar un Proceso", size=20, weight="bold", color="red"),
                proceso_pid,
                ft.ElevatedButton("Matar Proceso", on_click=ejecutar_matar, bgcolor="black", color="white"),
                ft.Container(
                    lista_procesos_column,
                    border=ft.border.all(1),
                    padding=10,
                    height=300  # Altura fija para permitir desplazamiento
                ),
                ft.ElevatedButton("Volver", on_click=lambda e: mostrar_home("Usuario", "Nunca", es_admin=True),
                                  bgcolor="gray", color="white")
            ], alignment="center")
        )

        # Iniciar la actualización automática de los procesos
        actualizar_procesos(lista_procesos_column, page)
        page.update()

    def mostrar_home(nombre_usuario, ultimo_login, es_admin=False):
        page.clean()
        column_elements = [
            ft.Text(f"Bienvenido, {nombre_usuario}!", size=20, weight="bold", color="blue"),
            ft.Text(f"Último login: {ultimo_login}", size=14, italic=True, color="gray"),
            ft.ElevatedButton("Cerrar sesión", on_click=logout, bgcolor="blue", color="white"),
            ft.ElevatedButton("Eliminar cuenta", on_click=eliminar, bgcolor="red", color="white"),
            ft.ElevatedButton("Realizar Backup", on_click=realizar_backup, bgcolor="green", color="white"),
            ft.ElevatedButton("Matar Proceso", on_click=matar_proceso, bgcolor="black", color="white")
        ]

        if es_admin:
            column_elements.append(
                ft.ElevatedButton("Panel de Administrador",
                                  on_click=lambda e: panel_admin(nombre_usuario, ultimo_login), bgcolor="purple",
                                  color="white")
            )

        page.add(ft.Column(column_elements, alignment="center"))
        page.update()

    def panel_admin(nombre_usuario, ultimo_login):
        page.clean()
        page.add(
            ft.Text("Bienvenido al Panel de Administrador", size=20, weight="bold", color="blue"),
            # Aquí puedes agregar el contenido del panel de administrador
            ft.ElevatedButton("Volver al inicio",
                              on_click=lambda e: mostrar_home(nombre_usuario, ultimo_login, es_admin=True),
                              bgcolor="gray", color="white")
        )
        page.update()

    def eliminar(e):
        user = verificar_usuario(email.value, password.value)
        print(f"Datos del usuario: {user}")  # Verificar que estás obteniendo toda la tupla
        if user:
            user_id = user[0]  # Obtener el ID del usuario
            print(f"El ID del usuario a eliminar es: {user_id}")  # Ver el ID
            mensaje = eliminar_usuario(user_id)  # Pasar el ID a la función de eliminación
            set_mensaje(mensaje, "green" if "eliminado" in mensaje else "red")
            limpiar_campos()
            mostrar_login()
        else:
            set_mensaje("No se pudo eliminar la cuenta.", "red")

    def logout(e):
        limpiar_campos()
        mostrar_login()

    mostrar_login()


if __name__ == "__main__":
    ft.app(target=main)
