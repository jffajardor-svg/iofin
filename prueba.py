
import networkx as nx
import matplotlib.pyplot as plt

actividades = {}
G = nx.DiGraph()

print("=" * 65)
print("       SISTEMA INTERACTIVO DE PLANIFICACIÓN PERT / CPM")
print("=" * 65)

# ==========================================================
# 1. INGRESO DE DATOS DEL PROYECTO
# ==========================================================

# El usuario define cuántas actividades tendrá el proyecto.
# De esta manera, el programa no depende de una cantidad
# fija de tareas y puede adaptarse a proyectos diferentes.

while True:
    try:
        cantidad = int(input("\n¿Cuántas actividades tiene el proyecto?: "))
        if cantidad > 0:
            break
        print("Ingrese una cantidad mayor que cero.")
    except ValueError:
        print("Debe ingresar un número entero.")

# Se solicita el nombre y duración de cada actividad.
# Los identificadores se generan automáticamente (A1, A2...).
# Estos identificadores permiten establecer las dependencias
# sin necesidad de escribir nombres largos.

for i in range(1, cantidad + 1):

    codigo = f"A{i}"

    print(f"\n--- ACTIVIDAD {codigo} ---")

    while True:
        nombre = input("Nombre de la actividad: ").strip()
        if nombre:
            break
        print("El nombre no puede estar vacío.")

    while True:
        try:
            duracion = float(input("Duración en días: "))
            if duracion > 0:
                break
            print("La duración debe ser mayor que cero.")
        except ValueError:
            print("Ingrese una duración numérica válida.")

    actividades[codigo] = {
        "nombre": nombre,
        "duracion": duracion,
        "predecesoras": []
    }

# ==========================================================
# 2. INGRESO DE DEPENDENCIAS
# ==========================================================

# Una actividad predecesora es aquella que debe terminar
# antes de que otra actividad pueda comenzar.
#
# Se permite ingresar varios identificadores separados
# por comas. Si la actividad no depende de ninguna otra,
# el usuario simplemente presiona ENTER.

print("\n" + "=" * 65)
print("             REGISTRO DE DEPENDENCIAS")
print("=" * 65)

print("\nActividades registradas:")

for codigo, datos in actividades.items():
    print(f"{codigo}: {datos['nombre']}")

for codigo in actividades:

    while True:
        entrada = input(
            f"\n¿Qué actividades preceden a {codigo}? "
            "Ingrese códigos separados por coma o ENTER si ninguna: "
        ).strip()

        if not entrada:
            predecesoras = []
        else:
            predecesoras = [
                p.strip().upper()
                for p in entrada.split(",")
            ]

        if len(predecesoras) != len(set(predecesoras)):
            print("No repita identificadores.")
            continue

        if codigo in predecesoras:
            print("Una actividad no puede depender de sí misma.")
            continue

        desconocidas = [
            p for p in predecesoras
            if p not in actividades
        ]

        if desconocidas:
            print("Identificadores inexistentes:", desconocidas)
            continue

        actividades[codigo]["predecesoras"] = predecesoras
        break

# ==========================================================
# 3. CONSTRUCCIÓN DEL GRAFO
# ==========================================================

# NetworkX permite representar el proyecto como un grafo
# dirigido. Los nodos representan actividades y las flechas
# representan las dependencias entre ellas.

for codigo, datos in actividades.items():

    G.add_node(
        codigo,
        nombre=datos["nombre"],
        duracion=datos["duracion"]
    )

    for predecesora in datos["predecesoras"]:
        G.add_edge(predecesora, codigo)

# Se comprueba que el proyecto no tenga dependencias
# circulares. Una dependencia circular impediría determinar
# un orden válido para ejecutar las actividades.

if not nx.is_directed_acyclic_graph(G):
    print("\nERROR: Se encontraron dependencias circulares.")
    print("Revise las actividades predecesoras e intente nuevamente.")
    raise SystemExit

orden = list(nx.topological_sort(G))

# ==========================================================
# 4. CÁLCULO DE TIEMPOS TEMPRANOS
# ==========================================================

# ES representa el inicio más temprano.
# EF representa la finalización más temprana.
#
# Se recorren las actividades siguiendo el orden lógico
# de sus dependencias.
#
# Cuando una actividad tiene varias predecesoras,
# se toma la mayor finalización temprana, porque
# todas deben terminar antes de comenzar la siguiente.

for nodo in orden:

    predecesoras = list(G.predecessors(nodo))

    if predecesoras:
        ES = max(G.nodes[p]["EF"] for p in predecesoras)
    else:
        ES = 0

    EF = ES + G.nodes[nodo]["duracion"]

    G.nodes[nodo]["ES"] = ES
    G.nodes[nodo]["EF"] = EF

# ==========================================================
# 5. DURACIÓN TOTAL DEL PROYECTO
# ==========================================================

# Las actividades finales son aquellas que no tienen
# actividades sucesoras.
#
# La duración total corresponde a la mayor finalización
# temprana entre todas las actividades finales.

finales = [
    nodo for nodo in G.nodes()
    if G.out_degree(nodo) == 0
]

duracion_proyecto = max(
    G.nodes[nodo]["EF"] for nodo in finales
)

# ==========================================================
# 6. CÁLCULO DE TIEMPOS TARDÍOS
# ==========================================================

# LS representa el inicio más tardío permitido.
# LF representa la finalización más tardía permitida.
#
# Se recorre el proyecto en orden inverso.
# Cuando una actividad tiene varias sucesoras,
# se utiliza el menor inicio tardío para garantizar
# que ninguna de ellas se retrase.

for nodo in reversed(orden):

    sucesoras = list(G.successors(nodo))

    if sucesoras:
        LF = min(G.nodes[s]["LS"] for s in sucesoras)
    else:
        LF = duracion_proyecto

    LS = LF - G.nodes[nodo]["duracion"]

    G.nodes[nodo]["LS"] = LS
    G.nodes[nodo]["LF"] = LF

# ==========================================================
# 7. CÁLCULO DE HOLGURAS
# ==========================================================

# La holgura indica cuántos días puede retrasarse una
# actividad sin afectar la duración total del proyecto.
#
# Fórmula:
# Holgura = LS - ES
#
# Si la holgura es cero, la actividad es crítica.

for nodo in G.nodes():

    holgura = (
        G.nodes[nodo]["LS"] -
        G.nodes[nodo]["ES"]
    )

    G.nodes[nodo]["holgura"] = round(holgura, 2)
    G.nodes[nodo]["critica"] = abs(holgura) < 0.000001

# ==========================================================
# 8. IDENTIFICACIÓN DE LA RUTA CRÍTICA
# ==========================================================

# Una actividad crítica tiene holgura cero.
# Una conexión crítica debe unir dos actividades críticas
# y cumplir que el fin temprano de la primera coincida
# con el inicio temprano de la segunda.
#
# Esto permite identificar correctamente las secuencias
# críticas incluso cuando existen varias rutas críticas.

nodos_criticos = [
    nodo for nodo in G.nodes()
    if G.nodes[nodo]["critica"]
]

aristas_criticas = [
    (u, v)
    for u, v in G.edges()
    if G.nodes[u]["critica"]
    and G.nodes[v]["critica"]
    and abs(G.nodes[u]["EF"] - G.nodes[v]["ES"]) < 0.000001
]

GC = nx.DiGraph()
GC.add_nodes_from(nodos_criticos)
GC.add_edges_from(aristas_criticas)

# Se buscan todas las secuencias críticas completas.
# Esto evita mostrar solamente una ruta cuando el proyecto
# tiene más de un camino crítico.

inicios_criticos = [
    nodo for nodo in GC.nodes()
    if GC.in_degree(nodo) == 0
    and abs(G.nodes[nodo]["ES"]) < 0.000001
]

finales_criticos = [
    nodo for nodo in GC.nodes()
    if GC.out_degree(nodo) == 0
    and abs(G.nodes[nodo]["EF"] - duracion_proyecto) < 0.000001
]

rutas_criticas = []

for inicio in inicios_criticos:
    for final in finales_criticos:
        rutas = nx.all_simple_paths(GC, inicio, final)
        rutas_criticas.extend(list(rutas))

# ==========================================================
# 9. PRESENTACIÓN DE RESULTADOS
# ==========================================================

# Se imprime una tabla con los resultados del análisis.
# Cada columna representa un indicador de programación:
# ES, EF, LS, LF y holgura.
#
# Estos valores permiten identificar qué actividades
# tienen flexibilidad y cuáles determinan el plazo final.

print("\n" + "=" * 115)
print("                 RESULTADOS DEL ANÁLISIS PERT / CPM")
print("=" * 115)

print(
    f"{'ID':<6}"
    f"{'ACTIVIDAD':<43}"
    f"{'DUR.':>8}"
    f"{'ES':>8}"
    f"{'EF':>8}"
    f"{'LS':>8}"
    f"{'LF':>8}"
    f"{'HOLG.':>9}"
    f"{'ESTADO':>15}"
)

print("-" * 115)

for nodo in orden:

    datos = G.nodes[nodo]

    estado = "CRÍTICA" if datos["critica"] else "NO CRÍTICA"

    print(
        f"{nodo:<6}"
        f"{datos['nombre'][:42]:<43}"
        f"{datos['duracion']:>8.2f}"
        f"{datos['ES']:>8.2f}"
        f"{datos['EF']:>8.2f}"
        f"{datos['LS']:>8.2f}"
        f"{datos['LF']:>8.2f}"
        f"{datos['holgura']:>9.2f}"
        f"{estado:>15}"
    )

print("-" * 115)

print(f"\nDURACIÓN TOTAL DEL PROYECTO: {duracion_proyecto:.2f} días")

print("\nRUTA(S) CRÍTICA(S):")

if rutas_criticas:
    for i, ruta in enumerate(rutas_criticas, 1):
        print(f"Ruta {i}: {' -> '.join(ruta)}")
else:
    print("No se pudo identificar una ruta crítica completa.")

print("\nACTIVIDADES CON HOLGURA:")

for nodo in orden:
    if not G.nodes[nodo]["critica"]:
        print(
            f"{nodo} - {G.nodes[nodo]['nombre']}: "
            f"{G.nodes[nodo]['holgura']:.2f} días"
        )

# ==========================================================
# 10. GENERACIÓN DEL DIAGRAMA VISUAL
# ==========================================================

# Se calcula una capa para cada actividad según su posición
# dentro de la secuencia de dependencias.
#
# Esto permite distribuir los nodos en el gráfico
# y facilitar la interpretación del proyecto.

capas = {}

for nodo in orden:

    predecesoras = list(G.predecessors(nodo))

    if predecesoras:
        capas[nodo] = max(capas[p] for p in predecesoras) + 1
    else:
        capas[nodo] = 0

nx.set_node_attributes(G, capas, "layer")

pos = nx.multipartite_layout(
    G,
    subset_key="layer",
    align="horizontal",
    scale=3
)

# Las actividades críticas se representan en rojo.
# Las actividades no críticas se representan en azul.
# Las conexiones críticas tienen líneas rojas más gruesas.

colores_nodos = [
    "tomato" if G.nodes[n]["critica"] else "lightblue"
    for n in G.nodes()
]

colores_aristas = [
    "red" if (u, v) in aristas_criticas else "gray"
    for u, v in G.edges()
]

anchos = [
    3 if (u, v) in aristas_criticas else 1.3
    for u, v in G.edges()
]

# Las etiquetas muestran el código de la actividad,
# su duración y su holgura.

etiquetas = {
    nodo: (
        f"{nodo}\n"
        f"{G.nodes[nodo]['duracion']:g} días\n"
        f"H: {G.nodes[nodo]['holgura']:g}"
    )
    for nodo in G.nodes()
}

# Se ajusta el tamaño de la imagen según el número
# de actividades para mejorar la visualización.

ancho = max(14, len(orden) * 1.2)
alto = max(8, cantidad * 0.6)

plt.figure(figsize=(ancho, alto))

nx.draw_networkx_nodes(
    G,
    pos,
    node_color=colores_nodos,
    node_size=2800,
    edgecolors="black",
    linewidths=1.5
)

nx.draw_networkx_labels(
    G,
    pos,
    labels=etiquetas,
    font_size=9,
    font_weight="bold"
)

nx.draw_networkx_edges(
    G,
    pos,
    edge_color=colores_aristas,
    width=anchos,
    arrows=True,
    arrowsize=22,
    connectionstyle="arc3,rad=0.08"
)

plt.title(
    "DIAGRAMA PERT / CPM\n"
    f"Duración total: {duracion_proyecto:g} días",
    fontsize=16,
    fontweight="bold"
)

plt.figtext(
    0.5,
    0.02,
    "ROJO: Ruta crítica | AZUL: Actividades no críticas | "
    "H: Holgura en días",
    ha="center",
    fontsize=11
)

plt.axis("off")
plt.tight_layout()

plt.savefig(
    "diagrama_pert_cpm.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("\nDiagrama guardado como: diagrama_pert_cpm.png")
