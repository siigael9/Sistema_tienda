print("========================================")
print("       SISTEMA DE TIENDA DE ABARROTES")
print("========================================")

# INVENTARIO INICIAL
productos = [
	{"nombre": "Leche", "precio": 28.0, "stock": 12, "unidad": "pieza"},
	{"nombre": "Huevo", "precio": 48.0, "stock": 8, "unidad": "docena"},
	{"nombre": "Arroz", "precio": 32.0, "stock": 15, "unidad": "kg"},
	{"nombre": "Frijol", "precio": 38.0, "stock": 10, "unidad": "kg"},
	{"nombre": "Aceite", "precio": 45.0, "stock": 9, "unidad": "litro"},
	{"nombre": "Azucar", "precio": 29.0, "stock": 20, "unidad": "kg"},
	{"nombre": "Galletas", "precio": 18.0, "stock": 14, "unidad": "paquete"},
	{"nombre": "Refresco", "precio": 35.0, "stock": 10, "unidad": "pieza"}
]

ventas = []
total_ventas = 0.0
opcion = 0

while opcion != 6:
	print("\n========================================")
	print("              MENU PRINCIPAL")
	print("========================================")
	print("1. Mostrar inventario")
	print("2. Realizar venta")
	print("3. Buscar producto")
	print("4. Estadisticas")
	print("5. Historial de ventas")
	print("6. Salir")

	try:
		opcion = int(input("\nSelecciona una opcion: "))
	except ValueError:
		print("Debes introducir un numero")
		continue

	if opcion == 1:
		print("\n========== INVENTARIO ==========")
		for i, producto in enumerate(productos, start=1):
			print("\nNumero:", i)
			print("Producto:", producto["nombre"])
			print("Precio: $", producto["precio"])
			print("Existencias:", producto["stock"], producto["unidad"])

	elif opcion == 2:
		carrito = []
		print("\n========== NUEVA COMPRA ==========")

		while True:
			print("\nPRODUCTOS DISPONIBLES")
			for i, producto in enumerate(productos, start=1):
				print(i, producto["nombre"], "$", producto["precio"],
					  "Stock:", producto["stock"], producto["unidad"])
			print("\n0. Finalizar compra")

			try:
				seleccion = int(input("\nSelecciona un producto: "))
			except ValueError:
				print("Seleccion invalida")
				continue

			if seleccion == 0:
				break
			if seleccion < 1 or seleccion > len(productos):
				print("Producto no valido")
				continue

			indice = seleccion - 1
			try:
				cantidad = float(input("Cantidad que deseas comprar: "))
			except ValueError:
				print("Debes introducir una cantidad numerica")
				continue

			if cantidad <= 0:
				print("La cantidad debe ser mayor que cero")
				continue

			producto = productos[indice]
			if producto["unidad"] in ["pieza", "paquete", "docena"] and not cantidad.is_integer():
				print("Este producto requiere cantidades enteras")
				continue

			cantidad_carrito = sum(
				elemento["cantidad"] for elemento in carrito
				if elemento["indice"] == indice
			)
			disponible = producto["stock"] - cantidad_carrito
			if cantidad > disponible:
				print("No hay suficientes existencias")
				print("Disponibles:", disponible, producto["unidad"])
				continue

			carrito.append({
				"indice": indice,
				"nombre": producto["nombre"],
				"cantidad": cantidad,
				"unidad": producto["unidad"],
				"subtotal": producto["precio"] * cantidad
			})
			print("Producto agregado al carrito")

		if carrito:
			subtotal_compra = 0.0
			print("\n========== RESUMEN DE COMPRA ==========")
			for elemento in carrito:
				print(elemento["nombre"], "x", elemento["cantidad"],
					  elemento["unidad"], "$", round(elemento["subtotal"], 2))
				subtotal_compra += elemento["subtotal"]

			descuento = subtotal_compra * 0.10 if subtotal_compra > 500 else 0
			total = subtotal_compra - descuento
			print("\nSubtotal: $", round(subtotal_compra, 2))
			print("Descuento: $", round(descuento, 2))
			print("TOTAL: $", round(total, 2))

			for elemento in carrito:
				productos[elemento["indice"]]["stock"] -= elemento["cantidad"]

			ventas.append({
				"productos": carrito.copy(),
				"subtotal": subtotal_compra,
				"descuento": descuento,
				"total": total
			})
			total_ventas += total
			print("\nCompra registrada correctamente")
		else:
			print("No se agregaron productos")

	elif opcion == 3:
		print("\n========== BUSCAR PRODUCTO ==========")
		busqueda = input("Nombre del producto: ").lower()
		encontrado = False
		for producto in productos:
			if busqueda in producto["nombre"].lower():
				print("\nProducto encontrado")
				print("Nombre:", producto["nombre"])
				print("Precio: $", producto["precio"])
				print("Existencias:", producto["stock"])
				print("Unidad:", producto["unidad"])
				encontrado = True
		if not encontrado:
			print("No se encontro el producto")

	elif opcion == 4:
		print("\n========== ESTADISTICAS ==========")
		print("Productos registrados:", len(productos))
		print("Ventas realizadas:", len(ventas))
		print("Ingresos acumulados: $", round(total_ventas, 2))
		if ventas:
			print("Promedio por venta: $", round(total_ventas / len(ventas), 2))
		else:
			print("Promedio por venta: $0")
		productos_agotados = sum(1 for producto in productos if producto["stock"] == 0)
		print("Productos agotados:", productos_agotados)
		producto_mas_caro = max(productos, key=lambda producto: producto["precio"])
		print("Producto mas caro:", producto_mas_caro["nombre"])
		print("Precio: $", producto_mas_caro["precio"])

	elif opcion == 5:
		print("\n========== HISTORIAL DE VENTAS ==========")
		if not ventas:
			print("Todavia no hay ventas registradas")
		else:
			for i, venta in enumerate(ventas, start=1):
				print("\nVenta numero:", i)
				for elemento in venta["productos"]:
					print(elemento["nombre"], "x", elemento["cantidad"],
						  elemento["unidad"], "$", round(elemento["subtotal"], 2))
				print("Subtotal: $", round(venta["subtotal"], 2))
				print("Descuento: $", round(venta["descuento"], 2))
				print("Total: $", round(venta["total"], 2))

	elif opcion == 6:
		print("\nCerrando sistema...")
	else:
		print("Opcion no valida")

print("\n========================================")
print("              REPORTE FINAL")
print("========================================")
print("Ventas realizadas:", len(ventas))
print("Ingresos totales: $", round(total_ventas, 2))
print("\nINVENTARIO RESTANTE")
for producto in productos:
	print(producto["nombre"], "-", producto["stock"], producto["unidad"])
print("\nGracias por utilizar el sistema")
print("========================================")
