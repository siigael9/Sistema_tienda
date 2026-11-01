"""Punto de entrada del Sistema de Tienda 2.0."""
from datetime import date
from base_datos import inicializar_base_datos
from productos import listar_productos, buscar_producto, agregar_producto, editar_producto, retirar_producto
from inventario import mostrar_inventario, registrar_reposicion
from ventas import registrar_venta
from estadisticas import mostrar_estadisticas
from historial import mostrar_historial, cerrar_semana, obtener_cierres


def pedir_numero(mensaje, permitir_decimal=True):
    texto = input(mensaje).strip().replace(",", ".")
    numero = float(texto)
    if not permitir_decimal and not numero.is_integer():
        raise ValueError("Escribe un número entero.")
    return numero


def elegir_producto(productos):
    if not productos:
        print("No hay productos disponibles.")
        return None
    for numero, producto in enumerate(productos, start=1):
        print(f"{numero}. {producto['nombre']} | ${producto['precio']:.2f} | "
              f"Stock: {producto['stock']:g} {producto['unidad']}")
    try:
        indice = int(input("Elige el número del producto: ")) - 1
        return productos[indice] if 0 <= indice < len(productos) else None
    except ValueError:
        return None


def menu_productos():
    while True:
        print("\n--- PRODUCTOS ---\n1. Agregar\n2. Editar\n3. Retirar\n4. Buscar\n0. Volver")
        opcion = input("Selecciona una opción: ").strip()
        try:
            if opcion == "0":
                return
            if opcion == "1":
                nombre = input("Nombre: ")
                precio = pedir_numero("Precio: $")
                stock = pedir_numero("Existencias iniciales: ")
                unidad = input("Unidad (pieza, kg, litro...): ")
                agregar_producto(nombre, precio, stock, unidad)
                print("Producto agregado.")
            elif opcion == "2":
                producto = elegir_producto(listar_productos())
                if producto:
                    nombre = input(f"Nombre [{producto['nombre']}]: ").strip() or producto["nombre"]
                    precio_txt = input(f"Precio [{producto['precio']:.2f}]: ").strip()
                    precio = float(precio_txt.replace(",", ".")) if precio_txt else producto["precio"]
                    unidad = input(f"Unidad [{producto['unidad']}]: ").strip() or producto["unidad"]
                    editar_producto(producto["id"], nombre, precio, unidad)
                    print("Producto actualizado. Las ventas anteriores conservan su nombre y precio.")
            elif opcion == "3":
                producto = elegir_producto(listar_productos())
                if producto:
                    retirar_producto(producto["id"])
                    print("Producto retirado; su historial se conserva.")
            elif opcion == "4":
                resultados = buscar_producto(input("Nombre o parte del nombre: "))
                for p in resultados:
                    print(f"{p['nombre']} | ${p['precio']:.2f} | {p['stock']:g} {p['unidad']}")
                if not resultados:
                    print("No se encontraron productos.")
            else:
                print("Opción no válida.")
        except (ValueError, TypeError) as error:
            print("No se pudo completar:", error)
        except Exception as error:
            if "UNIQUE constraint failed" in str(error):
                print("Ya existe un producto con ese nombre.")
            else:
                raise


def nueva_venta():
    carrito = []
    while True:
        productos = listar_productos()
        print("\n--- PRODUCTOS DISPONIBLES ---")
        for numero, p in enumerate(productos, start=1):
            print(f"{numero}. {p['nombre']} | ${p['precio']:.2f} | Stock: {p['stock']:g} {p['unidad']}")
        print("0. Terminar y cobrar")
        try:
            seleccion = int(input("Selecciona un producto: "))
            if seleccion == 0:
                break
            if not 1 <= seleccion <= len(productos):
                print("Producto no válido.")
                continue
            producto = productos[seleccion - 1]
            cantidad = pedir_numero("Cantidad: ")
            if cantidad <= 0:
                print("La cantidad debe ser mayor que cero.")
                continue
            carrito.append((producto["id"], cantidad))
            print("Agregado al carrito.")
        except ValueError as error:
            print("Dato no válido:", error)
    if not carrito:
        print("No se registró una venta.")
        return
    try:
        venta = registrar_venta(carrito)
        print(f"\nSubtotal: ${venta['subtotal']:.2f}")
        print(f"Descuento: ${venta['descuento']:.2f}")
        print(f"TOTAL: ${venta['total']:.2f}")
        print("Venta registrada correctamente.")
    except ValueError as error:
        print("No se registró la venta:", error)


def iniciar():
    inicializar_base_datos()
    print("========================================\n       SISTEMA DE TIENDA 2.0\n========================================")
    while True:
        print("\n--- MENÚ PRINCIPAL ---")
        print("1. Mostrar inventario\n2. Realizar venta\n3. Productos (agregar/editar/retirar/buscar)")
        print("4. Reponer inventario\n5. Estadísticas\n6. Historial de ventas\n7. Cierre semanal manual\n8. Ver cierres\n0. Salir")
        opcion = input("\nSelecciona una opción: ").strip()
        try:
            if opcion == "0":
                print("Cerrando sistema. ¡Gracias!")
                break
            elif opcion == "1":
                mostrar_inventario()
            elif opcion == "2":
                nueva_venta()
            elif opcion == "3":
                menu_productos()
            elif opcion == "4":
                producto = elegir_producto(listar_productos())
                if producto:
                    cantidad = pedir_numero("Cantidad que se agrega: ")
                    nota = input("Nota (opcional): ").strip() or "Reposición"
                    registrar_reposicion(producto["id"], cantidad, nota)
                    print("Reposición registrada.")
            elif opcion == "5":
                mostrar_estadisticas()
            elif opcion == "6":
                mostrar_historial()
            elif opcion == "7":
                print("Se cerrará la semana actual (lunes a domingo):", date.today())
                if input("¿Confirmas el cierre? (s/n): ").strip().lower() == "s":
                    cierre = cerrar_semana()
                    print(f"Cierre listo: {cierre['inicio']} a {cierre['fin']} | "
                          f"{cierre['ventas']} ventas | ${cierre['ingresos']:.2f}")
            elif opcion == "8":
                cierres = obtener_cierres()
                if not cierres:
                    print("Todavía no hay cierres.")
                for c in cierres:
                    print(f"{c['inicio_semana']} a {c['fin_semana']} | {c['numero_ventas']} ventas | ${c['ingresos']:.2f}")
            else:
                print("Opción no válida.")
        except ValueError as error:
            print("No se pudo completar:", error)


if __name__ == "__main__":
    iniciar()
