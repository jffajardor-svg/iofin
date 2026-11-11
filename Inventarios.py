
from datetime import datetime, timedelta

# INVENTARIO DIGITAL - PEPS, UEPS, KARDEX Y ABC

inventario = {}
kardex = []
catalogo = {}

# Registrar un recurso digital
def registrar_recurso(codigo, nombre, categoria, costo_mensual):
    inventario[codigo] = []
    catalogo[codigo] = {
        "nombre": nombre,
        "categoria": categoria,
        "costo_mensual": costo_mensual
    }

# Registrar entradas al inventario
def entrada(codigo, cantidad, costo, vencimiento, usuario="Administrador"):
    if codigo not in inventario or cantidad <= 0 or costo < 0:
        print("Datos incorrectos.")
        return

    lote = {
        "cantidad": cantidad,
        "costo": costo,
        "vencimiento": datetime.strptime(vencimiento, "%Y-%m-%d").date()
    }

    inventario[codigo].append(lote)

    registrar_movimiento(
        codigo, "ENTRADA", cantidad, costo, usuario
    )

    print("Entrada registrada correctamente.")

# Registrar movimientos en KARDEX
def registrar_movimiento(codigo, tipo, cantidad, costo, usuario):
    saldo = sum(lote["cantidad"] for lote in inventario[codigo])
    valor = sum(
        lote["cantidad"] * lote["costo"]
        for lote in inventario[codigo]
    )

    kardex.append({
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "recurso": catalogo[codigo]["nombre"],
        "tipo": tipo,
        "cantidad": cantidad,
        "costo": costo,
        "total": cantidad * costo,
        "saldo": saldo,
        "valor_inventario": valor,
        "usuario": usuario
    })

# Salidas mediante PEPS o UEPS
def salida(codigo, cantidad, metodo="PEPS", usuario="Desarrollador"):
    if codigo not in inventario or cantidad <= 0:
        print("Datos incorrectos.")
        return

    lotes = inventario[codigo]

    if cantidad > sum(l["cantidad"] for l in lotes):
        print("No hay existencias suficientes.")
        return

    if metodo == "PEPS":
        lotes.sort(key=lambda x: x["vencimiento"])
    elif metodo == "UEPS":
        lotes.sort(key=lambda x: x["vencimiento"], reverse=True)
    else:
        print("Método no válido.")
        return

    pendiente = cantidad
    costo_total = 0

    for lote in list(lotes):
        if pendiente == 0:
            break

        consumido = min(pendiente, lote["cantidad"])
        costo_total += consumido * lote["costo"]

        lote["cantidad"] -= consumido
        pendiente -= consumido

        if lote["cantidad"] == 0:
            lotes.remove(lote)

    costo_promedio = costo_total / cantidad

    registrar_movimiento(
        codigo, metodo, cantidad, costo_promedio, usuario
    )

    print(f"Salida registrada con {metodo}.")
    print(f"Costo total: ${costo_total:,.2f}")

# Consultar KARDEX
def mostrar_kardex():
    print("\n========== KARDEX ==========")

    for m in kardex:
        print(
            f"Fecha: {m['fecha']} | "
            f"Recurso: {m['recurso']} | "
            f"Movimiento: {m['tipo']} | "
            f"Cantidad: {m['cantidad']} | "
            f"Costo unitario: ${m['costo']:,.2f} | "
            f"Total: ${m['total']:,.2f} | "
            f"Saldo: {m['saldo']} | "
            f"Usuario: {m['usuario']}"
        )

# Consultar existencias
def mostrar_inventario():
    print("\n========== INVENTARIO ==========")

    for codigo, lotes in inventario.items():
        cantidad = sum(l["cantidad"] for l in lotes)
        valor = sum(
            l["cantidad"] * l["costo"] for l in lotes
        )

        print(f"\nRecurso: {catalogo[codigo]['nombre']}")
        print(f"Categoría: {catalogo[codigo]['categoria']}")
        print(f"Cantidad disponible: {cantidad}")
        print(f"Valor del inventario: ${valor:,.2f}")

# Clasificación ABC
def clasificacion_abc():
    print("\n========== CLASIFICACIÓN ABC ==========")

    recursos = sorted(
        catalogo.items(),
        key=lambda x: x[1]["costo_mensual"],
        reverse=True
    )

    total = sum(
        datos["costo_mensual"]
        for datos in catalogo.values()
    )

    acumulado = 0

    for codigo, datos in recursos:
        costo = datos["costo_mensual"]
        porcentaje = (costo / total * 100) if total else 0
        acumulado += porcentaje

        if acumulado <= 80:
            clase = "A"
        elif acumulado <= 95:
            clase = "B"
        else:
            clase = "C"

        print(
            f"{datos['nombre']} | "
            f"Costo mensual: ${costo:,.2f} | "
            f"Participación: {porcentaje:.2f}% | "
            f"Acumulado: {acumulado:.2f}% | "
            f"Clase: {clase}"
        )

# Alertas de vencimiento
def alertas_vencimiento(dias=30):
    print("\n========== ALERTAS DE VENCIMIENTO ==========")

    hoy = datetime.now().date()
    limite = hoy + timedelta(days=dias)
    encontrado = False

    for codigo, lotes in inventario.items():
        for lote in lotes:
            fecha = lote["vencimiento"]

            if fecha <= limite:
                encontrado = True

                if fecha < hoy:
                    estado = "VENCIDO"
                else:
                    estado = "PRÓXIMO A VENCER"

                print(
                    f"{catalogo[codigo]['nombre']} | "
                    f"Cantidad: {lote['cantidad']} | "
                    f"Vencimiento: {fecha} | "
                    f"Estado: {estado}"
                )

    if not encontrado:
        print("No hay recursos próximos a vencer.")

# DATOS DE EJEMPLO
def cargar_datos():
    registrar_recurso(
        "R01", "ChatGPT API", "Créditos de IA", 1200000
    )
    registrar_recurso(
        "R02", "Microsoft 365", "Suscripciones", 450000
    )
    registrar_recurso(
        "R03", "Azure", "Servicios en la nube", 2500000
    )
    registrar_recurso(
        "R04", "IntelliJ IDEA", "Licencias IDE", 350000
    )
    registrar_recurso(
        "R05", "Figma", "Diseño", 150000
    )
    registrar_recurso(
        "R06", "Plugins", "Herramientas complementarias", 50000
    )

    entrada("R01", 1000, 1200, "2026-12-15")
    entrada("R01", 1500, 1300, "2027-02-15")

    entrada("R02", 20, 22500, "2027-01-15")
    entrada("R03", 500, 4000, "2027-03-15")

    entrada("R04", 10, 35000, "2027-01-10")
    entrada("R05", 15, 10000, "2027-02-10")
    entrada("R06", 50, 1000, "2027-04-10")

# MENÚ PRINCIPAL
def menu():
    cargar_datos()

    while True:
        print("\n================================")
        print(" SISTEMA DE INVENTARIO DIGITAL")
        print("================================")
        print("1. Registrar entrada")
        print("2. Registrar salida PEPS")
        print("3. Registrar salida UEPS")
        print("4. Consultar inventario")
        print("5. Consultar KARDEX")
        print("6. Clasificación ABC")
        print("7. Alertas de vencimiento")
        print("8. Salir")

        opcion = input("\nSeleccione una opción: ")

        if opcion == "1":
            codigo = input("Código del recurso: ")
            cantidad = int(input("Cantidad: "))
            costo = float(input("Costo unitario: "))
            fecha = input("Vencimiento (AAAA-MM-DD): ")
            usuario = input("Usuario: ")

            entrada(codigo, cantidad, costo, fecha, usuario)

        elif opcion == "2":
            codigo = input("Código del recurso: ")
            cantidad = int(input("Cantidad de salida: "))
            usuario = input("Usuario: ")
            salida(codigo, cantidad, "PEPS", usuario)

        elif opcion == "3":
            codigo = input("Código del recurso: ")
            cantidad = int(input("Cantidad de salida: "))
            usuario = input("Usuario: ")
            salida(codigo, cantidad, "UEPS", usuario)

        elif opcion == "4":
            mostrar_inventario()

        elif opcion == "5":
            mostrar_kardex()

        elif opcion == "6":
            clasificacion_abc()

        elif opcion == "7":
            alertas_vencimiento()

        elif opcion == "8":
            print("Sistema finalizado.")
            break

        else:
            print("Opción no válida.")

if __name__ == "__main__":
    menu()
