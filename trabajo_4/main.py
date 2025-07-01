import oracledb
import random
import time

# Configuración de conexión a Oracle
def conectar():
    try:
        return oracledb.connect(
            user="system",
            password="Atom", 
            dsn="localhost:1521/XE"
        )
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

# Funciones de carga de datos
def cargar_usuarios():
    usuarios = {}
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT rut, nombre, segundo_nombre, apellido_p, apellido_m, clave FROM usuarios_barber")
            for fila in cursor.fetchall():
                rut, nombre, segundo_nombre, apellido_p, apellido_m, clave = fila
                usuarios[rut] = {
                    "nombre": nombre,
                    "segundo_nombre": segundo_nombre,  
                    "apellido_p": apellido_p,
                    "apellido_m": apellido_m,
                    "clave": clave
                }
        except Exception as e:
            print(f"Error cargando usuarios: {e}")
        finally:
            conn.close()
    return usuarios

def cargar_colaboradores():
    colaboradores = {}
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT nombre, clave FROM colaboradores")
            for nombre, clave in cursor.fetchall():
                colaboradores[nombre] = {"clave": clave, "horario": {}}
        except Exception as e:
            print(f"Error cargando colaboradores: {e}")
        finally:
            conn.close()
    return colaboradores

def cargar_horarios(colaboradores):
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT colaborador, mes, dia, hora, rut_cliente, nombre_cliente FROM horarios")
            for nombre, mes, dia, hora, rut_cliente, nombre_cliente in cursor.fetchall():
                if nombre in colaboradores:
                    colaboradores[nombre]["horario"][(str(mes), str(dia), hora[:2])] = {
                        "rut_cliente": rut_cliente,
                        "nombre": nombre_cliente
                    }
        except Exception as e:
            print(f"Error cargando horarios: {e}")
        finally:
            conn.close()

# Funciones de inserción
def insertar_usuario(rut, nombre, segundo_nombre, apellido_p, apellido_m, clave):
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO usuarios_barber (rut, nombre, segundo_nombre, apellido_p, apellido_m, clave) 
                VALUES (:1, :2, :3, :4, :5, :6)
            """, [rut, nombre, segundo_nombre, apellido_p, apellido_m, clave])
            conn.commit()
            return True
        except Exception as e:
            print(f"Error insertando usuario: {e}")
            conn.rollback()
        finally:
            conn.close()
    return False

def insertar_horario(colaborador, mes, dia, hora, rut_cliente, nombre_cliente):
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO horarios (colaborador, mes, dia, hora, rut_cliente, nombre_cliente) 
                VALUES (:1, :2, :3, :4, :5, :6)
            """, [colaborador, int(mes), int(dia), hora, rut_cliente, nombre_cliente])
            conn.commit()
            return True
        except Exception as e:
            print(f"Error insertando horario: {e}")
            conn.rollback()
        finally:
            conn.close()
    return False

def insertar_pago(rut, nombre, boleta, tipo_pago):
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO pagos (rut, nombre, boleta, tipo_pago) VALUES (:1, :2, :3, :4)", 
                         [rut, nombre, boleta, tipo_pago])
            conn.commit()
            return True
        except Exception as e:
            print(f"Error insertando pago: {e}")
            conn.rollback()
        finally:
            conn.close()
    return False

def insertar_atencion(correo, nombre):
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO atencion_clientes (correo, nombre) VALUES (:1, :2)", [correo, nombre])
            conn.commit()
            return True
        except Exception as e:
            print(f"Error insertando atención al cliente: {e}")
            conn.rollback()
        finally:
            conn.close()
    return False

def eliminar_horario(colaborador, mes, dia, hora):
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM horarios WHERE colaborador = :1 AND mes = :2 AND dia = :3 AND hora = :4",
                         [colaborador, int(mes), int(dia), hora])
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error eliminando horario: {e}")
            conn.rollback()
        finally:
            conn.close()
    return False

# Funciones de utilidad
def validar_entrada(prompt, tipo, rango=None):
    """Valida entrada del usuario con reintentos"""
    intentos = 0
    while intentos < 3:
        entrada = input(prompt).strip()
        if tipo == "numero":
            if entrada.isdigit():
                num = int(entrada)
                if rango and (num < rango[0] or num > rango[1]):
                    print(f"Debe estar entre {rango[0]} y {rango[1]}")
                else:
                    return num
            print("Debe ingresar un número válido")
        elif tipo == "texto" and entrada:
            return entrada
        intentos += 1
    return None

def preguntar_volver_menu():
    while True:
        respuesta = input("\n¿Desea volver al menú principal? (si/no): ").strip().lower()
        if respuesta in ["si", "no"]:
            return respuesta == "si"
        print("Opción inválida. Ingrese 'si' o 'no'.")

# Funciones del menú
def crear_cuenta(usuarios):
    print("=== CREAR CUENTA ===")
    datos = ["primer nombre", "segundo nombre", "apellido paterno", "apellido materno", "clave", "rut"]
    valores = []
    
    for dato in datos:
        valor = input(f"Ingrese {dato}: ").strip()
        valores.append(valor)
    
    rut = valores[-1]
    if rut in usuarios:
        print("El usuario ya existe.")
        return
    
    if insertar_usuario(*valores):
        usuarios[rut] = {
            "nombre": valores[0],
            "segundo_nombre": valores[1],
            "apellido_p": valores[2],
            "apellido_m": valores[3],
            "clave": valores[4]
        }
        print("Usuario creado exitosamente.")
    else:
        print("Error al crear el usuario.")

def iniciar_sesion(usuarios):
    print("=== INICIAR SESIÓN ===")
    rut = input("Ingrese su rut: ").strip()
    clave = input("Ingrese su clave: ")
    
    if rut in usuarios and usuarios[rut]["clave"] == clave:
        print(f"Bienvenido {usuarios[rut]['nombre']} de nuevo!")
    else:
        print("Rut o clave incorrectos.")

def ingreso_colaboradores(colaboradores):
    print("=== INGRESO COLABORADORES ===")
    nombre_colab = input("Ingrese nombre de colaborador (Tomas/Agustin): ")
    
    if nombre_colab not in colaboradores:
        print("Colaborador no encontrado.")
        return
    
    clave = input("Ingrese la clave: ")
    if clave != colaboradores[nombre_colab]["clave"]:
        print("Clave incorrecta.")
        return
    
    print(f"Bienvenido {nombre_colab}!")
    horario = colaboradores[nombre_colab]["horario"]
    
    if not horario:
        print("No tienes horas agendadas.")
        return
    
    print("Tus horas agendadas son:")
    claves_horas = list(horario.keys())
    for idx, clave_h in enumerate(claves_horas, 1):
        mes, dia, hora = clave_h
        print(f"{idx}. Mes: {mes}, Día: {dia}, Hora: {int(hora):02d}:00, Usuario: {horario[clave_h]['nombre']}")
    
    if input("\n¿Deseas editar alguna hora agendada? (si/no): ").lower() == "si":
        num = validar_entrada("Ingresa el número de la hora que deseas editar: ", "numero", (1, len(claves_horas)))
        if num:
            # Lógica de edición simplificada
            clave_a_editar = claves_horas[num-1]
            datos_usuario = horario[clave_a_editar]
            
            nuevo_mes = validar_entrada("Ingrese el nuevo mes (1-12): ", "numero", (1, 12))
            nuevo_dia = validar_entrada("Ingrese el nuevo día (1-31): ", "numero", (1, 31))
            nueva_hora = validar_entrada("Ingrese la nueva hora (9-18): ", "numero", (9, 18))
            
            if all([nuevo_mes, nuevo_dia, nueva_hora]):
                nueva_clave = (str(nuevo_mes), str(nuevo_dia), str(nueva_hora))
                if nueva_clave not in horario:
                    hora_a_eliminar = f"{int(clave_a_editar[2]):02d}:00"
                    if eliminar_horario(nombre_colab, clave_a_editar[0], clave_a_editar[1], hora_a_eliminar):
                        hora_txt = f"{nueva_hora:02d}:00"
                        if insertar_horario(nombre_colab, nuevo_mes, nuevo_dia, hora_txt, 
                                          datos_usuario['rut_cliente'], datos_usuario['nombre']):
                            del horario[clave_a_editar]
                            horario[nueva_clave] = datos_usuario
                            print(f"Hora editada correctamente: {nuevo_dia}-{nuevo_mes}-2025 a las {hora_txt}")
                        else:
                            print("Error al insertar la nueva hora.")
                    else:
                        print("Error al eliminar la hora actual.")
                else:
                    print("Esa hora ya está ocupada.")

def agendar_cita(usuarios, colaboradores):
    print("=== AGENDAR CITA ===")
    rut = input("Ingrese su rut para agendar: ").strip()
    
    if rut not in usuarios:
        print("Debe crear una cuenta primero.")
        return
    
    bar = input(f"{usuarios[rut]['nombre']}, ¿con qué colaborador desea agendar? ({'/'.join(colaboradores.keys())}): ")
    if bar not in colaboradores:
        print("Colaborador inválido.")
        return
    
    # Validación simplificada
    mes = validar_entrada("Ingrese el mes (1-12): ", "numero", (1, 12))
    if not mes: return
    
    max_dia = 28 if mes == 2 else 30 if mes in [4, 6, 9, 11] else 31
    dia = validar_entrada(f"Ingrese el día (1-{max_dia}): ", "numero", (1, max_dia))
    if not dia: return
    
    print("Horas disponibles:")
    for i in range(9, 19):
        print(f"{i-8}- {i}:00")
    
    hora_opcion = validar_entrada("Seleccione su hora (1-10): ", "numero", (1, 10))
    if not hora_opcion: return
    
    hora_real = hora_opcion + 8
    hora_txt = f"{hora_real:02d}:00"
    clave_horario = (str(mes), str(dia), str(hora_real))
    
    if clave_horario in colaboradores[bar]["horario"]:
        print("La hora ya fue agendada.")
        return
    
    if insertar_horario(bar, mes, dia, hora_txt, rut, usuarios[rut]['nombre']):
        colaboradores[bar]["horario"][clave_horario] = {
            "rut_cliente": rut,
            "nombre": usuarios[rut]['nombre']
        }
        print(f"{usuarios[rut]['nombre']} su hora agendada es: {dia}-{mes}-2025 a las {hora_txt}")
        
        # Proceso de pago
        tipo_pago = input("Ingrese tipo de pago:\n1- Efectivo\n2- Tarjeta\n")
        if tipo_pago == "1":
            print("Si deseas pagar con efectivo, contáctate con nosotros en la opción 5.")
        elif tipo_pago == "2":
            boleta = str(random.randint(1000, 9999))
            print(f"Su boleta es: {boleta}")
            if insertar_pago(rut, usuarios[rut]['nombre'], boleta, "Tarjeta"):
                print("¡Gracias por su consulta!")
            else:
                print("Error al procesar el pago.")
    else:
        print("Error al agendar la hora.")

def atencion_cliente():
    print("=== ATENCIÓN AL CLIENTE ===")
    correo = input("Ingrese su correo: ")
    nombre = input("Ingrese su nombre: ")
    
    if insertar_atencion(correo, nombre):
        print("Gracias por contactarnos. Pronto le responderemos.")
    else:
        print("Error al registrar su consulta.")

# Programa principal
def main():
    # Cargar datos iniciales
    usuarios = cargar_usuarios()
    colaboradores = cargar_colaboradores()
    cargar_horarios(colaboradores)
    
    while True:
        print("\n" + "="*40)
        print("        BARBERÍA - SISTEMA DE CITAS")
        print("="*40)
        print("1- Crear cuenta")
        print("2- Iniciar sesión")
        print("3- Ingreso de colaboradores")
        print("4- Agenda")
        print("5- Atención al cliente")
        print("6- Salir")
        print("="*40)
        
        opcion = input("Ingrese una opción: ").strip()
        
        if opcion == "1":
            crear_cuenta(usuarios)
        elif opcion == "2":
            iniciar_sesion(usuarios)
        elif opcion == "3":
            ingreso_colaboradores(colaboradores)
            if not preguntar_volver_menu():
                continue
        elif opcion == "4":
            agendar_cita(usuarios, colaboradores)
            if not preguntar_volver_menu():
                continue
        elif opcion == "5":
            atencion_cliente()
            if not preguntar_volver_menu():
                continue
        elif opcion == "6":
            print("¡Hasta luego!")
            break
        else:
            print("Opción inválida, intente nuevamente.")

if __name__ == "__main__":
    main()
