"""Historial de ventas y cierres semanales manuales."""
from datetime import date, datetime, timedelta
from base_datos import conectar
from ventas import obtener_ventas, obtener_detalle_venta


def mostrar_historial():
    ventas = obtener_ventas()
    print("\n--- HISTORIAL DE VENTAS ---")
    if not ventas:
        print("Todavía no hay ventas registradas.")
        return
    for venta in ventas:
        print(f"\nVenta #{venta['id']} | {venta['fecha']}")
        for linea in obtener_detalle_venta(venta["id"]):
            print(f"  {linea['nombre_producto']} x {linea['cantidad']:g} {linea['unidad']} "
                  f"@ ${linea['precio_unitario']:.2f} = ${linea['subtotal']:.2f}")
        print(f"  Subtotal: ${venta['subtotal']:.2f} | Descuento: ${venta['descuento']:.2f} "
              f"| Total: ${venta['total']:.2f}")


def cerrar_semana(fecha_referencia=None):
    """Cierra la semana lunes-domingo que contiene la fecha indicada o hoy."""
    dia = fecha_referencia or date.today()
    if isinstance(dia, str):
        dia = date.fromisoformat(dia)
    inicio = dia - timedelta(days=dia.weekday())
    fin = inicio + timedelta(days=6)
    inicio_txt, fin_txt = inicio.isoformat(), fin.isoformat()
    with conectar() as conexion:
        existente = conexion.execute(
            "SELECT * FROM cierres_semanales WHERE inicio_semana = ?", (inicio_txt,)
        ).fetchone()
        if existente:
            raise ValueError(f"La semana {inicio_txt} a {fin_txt} ya se cerró.")
        resumen = conexion.execute(
            "SELECT COUNT(*) AS cantidad, COALESCE(SUM(total), 0) AS ingresos FROM ventas WHERE date(fecha) BETWEEN ? AND ?",
            (inicio_txt, fin_txt),
        ).fetchone()
        conexion.execute(
            "INSERT INTO cierres_semanales (inicio_semana, fin_semana, fecha_cierre, numero_ventas, ingresos) VALUES (?, ?, ?, ?, ?)",
            (inicio_txt, fin_txt, datetime.now().isoformat(timespec="seconds"), resumen["cantidad"], resumen["ingresos"]),
        )
        return {"inicio": inicio_txt, "fin": fin_txt, "ventas": resumen["cantidad"], "ingresos": resumen["ingresos"]}


def obtener_cierres():
    with conectar() as conexion:
        return conexion.execute("SELECT * FROM cierres_semanales ORDER BY inicio_semana").fetchall()

