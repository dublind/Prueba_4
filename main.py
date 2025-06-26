import os
import oracledb
import random

# Configuración de la conexión a Oracle
def get_connection():
    try:
        connection = oracledb.connect(
            user="system",
            password="Atom", 
            dsn="localhost:1521/XE"  # Ajusta según tu configuración
        )
        return connection
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def cargar_usuarios():
    usuarios = {}
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT rut, nombre, segundo_nombre, apellido_p, apellido_m, clave FROM usuarios_barber")
            for row in cursor.fetchall():
                rut, nombre, segundo_nombre, apellido_p, apellido_m, clave = row
                usuarios[rut] = {
                    "nombre": nombre,
                    "segundo_nombre": segundo_nombre,
                    "apellido_p": apellido_p,
                    "apellido_m": apellido_m,
                    "clave": clave
                }
            cursor.close()
        except Exception as e:
            print(f"Error cargando usuarios: {e}")
        finally:
            conn.close()
    return usuarios

def cargar_colaboradores():
    colaboradores = {}
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT nombre, clave FROM colaboradores")
            for row in cursor.fetchall():
                nombre, clave = row
                colaboradores[nombre] = {"clave": clave, "horario": {}}
            cursor.close()
        except Exception as e:
            print(f"Error cargando colaboradores: {e}")
        finally:
            conn.close()
    return colaboradores

def cargar_horarios(colaboradores):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT colaborador, mes, dia, hora, rut_cliente, nombre_cliente FROM horarios")
            for row in cursor.fetchall():
                nombre, mes, dia, hora, rut_cliente, nombre_cliente = row
                if nombre in colaboradores:
                    colaboradores[nombre]["horario"][(str(mes), str(dia), hora[:2])] = {
                        "rut_cliente": rut_cliente,
                        "nombre": nombre_cliente
                    }
            cursor.close()
        except Exception as e:
            print(f"Error cargando horarios: {e}")
        finally:
            conn.close()

def cargar_pagos():
    pagos = []
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT rut, nombre, boleta, tipo_pago FROM pagos")
            for row in cursor.fetchall():
                rut, nombre, boleta, tipo_pago = row
                pagos.append({
                    "rut": rut,
                    "nombre": nombre,
                    "boleta": boleta,
                    "tipo_pago": tipo_pago
                })
            cursor.close()
        except Exception as e:
            print(f"Error cargando pagos: {e}")
        finally:
            conn.close()
    return pagos

def cargar_atencion():
    atencion_clientes = []
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT correo, nombre FROM atencion_clientes")
            for row in cursor.fetchall():
                correo, nombre = row
                atencion_clientes.append({
                    "correo": correo,
                    "nombre": nombre
                })
            cursor.close()
        except Exception as e:
            print(f"Error cargando atención al cliente: {e}")
        finally:
            conn.close()
    return atencion_clientes

def insertar_usuario(rut, nombre, segundo_nombre, apellido_p, apellido_m, clave):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO usuarios_barber (rut, nombre, segundo_nombre, apellido_p, apellido_m, clave) 
                VALUES (:1, :2, :3, :4, :5, :6)
            """, [rut, nombre, segundo_nombre, apellido_p, apellido_m, clave])
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error insertando usuario: {e}")
            conn.rollback()
        finally:
            conn.close()
    return False

def insertar_horario(colaborador, mes, dia, hora, rut_cliente, nombre_cliente):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO horarios (colaborador, mes, dia, hora, rut_cliente, nombre_cliente) 
                VALUES (:1, :2, :3, :4, :5, :6)
            """, [colaborador, int(mes), int(dia), hora, rut_cliente, nombre_cliente])
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error insertando horario: {e}")
            conn.rollback()
        finally:
            conn.close()
    return False

def insertar_pago(rut, nombre, boleta, tipo_pago):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO pagos (rut, nombre, boleta, tipo_pago) 
                VALUES (:1, :2, :3, :4)
            """, [rut, nombre, boleta, tipo_pago])
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error insertando pago: {e}")
            conn.rollback()
        finally:
            conn.close()
    return False

def insertar_atencion(correo, nombre):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO atencion_clientes (correo, nombre) 
                VALUES (:1, :2)
            """, [correo, nombre])
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error insertando atención al cliente: {e}")
            conn.rollback()
        finally:
            conn.close()
    return False

def eliminar_horario(colaborador, mes, dia, hora):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM horarios 
                WHERE colaborador = :1 AND mes = :2 AND dia = :3 AND hora = :4
            """, [colaborador, int(mes), int(dia), hora])
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error eliminando horario: {e}")
            conn.rollback()
        finally:
            conn.close()
    return False

def preguntar_volver_menu():
    while True:
        print("\n¿Desea volver al menú principal? (si/no)")
        volver = input().strip().lower()
        if volver == "si":
            return True
        elif volver == "no":
            return False
        else:
            print("Opción inválida. Ingrese 'si' para sí o 'no' para no.")

# Cargar datos iniciales
usuarios = cargar_usuarios()
colaboradores = cargar_colaboradores()
cargar_horarios(colaboradores)
pagos = cargar_pagos()
atencion_clientes = cargar_atencion()

menu = True
while menu:
    print("\nIngrese la opcion deseada: ")
    print("1- Crear cuenta")
    print("2- Iniciar sesion")
    print("3- Ingreso de colaboradores")
    print("4- Agenda")
    print("5- Atencion al cliente")
    print("6- Salir\n")
    print("Ingrese una opcion: ")
    opcion = input()

    if opcion == "1":
        print("Ingrese primer nombre del usuario: ")
        nombre = input()
        print("Ingrese segundo nombre: ")
        segundo_nombre = input()
        print("Ingrese apellido paterno: ")
        apellido_p = input()
        print("Ingrese apellido materno: ")
        apellido_m = input()
        print("Ingrese clave: ")
        clave = input()
        print("Ingrese rut: ")
        rut = input().strip()
        if rut in usuarios:
            print("El usuario ya existe.")
        else:
            if insertar_usuario(rut, nombre, segundo_nombre, apellido_p, apellido_m, clave):
                usuarios[rut] = {
                    "nombre": nombre,
                    "segundo_nombre": segundo_nombre,
                    "apellido_p": apellido_p,
                    "apellido_m": apellido_m,
                    "clave": clave
                }
                print("Usuario creado exitosamente.")
            else:
                print("Error al crear el usuario.")

    elif opcion == "2":
        print("Ingrese su rut: ")
        rut = input().strip()
        print("Ingrese su clave: ")
        clave = input()
        if rut in usuarios and usuarios[rut]["clave"] == clave:
            print(f"Bienvenido {usuarios[rut]['nombre']} de nuevo!")
        else:
            print("Rut o clave incorrectos.")

    elif opcion == "3":
        seguir = True
        while seguir:
            print("Ingrese nombre de colaborador (Tomas/Agustin): ")
            nombre_colab = input()
            if nombre_colab in colaboradores:
                print("Ingrese la clave: ")
                clave = input()
                if clave == colaboradores[nombre_colab]["clave"]:
                    print(f"Bienvenido {nombre_colab}!")
                    horario = colaboradores[nombre_colab]["horario"]
                    if not horario:
                        print("No tienes horas agendadas.")
                    else:
                        print("Tus horas agendadas son:")
                        claves_horas = list(horario.keys())
                        for idx, clave_h in enumerate(claves_horas, 1):
                            mes, dia, hora = clave_h
                            print(f"{idx}. Mes: {mes}, Día: {dia}, Hora: {int(hora):02d}:00, Usuario: {horario[clave_h]['nombre']}")
                        print("\n¿Deseas editar alguna hora agendada? (si/no)")
                        editar = input().lower()
                        if editar == "si":
                            print("Ingresa el número de la hora que deseas editar:")
                            try:
                                num = int(input())
                                if 1 <= num <= len(claves_horas):
                                    clave_a_editar = claves_horas[num-1]
                                    datos_usuario = horario[clave_a_editar]
                                    del horario[clave_a_editar]
                                    
                                    # Eliminar de la base de datos
                                    eliminar_horario(nombre_colab, clave_a_editar[0], clave_a_editar[1], f"{clave_a_editar[2]}:00")
                                    
                                    print("Ingrese el nuevo mes (1-12):")
                                    nuevo_mes = input().strip()
                                    print("Ingrese el nuevo día:")
                                    nuevo_dia = input().strip()
                                    print("Ingrese la nueva hora (9-18):")
                                    nueva_hora = input().strip()
                                    if not nueva_hora.isdigit() or not (9 <= int(nueva_hora) <= 18):
                                        print("Hora inválida. Debe ser entre 9 y 18.")
                                    else:
                                        nueva_clave = (nuevo_mes, nuevo_dia, nueva_hora)
                                        if nueva_clave in horario:
                                            print("Esa hora ya está ocupada.")
                                        else:
                                            hora_txt = f"{int(nueva_hora):02d}:00"
                                            if insertar_horario(nombre_colab, nuevo_mes, nuevo_dia, hora_txt, datos_usuario['rut_cliente'], datos_usuario['nombre']):
                                                horario[nueva_clave] = datos_usuario
                                                print(f"Hora editada y guardada correctamente: {nuevo_dia}-{nuevo_mes}-2025 a las {hora_txt}")
                                            else:
                                                print("Error al actualizar la hora.")
                                else:
                                    print("Número inválido.")
                            except ValueError:
                                print("Entrada inválida.")
                else:
                    print("Clave incorrecta.")
            else:
                print("Colaborador no encontrado.")
            if preguntar_volver_menu():
                seguir = False

    elif opcion == "4":
        seguir = True
        while seguir:
            print("Ingrese su rut para agendar: ")
            rut = input().strip()
            if rut not in usuarios:
                print("Debe crear una cuenta primero.")
            else:
                print(f"{usuarios[rut]['nombre']}, ¿con qué colaborador desea agendar? ({'/'.join(colaboradores.keys())})")
                bar = input()
                if bar not in colaboradores:
                    print("Colaborador inválido.")
                else:
                    # Intentos para el mes
                    intentos_mes = 0
                    mes_valido = False
                    while intentos_mes < 3 and not mes_valido:
                        print("Ingrese el mes en el cual desea agendar (entre 1 y 12): ")
                        mes = input().strip()
                        if mes.isdigit() and (1 <= int(mes) <= 12):
                            mes_valido = True
                        else:
                            print("Mes inválido.")
                            intentos_mes += 1
                    if not mes_valido:
                        print("Demasiados intentos inválidos para el mes.")
                        if preguntar_volver_menu():
                            seguir = False
                        continue

                    # Intentos para el día
                    if int(mes) == 2:
                        max_dia = 28
                    elif int(mes) in [4, 6, 9, 11]:
                        max_dia = 30
                    else:
                        max_dia = 31
                    intentos_dia = 0
                    dia_valido = False
                    while intentos_dia < 3 and not dia_valido:
                        print(f"Ingrese el día (entre 1 y {max_dia}): ")
                        dia = input().strip()
                        if dia.isdigit() and (1 <= int(dia) <= max_dia):
                            dia_valido = True
                        else:
                            print("Día inválido.")
                            intentos_dia += 1
                    if not dia_valido:
                        print("Demasiados intentos inválidos para el día.")
                        if preguntar_volver_menu():
                            seguir = False
                        continue

                    # Intentos para la hora
                    print("Horas disponibles:")
                    for i in range(9, 19):
                        print(f"{i-8}- {i}:00")
                    intentos_hora = 0
                    hora_valida = False
                    while intentos_hora < 3 and not hora_valida:
                        print("Seleccione su hora (entre 9:00 y 18:00 horas)")
                        hora = input().strip()
                        if hora.isdigit() and (1 <= int(hora) <= 10):
                            hora_valida = True
                        else:
                            print("Hora inválida.")
                            intentos_hora += 1
                    if not hora_valida:
                        print("Demasiados intentos inválidos para la hora.")
                        if preguntar_volver_menu():
                            seguir = False
                        continue

                    hora_real = int(hora) + 8
                    hora_txt = f"{hora_real:02d}:00"
                    clave_horario = (mes, dia, str(hora_real))
                    horario = colaboradores[bar]["horario"]
                    if clave_horario in horario:
                        print("La hora ya fue agendada, por favor intente nuevamente con otra hora.")
                    else:
                        if insertar_horario(bar, mes, dia, hora_txt, rut, usuarios[rut]['nombre']):
                            horario[clave_horario] = {
                                "rut_cliente": rut,
                                "nombre": usuarios[rut]['nombre']
                            }
                            print(f"{usuarios[rut]['nombre']} su hora agendada es: {dia}-{mes}-2025 a las {hora_txt}")
                            print("Ingrese tipo de pago: ")
                            print("1- Efectivo \n2- Tarjeta")
                            tipo_pago = input()
                            if tipo_pago == "1":
                                print("Si deseas pagar con efectivo, contáctate con nosotros en la opción 5.")
                                print(f"Hasta luego {usuarios[rut]['nombre']}")
                            elif tipo_pago == "2":
                                boleta = str(random.randint(1000, 9999))
                                print(f"Su boleta es: {boleta}")
                                if insertar_pago(rut, usuarios[rut]['nombre'], boleta, "Tarjeta"):
                                    pagos.append({
                                        "nombre": usuarios[rut]['nombre'],
                                        "rut": rut,
                                        "boleta": boleta,
                                        "tipo_pago": "Tarjeta"
                                    })
                                    print("¡Gracias por su consulta!")
                                else:
                                    print("Error al procesar el pago.")
                            else:
                                print("Tipo de pago inválido.")
                        else:
                            print("Error al agendar la hora.")
            if preguntar_volver_menu():
                seguir = False

    elif opcion == "5":
        seguir = True
        while seguir:
            print("Ingrese su correo: ")
            correo = input()
            print("Ingrese su nombre: ")
            nombre = input()
            if insertar_atencion(correo, nombre):
                atencion_clientes.append({
                    "correo": correo,
                    "nombre": nombre
                })
                print("Gracias por contactarnos. Pronto le responderemos.")
            else:
                print("Error al registrar su consulta.")
            if preguntar_volver_menu():
                seguir = False

    elif opcion == "6":
        print("¡Hasta luego!")
        menu = False

    else:
        print("Opción inválida, intente nuevamente.")
