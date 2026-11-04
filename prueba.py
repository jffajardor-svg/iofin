
import networkx as nx

actividades = {
    "A": ("Levantamiento de requisitos", 3),
    "B": ("Diseño de interfaces UI/UX", 4),
    "C": ("Diseño de base de datos", 3),
    "D": ("Desarrollo del frontend", 6),
    "E": ("Desarrollo del backend", 7),
    "F": ("Integración frontend-backend", 3),
    "G": ("Integración de pagos", 4),
    "H": ("Pruebas de seguridad y funcionalidad", 3),
    "I": ("Despliegue en producción", 2)
}

dependencias = [
    ("A", "B"),
    ("A", "C"),
    ("B", "D"),
    ("C", "E"),
    ("D", "F"),
    ("E", "F"),
    ("F", "G"),
    ("G", "H"),
    ("H", "I")
]

G = nx.DiGraph()

for codigo, (nombre, duracion) in actividades.items():
    G.add_node(codigo, nombre=nombre, duracion=duracion)

G.add_edges_from(dependencias)

orden = list(nx.topological_sort(G))

inicio = {}
final = {}

for nodo in orden:
    inicio[nodo] = max(
        [final[p] for p in G.predecessors(nodo)],
        default=0
    )
    final[nodo] = inicio[nodo] + G.nodes[nodo]["duracion"]

duracion_total = max(final.values())

fin_tardio = {}
inicio_tardio = {}

for nodo in reversed(orden):
    sucesores = list(G.successors(nodo))
    fin_tardio[nodo] = min(
        [inicio_tardio[s] for s in sucesores],
        default=duracion_total
    )
    inicio_tardio[nodo] = (
        fin_tardio[nodo] - G.nodes[nodo]["duracion"]
    )

print("CRONOGRAMA DEL PROYECTO\n")

for nodo in orden:
    holgura = inicio_tardio[nodo] - inicio[nodo]
    print(
        nodo,
        actividades[nodo][0],
        "| Inicio:", inicio[nodo],
        "| Fin:", final[nodo],
        "| Holgura:", holgura
    )

criticas = [
    n for n in orden
    if inicio_tardio[n] == inicio[n]
]

print("\nRuta crítica:", " -> ".join(criticas))
print("Duración total:", duracion_total, "días")
